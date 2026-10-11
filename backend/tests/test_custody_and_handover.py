"""Phase 2 tests for Custody handovers, offline sync, hash chain, and public view."""
import uuid
from decimal import Decimal
from django.utils import timezone
import pytest
from rest_framework.test import APIClient

from apps.identity.models import AppUser
from apps.identity.services.token import TokenService
from apps.inventory.models import LotBalance
from apps.labels.models import QrBlock, QrLabel
from apps.ledger.models import TraceEvent, HashAnchor
from apps.lots.models import Lot, Product
from apps.organisations.models import Organisation, PartnerLink
from apps.custody.models import Handover
from apps.alerts.models import Alert, ScanLog
from apps.publicview.models import PublicView
from apps.ledger.services.hash_chain import verify_lot_hash_chain
from apps.ledger.services.anchor_service import run_daily_anchoring


@pytest.fixture
def api_client():
    return APIClient()


def create_user_and_org(phone, name, org_type="FARMER", verification="VERIFIED"):
    org = Organisation.objects.create(
        org_id=uuid.uuid4(),
        name=name,
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


def setup_partner_link(org_a, org_b):
    return PartnerLink.objects.create(
        org_a=org_a,
        org_b=org_b,
        status="ACCEPTED",
    )


def create_sample_lot(farmer_user, serial="TOM261010ABCD", qty=500.0):
    prod, _ = Product.objects.get_or_create(name="Tomato", variety="Hybrid Roma")
    block = QrBlock.objects.create(
        issued_to_org=farmer_user.org,
        issued_by=farmer_user,
        count=10,
    )
    lot = Lot.objects.create(
        lot_id=uuid.uuid4(),
        public_code=serial,
        product=prod,
        created_by_org=farmer_user.org,
        lot_kind="HARVEST",
        state="CREATED",
        custodian_org=farmer_user.org,
        head_seq=1,
    )
    QrLabel.objects.create(
        serial=serial,
        block=block,
        issued_to_org=farmer_user.org,
        status="BOUND",
        lot=lot,
    )

    LotBalance.objects.create(
        lot=lot,
        qty_in_kg=Decimal(str(qty)),
    )
    TraceEvent.objects.create(
        event_id=uuid.uuid4(),
        lot=lot,
        lot_seq=1,
        event_type="HARVEST_CREATE",
        event_time=timezone.now(),
        org=farmer_user.org,
        user=farmer_user,
        qty_kg=Decimal(str(qty)),
        qty_basis="MEASURED",
        payload={"label_serial": serial, "net_qty_kg": qty},
        event_hash=b"initial_harvest_hash_0000000001",
    )
    lot.head_hash = b"initial_harvest_hash_0000000001"
    lot.save(update_fields=["head_hash"])
    return lot


@pytest.mark.django_db
def test_dispatch_and_receive_happy_path(api_client):
    farmer = create_user_and_org("+919333333331", "Farmer Org")
    aggregator = create_user_and_org("+919333333332", "Aggregator Org", org_type="AGGREGATOR")
    setup_partner_link(farmer.org, aggregator.org)
    lot = create_sample_lot(farmer, serial="7K3Q9XMD4T2A", qty=500.0)

    # 1. Farmer dispatches 500 kg
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {farmer.tokens['access_token']}")
    dispatch_payload = {
        "event_id": str(uuid.uuid4()),
        "event_time": timezone.now().isoformat(),
        "to_org_id": str(aggregator.org.org_id),
        "qty_kg": 500.0,
        "device_signature": "mock_sig_farmer",
    }
    resp = api_client.post(f"/v1/lots/{lot.public_code}/dispatch", dispatch_payload, format="json")
    assert resp.status_code == 201
    handover_id = resp.data["handover_id"]
    assert resp.data["state"] == "PENDING"

    lot.refresh_from_db()
    assert lot.state == "IN_TRANSIT"
    assert lot.pending_receiver_org_id == aggregator.org.org_id

    # 2. Aggregator receives with 1-tap Matches
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {aggregator.tokens['access_token']}")
    receive_payload = {
        "event_id": str(uuid.uuid4()),
        "event_time": timezone.now().isoformat(),
        "matches": True,
        "device_signature": "mock_sig_aggregator",
    }
    resp2 = api_client.post(f"/v1/handovers/{handover_id}/receive", receive_payload, format="json")
    assert resp2.status_code == 200
    assert resp2.data["state"] == "ACCEPTED"

    lot.refresh_from_db()
    assert lot.state == "IN_CUSTODY"
    assert lot.custodian_org_id == aggregator.org.org_id
    assert lot.pending_receiver_org_id is None

    balance = LotBalance.objects.get(lot=lot)
    assert float(balance.qty_on_hand_kg) == 500.0


@pytest.mark.django_db
def test_two_receivers_race_condition(api_client):
    farmer = create_user_and_org("+919333333333", "Farmer Org 2")
    aggregator = create_user_and_org("+919333333334", "Aggregator Org 2", org_type="AGGREGATOR")
    setup_partner_link(farmer.org, aggregator.org)
    lot = create_sample_lot(farmer, serial="7K3Q9XMD4T2B", qty=500.0)

    # Dispatch
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {farmer.tokens['access_token']}")
    d_resp = api_client.post(
        f"/v1/lots/{lot.public_code}/dispatch",
        {
            "event_id": str(uuid.uuid4()),
            "event_time": timezone.now().isoformat(),
            "to_org_id": str(aggregator.org.org_id),
            "qty_kg": 500.0,
            "device_signature": "mock_sig",
        },
        format="json",
    )
    handover_id = d_resp.data["handover_id"]

    # First receive succeeds
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {aggregator.tokens['access_token']}")
    r1 = api_client.post(
        f"/v1/handovers/{handover_id}/receive",
        {
            "event_id": str(uuid.uuid4()),
            "event_time": timezone.now().isoformat(),
            "matches": True,
            "device_signature": "mock_sig_1",
        },
        format="json",
    )
    assert r1.status_code == 200

    # Second receive for same handover is rejected / conflict
    r2 = api_client.post(
        f"/v1/handovers/{handover_id}/receive",
        {
            "event_id": str(uuid.uuid4()),
            "event_time": timezone.now().isoformat(),
            "matches": True,
            "device_signature": "mock_sig_2",
        },
        format="json",
    )
    assert r2.status_code in [400, 409]


@pytest.mark.django_db
def test_tolerance_and_discrepancy(api_client):
    farmer = create_user_and_org("+919333333335", "Farmer Org 3")
    aggregator = create_user_and_org("+919333333336", "Aggregator Org 3", org_type="AGGREGATOR")
    setup_partner_link(farmer.org, aggregator.org)
    lot = create_sample_lot(farmer, serial="7K3Q9XMD4T2C", qty=500.0)

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {farmer.tokens['access_token']}")
    d_resp = api_client.post(
        f"/v1/lots/{lot.public_code}/dispatch",
        {
            "event_id": str(uuid.uuid4()),
            "event_time": timezone.now().isoformat(),
            "to_org_id": str(aggregator.org.org_id),
            "qty_kg": 500.0,
            "device_signature": "sig",
        },
        format="json",
    )
    handover_id = d_resp.data["handover_id"]

    # Aggregator enters scale weight 450 kg (diff 50 kg > 10 kg tolerance)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {aggregator.tokens['access_token']}")
    r_resp = api_client.post(
        f"/v1/handovers/{handover_id}/receive",
        {
            "event_id": str(uuid.uuid4()),
            "event_time": timezone.now().isoformat(),
            "matches": False,
            "received_qty_kg": 450.0,
            "rejected_qty_kg": 0.0,
            "device_signature": "sig",
        },
        format="json",
    )
    assert r_resp.status_code == 200
    assert r_resp.data["state"] == "ACCEPTED_WITH_DISCREPANCY"

    # Alert should be logged
    alert = Alert.objects.filter(rule="TOLERANCE_EXCEEDED", lot=lot).first()
    assert alert is not None


@pytest.mark.django_db
def test_dispute_and_resolve_flow(api_client):
    farmer = create_user_and_org("+919333333337", "Farmer Org 4")
    aggregator = create_user_and_org("+919333333338", "Aggregator Org 4", org_type="AGGREGATOR")
    setup_partner_link(farmer.org, aggregator.org)
    lot = create_sample_lot(farmer, serial="7K3Q9XMD4T2D", qty=500.0)

    # Dispatch & Receive with discrepancy
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {farmer.tokens['access_token']}")
    d_resp = api_client.post(
        f"/v1/lots/{lot.public_code}/dispatch",
        {
            "event_id": str(uuid.uuid4()),
            "event_time": timezone.now().isoformat(),
            "to_org_id": str(aggregator.org.org_id),
            "qty_kg": 500.0,
            "device_signature": "sig",
        },
        format="json",
    )
    handover_id = d_resp.data["handover_id"]

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {aggregator.tokens['access_token']}")
    api_client.post(
        f"/v1/handovers/{handover_id}/receive",
        {
            "event_id": str(uuid.uuid4()),
            "event_time": timezone.now().isoformat(),
            "matches": False,
            "received_qty_kg": 450.0,
            "device_signature": "sig",
        },
        format="json",
    )

    # Farmer disputes
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {farmer.tokens['access_token']}")
    disp_resp = api_client.post(
        f"/v1/handovers/{handover_id}/dispute",
        {
            "event_id": str(uuid.uuid4()),
            "event_time": timezone.now().isoformat(),
            "reason": "Scales at aggregator uncalibrated",
            "device_signature": "sig",
        },
        format="json",
    )
    assert disp_resp.status_code == 200
    assert disp_resp.data["state"] == "DISPUTED"

    lot.refresh_from_db()
    assert lot.state == "DISPUTED"

    # Counterparty resolves with agreed 475 kg
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {aggregator.tokens['access_token']}")
    res_resp = api_client.post(
        f"/v1/handovers/{handover_id}/resolve",
        {
            "event_id": str(uuid.uuid4()),
            "event_time": timezone.now().isoformat(),
            "agreed_qty_kg": 475.0,
            "note": "Re-weighed together",
            "device_signature": "sig",
        },
        format="json",
    )
    assert res_resp.status_code == 200
    assert res_resp.data["state"] == "ACCEPTED"

    lot.refresh_from_db()
    assert lot.state == "IN_CUSTODY"


@pytest.mark.django_db
def test_offline_sync_batch_endpoint(api_client):
    farmer = create_user_and_org("+919333333339", "Farmer Sync Org")
    aggregator = create_user_and_org("+919333333340", "Aggregator Sync Org", org_type="AGGREGATOR")
    setup_partner_link(farmer.org, aggregator.org)
    lot = create_sample_lot(farmer, serial="7K3Q9XMD4T2E", qty=300.0)

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {farmer.tokens['access_token']}")

    event1_id = str(uuid.uuid4())
    sync_batch = {
        "items": [
            {
                "path": f"/v1/lots/{lot.public_code}/dispatch",
                "method": "POST",
                "body": {
                    "event_id": event1_id,
                    "event_time": timezone.now().isoformat(),
                    "to_org_id": str(aggregator.org.org_id),
                    "qty_kg": 300.0,
                    "device_signature": "sig",
                },
            }
        ]
    }

    # 1. Process batch
    resp = api_client.post("/v1/sync/events", sync_batch, format="json")
    assert resp.status_code == 200
    assert len(resp.data["results"]) == 1
    assert resp.data["results"][0]["status"] == "ACCEPTED"
    assert resp.data["results"][0]["event_id"] == event1_id

    # 2. Idempotent re-submission of same batch
    resp2 = api_client.post("/v1/sync/events", sync_batch, format="json")
    assert resp2.status_code == 200
    assert resp2.data["results"][0]["status"] == "ACCEPTED"


@pytest.mark.django_db
def test_public_view_zero_pii_leak(api_client):
    farmer = create_user_and_org("+919876543210", "Secret Farmer Personal Name")
    lot = create_sample_lot(farmer, serial="7K3Q9XMD4T2F", qty=100.0)

    # 1. JSON Public API
    resp = api_client.get(f"/v1/public/lots/{lot.public_code}")
    assert resp.status_code == 200
    json_str = str(resp.data)

    # Verify zero PII
    assert "+919876543210" not in json_str
    assert "Secret Farmer Personal Name" not in json_str
    assert "lat" not in json_str
    assert "lon" not in json_str
    assert resp.data["disclaimer"] is not None

    # 2. Server-rendered HTML page
    html_resp = api_client.get(f"/L/{lot.public_code}")
    assert html_resp.status_code == 200
    content = html_resp.content.decode("utf-8")
    assert "+919876543210" not in content
    assert "Secret Farmer Personal Name" not in content
    assert "This record is based on information entered by supply-chain participants" in content

    # 3. Check scan was logged
    assert ScanLog.objects.filter(serial=lot.public_code).count() >= 2


@pytest.mark.django_db
def test_daily_anchor_merkle_root():
    farmer = create_user_and_org("+919999999991", "Anchor Test Org")
    lot = create_sample_lot(farmer, serial="7K3Q9XMD4T2G", qty=200.0)
    assert lot.lot_id is not None

    root_hash, verified_count, corrupted_count = run_daily_anchoring()
    assert verified_count >= 1
    assert corrupted_count == 0
    assert len(root_hash) == 32

    anchor = HashAnchor.objects.filter(anchor_date=timezone.now().date()).first()
    assert anchor is not None
    assert bytes(anchor.root_hash) == root_hash
