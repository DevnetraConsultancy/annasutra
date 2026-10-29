"""Tests for Entity Profile Deletion Request workflow (Producer & downstream business entities).
Covers:
- Pre-flight in-transit & custody checks
- OTP verification on registered mobile
- Submission and state transition to DELETION_REQUESTED
- Owner cancellation of pending deletion request
- Administrative review queue and approval/rejection under DPDP Act 2023
"""

import uuid
import pytest
from rest_framework.test import APIClient

from apps.identity.models import (
    AppUser,
    EntityDeletionRequest,
    EntityProfile,
    EntitySensitive,
    VerificationReview,
)
from apps.identity.services.token import TokenService
from apps.lots.models import Lot, Product
from apps.organisations.models import Organisation


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_setup():
    # Admin User
    admin_org = Organisation.objects.create(
        org_id=uuid.uuid4(),
        name="State Oversight Authority",
        org_type="OPERATOR",
        verification="VERIFIED",
    )
    admin_user = AppUser.objects.create(
        user_id=uuid.uuid4(),
        org=admin_org,
        phone_e164="+919999999999",
        role="OWNER",
        status="ACTIVE",
    )
    admin_token = TokenService.issue_token_pair(admin_user)["access_token"]

    # Producer User & Profile
    producer_org = Organisation.objects.create(
        org_id=uuid.uuid4(),
        name="Green Meadows Organic Farm",
        org_type="FARMER",
        verification="VERIFIED",
    )
    producer_user = AppUser.objects.create(
        user_id=uuid.uuid4(),
        org=producer_org,
        phone_e164="+919876543210",
        role="OWNER",
        status="ACTIVE",
    )
    producer_token = TokenService.issue_token_pair(producer_user)["access_token"]

    producer_profile = EntityProfile.objects.create(
        entity_id=producer_org.org_id,
        user_id=producer_user.user_id,
        role="PRODUCER",
        entity_code="PROD-MH-000101",
        first_name="Ramesh",
        last_name="Patil",
        organisation_name="Green Meadows Organic Farm",
        phone_e164="+919876543210",
        village_town="Baramati",
        district="Pune",
        state="Maharashtra",
        pincode="413102",
        photo_object_key="photos/ramesh.jpg",
        status="VERIFIED",
    )

    EntitySensitive.objects.create(
        entity=producer_profile,
        aadhaar_last4="5678",
        bank_name="State Bank of India",
        account_last4="4321",
    )

    # Product for lot creation
    product = Product.objects.create(
        product_id=uuid.uuid4(),
        name="Organic Potatoes",
        variety="Kufri Jyoti",
    )

    return {
        "admin_user": admin_user,
        "admin_token": admin_token,
        "producer_org": producer_org,
        "producer_user": producer_user,
        "producer_profile": producer_profile,
        "producer_token": producer_token,
        "product": product,
    }


@pytest.mark.django_db
def test_preflight_check_returns_clear_status(api_client, test_setup):
    """GET /v1/me/profile/delete-request returns can_request_deletion=True when no lots are in transit."""
    token = test_setup["producer_token"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    resp = api_client.get("/v1/me/profile/delete-request")
    assert resp.status_code == 200
    data = resp.data
    assert data["has_pending_request"] is False
    assert data["can_request_deletion"] is True
    assert data["active_in_transit_count"] == 0
    assert len(data["blocking_reasons"]) == 0


@pytest.mark.django_db
def test_otp_request_action(api_client, test_setup, settings):
    """POST /v1/me/profile/delete-request with action='request_otp' dispatches 2FA code."""
    settings.OTP_DEBUG = True
    token = test_setup["producer_token"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    resp = api_client.post("/v1/me/profile/delete-request", {"action": "request_otp"})
    assert resp.status_code == 202
    assert resp.data["status"] == "OTP_SENT"
    assert "debug_code" in resp.data


@pytest.mark.django_db
def test_successful_deletion_request_submission(api_client, test_setup, settings):
    """Submitting valid deletion request with OTP sets status to DELETION_REQUESTED."""
    settings.OTP_DEBUG = True
    token = test_setup["producer_token"]
    profile = test_setup["producer_profile"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    resp = api_client.post(
        "/v1/me/profile/delete-request",
        {
            "reason": "CEASING_OPERATIONS",
            "remarks": "Retiring from farming operations.",
            "otp_code": "123456",
        },
    )
    assert resp.status_code == 201
    assert resp.data["status"] == "DELETION_REQUESTED"

    profile.refresh_from_db()
    assert profile.status == "DELETION_REQUESTED"

    req_obj = EntityDeletionRequest.objects.filter(entity=profile, status="PENDING").first()
    assert req_obj is not None
    assert req_obj.reason == "CEASING_OPERATIONS"

    # VerificationReview audit log
    rev = VerificationReview.objects.filter(entity=profile, decision="DELETION_REQUESTED").first()
    assert rev is not None


@pytest.mark.django_db
def test_owner_can_cancel_pending_deletion_request(api_client, test_setup, settings):
    """Entity owner can cancel a pending deletion request to restore full VERIFIED access."""
    settings.OTP_DEBUG = True
    token = test_setup["producer_token"]
    profile = test_setup["producer_profile"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # 1. Submit request
    api_client.post(
        "/v1/me/profile/delete-request",
        {
            "reason": "LAND_TRANSFER",
            "remarks": "Land transfer underway.",
            "otp_code": "123456",
        },
    )
    profile.refresh_from_db()
    assert profile.status == "DELETION_REQUESTED"

    # 2. Cancel request
    resp = api_client.post("/v1/me/profile/delete-request/cancel")
    assert resp.status_code == 200
    assert resp.data["status"] == "VERIFIED"

    profile.refresh_from_db()
    assert profile.status == "VERIFIED"

    req_obj = EntityDeletionRequest.objects.filter(entity=profile, status="CANCELLED").first()
    assert req_obj is not None


@pytest.mark.django_db
def test_in_transit_lots_block_deletion_request(api_client, test_setup, settings):
    """If the entity has lots in HANDOVER_REQUESTED (in transit), deletion request is blocked."""
    settings.OTP_DEBUG = True
    token = test_setup["producer_token"]
    org = test_setup["producer_org"]
    product = test_setup["product"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # Create lot in transit
    Lot.objects.create(
        lot_id=uuid.uuid4(),
        public_code="LOT-IN-TRANSIT-01",
        product=product,
        created_by_org=org,
        custodian_org=org,
        pending_receiver_org=test_setup["admin_user"].org,
        lot_kind="HARVEST",
        state="IN_TRANSIT",
    )

    # 1. Pre-flight check shows blocked
    get_resp = api_client.get("/v1/me/profile/delete-request")
    assert get_resp.data["can_request_deletion"] is False
    assert get_resp.data["active_in_transit_count"] == 1
    assert len(get_resp.data["blocking_reasons"]) > 0

    # 2. POST attempt fails with validation error
    post_resp = api_client.post(
        "/v1/me/profile/delete-request",
        {
            "reason": "DUPLICATE",
            "otp_code": "123456",
        },
    )
    assert post_resp.status_code == 400
    assert "in transit" in post_resp.data["detail"]


@pytest.mark.django_db
def test_admin_deletion_approval_and_rejection_workflow(api_client, test_setup, settings):
    """Admin can list, reject, and approve entity deletion requests."""
    settings.OTP_DEBUG = True
    producer_token = test_setup["producer_token"]
    admin_token = test_setup["admin_token"]
    profile = test_setup["producer_profile"]
    producer_user = test_setup["producer_user"]

    # 1. Producer submits request
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {producer_token}")
    sub_resp = api_client.post(
        "/v1/me/profile/delete-request",
        {
            "reason": "DPDP_ERASURE",
            "remarks": "Exercising DPDP right to erasure.",
            "otp_code": "123456",
        },
    )
    assert sub_resp.status_code == 201
    req_id = sub_resp.data["request_id"]

    # 2. Admin lists deletion requests
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
    list_resp = api_client.get("/v1/admin/deletion-requests")
    assert list_resp.status_code == 200
    assert list_resp.data["count"] >= 1
    match = next(r for r in list_resp.data["results"] if r["request_id"] == req_id)
    assert match["reason"] == "DPDP_ERASURE"
    assert match["status"] == "PENDING"

    # 3. Admin rejects first with explanation
    rej_resp = api_client.post(
        f"/v1/admin/deletion-requests/{req_id}/decision",
        {"decision": "REJECTED", "remarks": "Ongoing food safety audit requires 30 days retention."},
    )
    assert rej_resp.status_code == 200
    assert rej_resp.data["status"] == "REJECTED"

    profile.refresh_from_db()
    assert profile.status == "VERIFIED"

    # 4. Producer resubmits
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {producer_token}")
    sub_resp2 = api_client.post(
        "/v1/me/profile/delete-request",
        {
            "reason": "DPDP_ERASURE",
            "remarks": "Audit completed. Resubmitting erasure request.",
            "otp_code": "123456",
        },
    )
    req_id2 = sub_resp2.data["request_id"]

    # 5. Admin approves deletion
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
    app_resp = api_client.post(
        f"/v1/admin/deletion-requests/{req_id2}/decision",
        {"decision": "APPROVED", "remarks": "Compliance checks clear. Account deactivated."},
    )
    assert app_resp.status_code == 200
    assert app_resp.data["status"] == "APPROVED"
    assert app_resp.data["entity_status"] == "DEACTIVATED"

    # Verify entity deactivated
    profile.refresh_from_db()
    assert profile.status == "DEACTIVATED"

    # Verify user disabled
    producer_user.refresh_from_db()
    assert producer_user.status == "DISABLED"

    # Verify sensitive data scrubbed (DPDP 2023 compliance)
    sens = EntitySensitive.objects.get(entity=profile)
    assert sens.bank_name == ""
    assert sens.account_last4 == ""
    assert sens.aadhaar_last4 == ""


@pytest.mark.django_db
def test_deletion_for_unregistered_or_new_user(api_client, settings):
    """GET and POST /v1/me/profile/delete-request succeed for new users without EntityProfile."""
    settings.OTP_DEBUG = True
    org = Organisation.objects.create(
        org_id=uuid.uuid4(),
        name="Temporary Farm Node",
        org_type="FARMER",
        verification="PENDING",
    )
    user = AppUser.objects.create(
        user_id=uuid.uuid4(),
        org=org,
        phone_e164="+919111222333",
        role="OWNER",
        status="ACTIVE",
    )
    token = TokenService.issue_token_pair(user)["access_token"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # 1. Preflight check returns can_request_deletion=True
    resp = api_client.get("/v1/me/profile/delete-request")
    assert resp.status_code == 200
    assert resp.data["can_request_deletion"] is True
    assert resp.data["has_pending_request"] is False

    # 2. Deletion action deactivates the user immediately
    post_resp = api_client.post(
        "/v1/me/profile/delete-request",
        {"otp_code": "123456"},
    )
    assert post_resp.status_code == 200
    assert post_resp.data["status"] == "DELETED"

    user.refresh_from_db()
    assert user.status == "DISABLED"
