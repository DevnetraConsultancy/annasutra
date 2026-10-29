"""Unit and integration tests for Identity & Auth endpoints (Phase 1 & Phase 2)."""

import uuid
import pytest
from rest_framework.test import APIClient

from apps.identity.models import AppUser, Device, EntityProfile
from apps.identity.services.entity_allocation import approve_entity_registration
from apps.identity.services.token import TokenService
from apps.organisations.models import Organisation


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def verified_user():
    org = Organisation.objects.create(
        org_id=uuid.uuid4(),
        name="Verified Farms",
        org_type="FARMER",
        verification="VERIFIED",
    )
    user = AppUser.objects.create(
        user_id=uuid.uuid4(),
        org=org,
        email="farmer.verified@gmail.com",
        phone_e164="+919876543210",
        role="OWNER",
        status="ACTIVE",
    )
    tokens = TokenService.issue_token_pair(user)
    user.tokens = tokens
    return user


@pytest.mark.django_db
def test_otp_unlinked_mobile_rejected_gmail_required_first(api_client, settings):
    """Decision 30: Mobile OTP login works ONLY if that mobile is already linked to a Gmail account."""
    settings.OTP_DEBUG = True

    req_resp = api_client.post("/v1/auth/otp/request", {"phone": "+919123456780", "language": "hi"}, format="json")
    assert req_resp.status_code == 202
    debug_code = req_resp.data.get("debug_code")

    verify_resp = api_client.post(
        "/v1/auth/otp/verify",
        {"phone": "+919123456780", "code": debug_code},
        format="json",
    )
    assert verify_resp.status_code == 400
    assert verify_resp.data["code"] == "GMAIL_REQUIRED_FIRST"


@pytest.mark.django_db
def test_otp_request_and_verify_success_for_linked_gmail_account(api_client, settings):
    """Decision 30: Once signed in via Gmail and linked to a mobile, OTP login succeeds."""
    settings.OTP_DEBUG = True

    # 0. First sign in via Google Sign-In linking mobile
    g_resp = api_client.post(
        "/api/v1/auth/google",
        {
            "email": "linked.farmer@gmail.com",
            "name": "Linked Farmer",
            "phone": "+919123456789",
            "role": "PRODUCER",
        },
        format="json",
    )
    assert g_resp.status_code == 200

    # 1. Request OTP
    req_resp = api_client.post("/v1/auth/otp/request", {"phone": "+919123456789", "language": "hi"}, format="json")
    assert req_resp.status_code == 202
    debug_code = req_resp.data.get("debug_code")
    assert debug_code is not None

    # 2. Verify OTP
    verify_resp = api_client.post(
        "/v1/auth/otp/verify",
        {
            "phone": "+919123456789",
            "code": debug_code,
            "device_public_key": "dGVzdF9wdWJsaWNfa2V5",
            "device_label": "Farmer Pixel 6",
        },
        format="json",
    )
    assert verify_resp.status_code == 200
    assert "access_token" in verify_resp.data
    assert "refresh_token" in verify_resp.data
    assert verify_resp.data["org_verification"] == "PENDING"

    user = AppUser.objects.get(phone_e164="+919123456789")
    assert user.email == "linked.farmer@gmail.com"
    assert Device.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_google_signin_without_mobile_and_system_serial_uid_and_multi_role_portal(api_client):
    """Decisions 29, 30, 31, 32, 35:
    - Google Sign-In works with Gmail alone (no mobile required).
    - Admin approval mints 26-digit Role ID using 10-digit system serial (000000xxxx) when no mobile is present.
    - Same Gmail can file separate registrations across roles (e.g. PRODUCER and AGGREGATOR).
    - Single Admin Lock restricts /api/v1/admin/* strictly to devnetraconsultancy@gmail.com.
    """
    # 1. Sign in with Gmail only (no phone)
    g_resp = api_client.post(
        "/api/v1/auth/google",
        {
            "email": "NoMobile.Kisan@Gmail.com",
            "name": "Ananya Sen",
            "role": "PRODUCER",
        },
        format="json",
    )
    assert g_resp.status_code == 200
    data = g_resp.json()
    assert data["user"]["email"] == "nomobile.kisan@gmail.com"
    assert data["user"]["phone"] is None
    assert data["is_admin"] is False
    assert not data.get("farmer_uid")
    assert len(data["registrations"]) == 6

    user_token = data["access_token"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_token}")

    # 2. Non-admin Gmail must get 403 Forbidden on Admin endpoints (Decision 32)
    admin_check = api_client.get("/api/v1/admin/reviews")
    assert admin_check.status_code == 403

    # 3. Single Admin (devnetraconsultancy@gmail.com) signs in and approves the Gmail-only Producer
    admin_client = APIClient()
    admin_auth = admin_client.post(
        "/api/v1/auth/google",
        {
            "email": "devnetraconsultancy@gmail.com",
            "name": "AnnaSutra Admin",
            "create_draft": False,
        },
        format="json",
    )
    assert admin_auth.status_code == 200
    assert admin_auth.json()["is_admin"] is True
    admin_token = admin_auth.json()["access_token"]
    admin_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")

    prod_profile = EntityProfile.objects.get(email="nomobile.kisan@gmail.com", role="PRODUCER")
    dec_resp = admin_client.post(
        f"/api/v1/admin/entities/{prod_profile.entity_id}/decision",
        {"decision": "APPROVED", "reason": "Verified Gmail-only producer"},
        format="json",
    )
    assert dec_resp.status_code == 200
    minted_uid = dec_resp.json()["farmer_uid"]
    assert len(minted_uid) == 26
    assert minted_uid.isdigit()
    # Last 10 digits must be a 000000xxxx system serial since no mobile was provided
    assert minted_uid[14:16] == "91"
    assert minted_uid[16:].startswith("000000")

    # 4. Register a second role (AGGREGATOR) under the exact same Gmail via Login Status Portal
    reg_post = api_client.post("/api/v1/me/registrations", {"role": "AGGREGATOR"}, format="json")
    assert reg_post.status_code == 201
    portal_data = reg_post.json()
    assert portal_data["already_registered"] is False
    assert portal_data["approved_roles"] == ["PRODUCER"]
    by_role = {r["role"]: r for r in portal_data["registrations"]}
    assert by_role["PRODUCER"]["status"] == "APPROVED"
    assert by_role["PRODUCER"]["role_uid"] == minted_uid
    assert by_role["AGGREGATOR"]["status"] == "DRAFT"
    assert by_role["RETAILER"]["status"] == "NOT_REGISTERED"


@pytest.mark.django_db
def test_otp_invalid_code(api_client, settings):
    settings.OTP_DEBUG = True
    api_client.post("/v1/auth/otp/request", {"phone": "+919888877777"}, format="json")

    verify_resp = api_client.post(
        "/v1/auth/otp/verify",
        {"phone": "+919888877777", "code": "000000"},
        format="json",
    )
    assert verify_resp.status_code == 400
    assert verify_resp.data["code"] == "INVALID_OTP"


@pytest.mark.django_db
def test_otp_rate_limiting(api_client, settings):
    settings.OTP_DEBUG = True
    phone = "+919999911111"

    r1 = api_client.post("/v1/auth/otp/request", {"phone": phone}, format="json")
    assert r1.status_code == 202

    r2 = api_client.post("/v1/auth/otp/request", {"phone": phone}, format="json")
    assert r2.status_code == 429
    assert r2.data["code"] == "RATE_LIMITED"


@pytest.mark.django_db
def test_token_refresh(api_client, verified_user):
    refresh_token = verified_user.tokens["refresh_token"]

    resp = api_client.post("/v1/auth/refresh", {"refresh_token": refresh_token}, format="json")
    assert resp.status_code == 200
    assert "access_token" in resp.data
    assert "refresh_token" in resp.data
    assert resp.data["org_verification"] == "VERIFIED"


@pytest.mark.django_db
def test_device_enrollment_and_revocation(api_client, verified_user):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {verified_user.tokens['access_token']}")

    enroll_resp = api_client.post(
        "/v1/auth/devices",
        {
            "public_key": "ZXMyNTZfcHViX2tleQ==",
            "key_alg": "ES256",
            "label": "Warehouse Scanner",
        },
        format="json",
    )
    assert enroll_resp.status_code == 201
    device_id = enroll_resp.data["device_id"]

    list_resp = api_client.get("/v1/auth/devices")
    assert list_resp.status_code == 200
    assert len(list_resp.data) >= 1

    del_resp = api_client.delete(f"/v1/auth/devices/{device_id}")
    assert del_resp.status_code == 204

    device = Device.objects.get(device_id=device_id)
    assert device.revoked_at is not None
