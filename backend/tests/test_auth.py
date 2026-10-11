"""Unit and integration tests for Identity & Auth endpoints."""

import uuid
import pytest
from rest_framework.test import APIClient

from apps.identity.models import AppUser, Device
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
        phone_e164="+919876543210",
        role="OWNER",
        status="ACTIVE",
    )
    tokens = TokenService.issue_token_pair(user)
    user.tokens = tokens
    return user


@pytest.mark.django_db
def test_otp_request_and_verify_success(api_client, settings):
    settings.OTP_DEBUG = True

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

    # Verify device enrolled
    user = AppUser.objects.get(phone_e164="+919123456789")
    assert Device.objects.filter(user=user).exists()


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

    # First request succeeds
    r1 = api_client.post("/v1/auth/otp/request", {"phone": phone}, format="json")
    assert r1.status_code == 202

    # Second immediate request should hit cooldown rate limit
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

    # 1. Enroll device
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

    # 2. List devices
    list_resp = api_client.get("/v1/auth/devices")
    assert list_resp.status_code == 200
    assert len(list_resp.data) >= 1

    # 3. Revoke device
    del_resp = api_client.delete(f"/v1/auth/devices/{device_id}")
    assert del_resp.status_code == 204

    # Verify device has revoked_at set
    device = Device.objects.get(device_id=device_id)
    assert device.revoked_at is not None
