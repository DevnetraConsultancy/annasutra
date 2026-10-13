"""Tests for Lot creation, label binding, idempotency, and cross-org access control."""

import uuid
from django.utils import timezone
import pytest
from rest_framework.test import APIClient

from apps.identity.models import AppUser
from apps.identity.services.token import TokenService
from apps.inventory.models import LotBalance
from apps.labels.models import QrLabel
from apps.ledger.models import TraceEvent
from apps.lots.models import Lot
from apps.organisations.models import Organisation


@pytest.fixture
def api_client():
    return APIClient()


def create_user_and_org(phone, name, verification="VERIFIED"):
    org = Organisation.objects.create(
        org_id=uuid.uuid4(),
        name=name,
        org_type="FARMER",
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
def test_unverified_org_cannot_create_lot(api_client):
    user = create_user_and_org("+919111111111", "Unverified Farm", verification="PENDING")
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {user.tokens['access_token']}")

    payload = {
        "event_id": str(uuid.uuid4()),
        "label_serial": "TESTSER12345",
        "product": {"name": "Tomato", "variety": "Roma"},
        "net_qty_kg": 250.0,
        "event_time": timezone.now().isoformat(),
    }
    resp = api_client.post("/v1/lots", payload, format="json")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_verified_org_creates_lot_successfully(api_client):
    user = create_user_and_org("+919222222222", "Green Valley Farms", verification="VERIFIED")
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {user.tokens['access_token']}")

    # 1. Allocate label block
    block_resp = api_client.post("/v1/labels/blocks", {"count": 5}, format="json")
    assert block_resp.status_code == 201
    serial = block_resp.data["serials"][0]

    # 2. Create lot
    event_id = str(uuid.uuid4())
    payload = {
        "event_id": event_id,
        "label_serial": serial,
        "product": {"name": "Organic Potato", "variety": "Kufri Jyoti"},
        "net_qty_kg": 500.0,
        "harvest_date": "2026-10-12",
        "event_time": timezone.now().isoformat(),
    }
    create_resp = api_client.post("/v1/lots", payload, format="json")
    assert create_resp.status_code == 201
    assert create_resp.data["public_code"] == serial
    assert create_resp.data["on_hand_kg"] == 500.0
    assert create_resp.data["state"] == "CREATED"

    # Verify DB records
    lot = Lot.objects.get(public_code=serial)
    assert lot.custodian_org_id == user.org.org_id
    assert QrLabel.objects.get(serial=serial).status == "BOUND"
    assert TraceEvent.objects.filter(event_id=event_id, event_type="HARVEST_CREATE").exists()
    assert LotBalance.objects.get(lot=lot).qty_on_hand_kg == 500.0


@pytest.mark.django_db
def test_lot_create_idempotent(api_client):
    user = create_user_and_org("+919333333333", "Idempotent Farms", verification="VERIFIED")
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {user.tokens['access_token']}")

    event_id = str(uuid.uuid4())
    serial = "IDEMP1234567"
    payload = {
        "event_id": event_id,
        "label_serial": serial,
        "product": {"name": "Wheat", "variety": "Sharbati"},
        "net_qty_kg": 1000.0,
        "event_time": timezone.now().isoformat(),
    }

    # First call creates
    r1 = api_client.post("/v1/lots", payload, format="json")
    assert r1.status_code == 201

    # Second call with same event_id returns existing without error
    r2 = api_client.post("/v1/lots", payload, format="json")
    assert r2.status_code == 200
    assert r2.data["lot_id"] == r1.data["lot_id"]
    assert r2.data["public_code"] == serial


@pytest.mark.django_db
def test_serial_already_used_conflict(api_client):
    user = create_user_and_org("+919444444444", "Double Use Farms", verification="VERIFIED")
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {user.tokens['access_token']}")

    serial = "REUSED123456"
    # Create first lot with this serial
    api_client.post(
        "/v1/lots",
        {
            "event_id": str(uuid.uuid4()),
            "label_serial": serial,
            "product": {"name": "Mustard", "variety": "Pusa"},
            "net_qty_kg": 100.0,
            "event_time": timezone.now().isoformat(),
        },
        format="json",
    )

    # Attempt to use same serial for another new lot
    r2 = api_client.post(
        "/v1/lots",
        {
            "event_id": str(uuid.uuid4()),
            "label_serial": serial,
            "product": {"name": "Corn", "variety": "Sweet"},
            "net_qty_kg": 200.0,
            "event_time": timezone.now().isoformat(),
        },
        format="json",
    )
    assert r2.status_code == 409
    assert r2.data["code"] == "LABEL_ALREADY_USED"


@pytest.mark.django_db
def test_cross_org_access_denied(api_client):
    user_a = create_user_and_org("+919555555551", "Org Alpha", verification="VERIFIED")
    user_b = create_user_and_org("+919555555552", "Org Beta", verification="VERIFIED")

    # User A creates a lot
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_a.tokens['access_token']}")
    serial = "ALPHA9876543"
    api_client.post(
        "/v1/lots",
        {
            "event_id": str(uuid.uuid4()),
            "label_serial": serial,
            "product": {"name": "Rice", "variety": "Basmati"},
            "net_qty_kg": 300.0,
            "event_time": timezone.now().isoformat(),
        },
        format="json",
    )

    # User B attempts to access User A's lot
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_b.tokens['access_token']}")
    get_resp = api_client.get(f"/v1/lots/{serial}")
    assert get_resp.status_code == 403
    assert get_resp.data["code"] == "CROSS_ORG_FORBIDDEN"
