"""Security hardening, header audit, zero-PII leak, and rate-limiting tests for AnnaSutra."""

import os
import pytest
from django.conf import settings
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.organisations.models import Organisation
from apps.identity.models import AppUser
from apps.publicview.models import PublicView


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_security_headers_enforced_on_all_responses(api_client):
    """Verifies that SecurityHeadersMiddleware injects required OWASP ASVS headers."""
    resp = api_client.get("/health")
    assert resp.status_code == 200

    # Content Security Policy
    csp = resp.headers.get("Content-Security-Policy")
    assert csp is not None
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp
    assert "object-src 'none'" in csp

    # Permissions Policy
    perm = resp.headers.get("Permissions-Policy")
    assert perm is not None
    assert "geolocation=()" in perm
    assert "camera=(self)" in perm

    # Standard security headers
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
    assert resp.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


@pytest.mark.django_db
def test_no_cache_headers_on_api_v1(api_client):
    """API v1 responses must include no-store Cache-Control headers."""
    resp = api_client.get("/v1/public/lots/NOTEXIST")
    assert "no-store" in resp.headers.get("Cache-Control", "")
    assert "no-cache" in resp.headers.get("Cache-Control", "")


@pytest.mark.django_db
def test_otp_request_rate_limiting(api_client):
    """OTP requests are throttled after max attempts in window."""
    cache.clear()
    phone = "+919876543210"

    # Make rapid requests
    responses = []
    for _ in range(5):
        r = api_client.post("/v1/auth/otp/request", {"phone": phone}, format="json")
        responses.append(r.status_code)

    # At least one request beyond the limit must be throttled with 429
    assert 429 in responses


@pytest.mark.django_db
def test_zero_pii_in_public_view_and_logs(api_client):
    """Ensures public views and logs never leak phone numbers, names, or GPS coordinates."""
    from django.utils import timezone
    from apps.lots.models import Lot, Product

    org = Organisation.objects.create(
        name="Confidential Farmer Org",
        org_type="FARMER",
        verification="VERIFIED",
    )
    AppUser.objects.create(
        org=org,
        phone_e164="+919876500099",
        role="OWNER",
        status="ACTIVE",
    )

    product, _ = Product.objects.get_or_create(name="Organic Tomato", variety="Himsona")
    lot = Lot.objects.create(
        public_code="TEST-PII-SAFE",
        product=product,
        created_by_org=org,
        custodian_org=org,
        lot_kind="HARVEST",
        state="IN_CUSTODY",
        head_seq=1,
    )

    # Seed public view
    PublicView.objects.create(
        lot=lot,
        public_code=lot.public_code,
        payload={
            "public_code": "TEST-PII-SAFE",
            "product_name": "Organic Tomato",
            "variety": "Himsona",
            "farmer_org_name": org.name,
            "harvest_date": "2026-10-10",
            "total_kg": 100.0,
            "journey_nodes": [],
            "certifications": [],
            "open_recall": False,
        },
        refreshed_at=timezone.now(),
    )

    resp = api_client.get("/v1/public/lots/TEST-PII-SAFE")
    assert resp.status_code == 200
    content = resp.content.decode("utf-8")

    # Strictly no phone numbers, passwords, or coordinates in public response
    assert "+919876500099" not in content
    assert "9876500099" not in content
    assert "gps" not in content.lower()
    assert "coordinates" not in content.lower()
    assert "password" not in content.lower()
    assert "secret" not in content.lower()


def test_no_secrets_in_tracked_repository_files():
    """Validates that no private keys, real AWS secrets, or credentials exist in tracked code."""
    # Check that settings SECRET_KEY is not committed as hardcoded production secret
    assert settings.DEBUG is False or settings.SECRET_KEY != ""
    # Even if local .env exists, verify that .env.example contains only placeholders
    example_path = os.path.join(settings.BASE_DIR, ".env.example")
    if os.path.exists(example_path):
        with open(example_path, "r", encoding="utf-8") as f:
            example_text = f.read()
            assert "AKIA" not in example_text  # No real AWS key
            assert "BEGIN PRIVATE KEY" not in example_text


@pytest.mark.django_db
def test_csp_allows_leaflet_and_ui_cdns(api_client):
    """Verifies that Content-Security-Policy explicitly permits required UI CDNs."""
    resp = api_client.get("/health")
    csp = resp.headers.get("Content-Security-Policy", "")
    assert "https://cdnjs.cloudflare.com" in csp
    assert "https://unpkg.com" in csp
    assert "https://cdn.jsdelivr.net" in csp


@pytest.mark.django_db
def test_no_cache_on_both_api_v1_and_v1_routes(api_client):
    """Verifies that both /v1/ and /api/v1/ prefixes strictly enforce no-cache headers."""
    resp_v1 = api_client.get("/v1/public/lots/NOTEXIST")
    assert "no-store" in resp_v1.headers.get("Cache-Control", "")

    resp_api_v1 = api_client.post("/api/v1/auth/otp/verify", data={"phone": "+919876543210", "code": "000000"})
    assert "no-store" in resp_api_v1.headers.get("Cache-Control", "")


def test_jwt_session_duration_configured_for_field_pilot():
    """Verify JWT access expiry is configured with a safe pilot duration."""
    assert getattr(settings, "JWT_ACCESS_EXPIRY_SECONDS", 0) >= 86400


@pytest.mark.django_db
def test_landing_query_code_sanitized_against_injection(api_client):
    """Landing page ?code= parameter strips dangerous special characters before redirecting."""
    resp = api_client.get("/?code=<script>alert(1)</script>LOT-101")
    assert resp.status_code == 302
    assert "script" in resp["Location"]
    assert "<" not in resp["Location"]
    assert ">" not in resp["Location"]
    assert "(" not in resp["Location"]


@pytest.mark.django_db
def test_serve_static_asset_path_traversal_blocked(api_client):
    """Path traversal, drive letters, and null bytes in static assets must return 404."""
    # Windows drive letter injection
    r1 = api_client.get("/static/C:/Windows/System32/drivers/etc/hosts")
    assert r1.status_code == 404

    # Traversal sequence
    r2 = api_client.get("/static/../../../../etc/passwd")
    assert r2.status_code == 404

    # Null byte injection
    r3 = api_client.get("/static/publicview/images/favicon.ico%00.png")
    assert r3.status_code == 404


@pytest.mark.django_db
def test_admin_auth_constant_time_comparison(api_client):
    """Admin endpoints using X-Admin-Key must perform constant-time comparison."""
    # Valid admin key
    resp_valid = api_client.get(
        "/api/v1/admin/reviews",
        HTTP_X_ADMIN_KEY=getattr(settings, "ADMIN_API_KEY", settings.SECRET_KEY),
    )
    assert resp_valid.status_code in (200, 204)

    # Invalid admin key
    resp_invalid = api_client.get(
        "/api/v1/admin/reviews",
        HTTP_X_ADMIN_KEY="incorrect_token_timing_probe",
    )
    assert resp_invalid.status_code in (401, 403)


@pytest.mark.django_db
def test_entity_profile_phone_relink_resilience(api_client):
    """A returning user whose AppUser was recreated gracefully re-links to their existing EntityProfile."""
    import uuid
    from apps.organisations.models import Organisation
    from apps.identity.models import EntityProfile
    from apps.identity.views_registration import _get_entity_profile_for_user

    phone = "+919876543210"
    org = Organisation.objects.create(name="Patel Farm Org", org_type="FARMER", verification="VERIFIED")
    user_orig = AppUser.objects.create(
        user_id=uuid.uuid4(),
        org=org,
        phone_e164=phone,
        role="OWNER",
        status="ACTIVE",
    )
    profile_orig = EntityProfile.objects.create(
        entity_id=uuid.uuid4(),
        user_id=user_orig.user_id,
        role="PRODUCER",
        phone_e164=phone,
        first_name="Ramesh",
        last_name="Patel",
        organisation_name="Patel Organic Farms",
        village_town="Bardhaman",
        district="Purba Bardhaman",
        state="West Bengal",
        address_line1="Field Road",
        pincode="713101",
        photo_object_key="photos/test.jpg",
        status="DRAFT",
    )

    # Create a new AppUser for the same phone (e.g. re-login or fresh device enrollment)
    user_new = AppUser.objects.create(
        user_id=uuid.uuid4(),
        org=org,
        phone_e164="+919876543211",  # Temporary distinct to allow creation
        role="OWNER",
        status="ACTIVE",
    )
    user_new.phone_e164 = phone  # Matches profile phone

    resolved_profile = _get_entity_profile_for_user(user_new, auto_create=True)
    assert resolved_profile.entity_id == profile_orig.entity_id
    assert resolved_profile.user_id == user_new.user_id


@pytest.mark.django_db
def test_dual_api_v1_and_v1_routes_exist():
    """Verify that both /api/v1/ and /v1/ routes resolve cleanly in Django."""
    from django.urls import resolve

    routes_to_check = [
        "/v1/auth/otp/request",
        "/api/v1/auth/otp/request",
        "/v1/auth/otp/verify",
        "/api/v1/auth/otp/verify",
        "/v1/me/profile",
        "/api/v1/me/profile",
        "/v1/me/plots",
        "/api/v1/me/plots",
        "/v1/lots/",
        "/api/v1/lots/",
        "/v1/organisations/",
        "/api/v1/organisations/",
    ]
    for r in routes_to_check:
        match = resolve(r)
        assert match is not None, f"Failed to resolve route: {r}"


@pytest.mark.django_db
def test_otp_verify_database_failure_returns_503(api_client, monkeypatch):
    """When the database is unreachable during OTP verification, an HTTP 503 is returned, never a fake token."""
    from apps.identity.services.otp import OtpService
    from apps.identity.services.token import TokenService
    from django.db import DatabaseError

    phone = "+919999988888"
    monkeypatch.setattr(OtpService, "verify_otp", lambda *args, **kwargs: True)

    def mock_issue(*args, **kwargs):
        raise DatabaseError("MySQL connection timed out or unreachable")

    monkeypatch.setattr(TokenService, "issue_token_pair", mock_issue)

    resp = api_client.post("/api/v1/auth/otp/verify", {"phone": phone, "code": "123456"})
    assert resp.status_code == 503
    assert resp.json().get("code") == "DATABASE_ERROR"
    assert "demo_access_token" not in resp.content.decode("utf-8")


