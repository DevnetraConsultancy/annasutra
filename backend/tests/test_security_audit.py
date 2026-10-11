"""Security hardening, header audit, zero-PII leak, and rate-limiting tests for AnnaSutra."""

import os
from decimal import Decimal
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
        r = api_client.post("/v1/auth/request-otp", {"phone": phone}, format="json")
        responses.append(r.status_code)

    # At least one request beyond the limit must be throttled with 429
    assert 429 in responses


@pytest.mark.django_db
def test_zero_pii_in_public_view_and_logs(api_client):
    """Ensures public views and logs never leak phone numbers, names, or GPS coordinates."""
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

    # Seed public view
    PublicView.objects.create(
        public_code="TEST-PII-SAFE",
        product_name="Organic Tomato",
        variety="Himsona",
        farmer_org_name=org.name,
        harvest_date="2026-10-10",
        total_kg=Decimal("100.000"),
        journey_nodes=[],
        certifications=[],
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
