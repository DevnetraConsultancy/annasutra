"""Tests for Organisation registration and bilateral Partner links."""

import uuid
import pytest
from rest_framework.test import APIClient

from apps.identity.models import AppUser, ConsentRecord
from apps.identity.services.token import TokenService
from apps.organisations.models import Facility, Organisation, PartnerLink


@pytest.fixture
def api_client():
    return APIClient()


def create_user_with_org(phone, org_name, org_type="FARMER", verification="VERIFIED"):
    org = Organisation.objects.create(
        org_id=uuid.uuid4(),
        name=org_name,
        org_type=org_type,
        verification=verification,
    )
    user = AppUser.objects.create(
        user_id=uuid.uuid4(),
        org=org,
        phone_e164=phone,
        role="OWNER",
        status="ACTIVE",
    )
    tokens = TokenService.issue_token_pair(user)
    user.tokens = tokens
    return user


@pytest.mark.django_db
def test_organisation_registration(api_client):
    user = create_user_with_org("+919000000001", "Pending Org", verification="PENDING")
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {user.tokens['access_token']}")

    payload = {
        "name": "Sundarban Honey Co-operative",
        "org_type": "FARMER",
        "fssai_no": "10020030040050",
        "consent_notice_version": "1.0",
        "consent_language": "bn",
    }
    resp = api_client.post("/v1/organisations", payload, format="json")
    assert resp.status_code == 201
    assert resp.data["name"] == "Sundarban Honey Co-operative"
    assert resp.data["org_type"] == "FARMER"
    assert resp.data["verification"] == "PENDING"

    # Verify facility and consent created
    assert Facility.objects.filter(org_id=resp.data["org_id"]).exists()
    assert ConsentRecord.objects.filter(user=user, notice_version="1.0").exists()


@pytest.mark.django_db
def test_partner_invitation_and_acceptance(api_client):
    user_a = create_user_with_org("+919000000002", "Farmer Ram", org_type="FARMER")
    user_b = create_user_with_org("+919000000003", "Kolkata Aggregator", org_type="AGGREGATOR")

    # 1. User A invites User B
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_a.tokens['access_token']}")
    invite_resp = api_client.post(
        "/v1/partners/invitations",
        {"to_org_id": str(user_b.org.org_id)},
        format="json",
    )
    assert invite_resp.status_code == 201
    assert invite_resp.data["status"] == "INVITED"

    # 2. User B checks partner list and sees INVITED
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_b.tokens['access_token']}")
    list_resp = api_client.get("/v1/partners")
    assert list_resp.status_code == 200
    partners = list_resp.data
    assert len(partners) == 1
    assert partners[0]["status"] == "INVITED"

    # 3. User B accepts invitation
    accept_resp = api_client.post(
        f"/v1/partners/invitations/{user_a.org.org_id}/accept",
        format="json",
    )
    assert accept_resp.status_code == 200
    assert accept_resp.data["status"] == "ACCEPTED"

    # 4. Verify link status in database
    link = PartnerLink.objects.first()
    assert link.status == "ACCEPTED"


@pytest.mark.django_db
def test_cannot_invite_own_organisation(api_client):
    user = create_user_with_org("+919000000004", "Self Farmer")
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {user.tokens['access_token']}")

    resp = api_client.post(
        "/v1/partners/invitations",
        {"to_org_id": str(user.org.org_id)},
        format="json",
    )
    assert resp.status_code == 400
    assert resp.data["code"] == "CANNOT_INVITE_SELF"
