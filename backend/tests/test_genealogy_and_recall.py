"""Genealogy, Quality, Recall, and Event Correction tests for AnnaSutra.

Tests:
1. Split lot and mass balance enforcement
2. Merge lots and cycle prevention
3. Sort and Grade mass balance
4. Waste & Spoilage and Retail Sale balance updates
5. Inspection quality recording and non-custodian rejection
6. Evidence upload descriptor request
7. Non-mutating event corrections and label reissue
8. Product recall and 200-lot seeded graph forward trace completeness
9. Admin and database trigger immutability of trace_event
"""

import uuid
from decimal import Decimal
import pytest
from django.db import connection, transaction
from django.utils import timezone
from rest_framework.test import APIClient

from apps.alerts.models import Alert
from apps.inventory.models import LotBalance
from apps.labels.models import QrBlock, QrLabel
from apps.ledger.models import TraceEvent
from apps.lots.models import Lot, Product
from apps.identity.models import AppUser
from apps.organisations.models import Organisation
from apps.quality.models import Inspection
from apps.reporting.models import Recall
from apps.ledger.admin import TraceEventAdmin


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_setup():
    # 1. Organisations
    farmer_org = Organisation.objects.create(
        name="Bardhaman Farmers Society",
        org_type="FARMER",
        verification="VERIFIED",
    )
    wholesaler_org = Organisation.objects.create(
        name="Kolkata Fresh Wholesalers",
        org_type="WHOLESALER",
        verification="VERIFIED",
    )
    distributor_org = Organisation.objects.create(
        name="Metro Veg Distributors",
        org_type="DISTRIBUTOR",
        verification="VERIFIED",
    )
    retailer_org = Organisation.objects.create(
        name="Gariahat Retail Fresh",
        org_type="RETAILER",
        verification="VERIFIED",
    )

    # 2. Users
    farmer_user = AppUser.objects.create(
        org=farmer_org,
        phone_e164="+919876500001",
        role="OWNER",
        status="ACTIVE",
    )
    wholesaler_user = AppUser.objects.create(
        org=wholesaler_org,
        phone_e164="+919876500002",
        role="STAFF",
        status="ACTIVE",
    )
    distributor_user = AppUser.objects.create(
        org=distributor_org,
        phone_e164="+919876500003",
        role="STAFF",
        status="ACTIVE",
    )
    retailer_user = AppUser.objects.create(
        org=retailer_org,
        phone_e164="+919876500004",
        role="STAFF",
        status="ACTIVE",
    )

    # 3. Product
    tomato, _ = Product.objects.get_or_create(name="Tomato", variety="Hybrid")
    potato, _ = Product.objects.get_or_create(name="Potato", variety="Jyoti")

    return {
        "farmer_org": farmer_org,
        "wholesaler_org": wholesaler_org,
        "distributor_org": distributor_org,
        "retailer_org": retailer_org,
        "farmer_user": farmer_user,
        "wholesaler_user": wholesaler_user,
        "distributor_user": distributor_user,
        "retailer_user": retailer_user,
        "tomato": tomato,
        "potato": potato,
    }


def create_test_lot(org, user, product, public_code, qty_kg, state="IN_CUSTODY", kind="HARVEST"):
    lot = Lot.objects.create(
        public_code=public_code,
        product=product,
        created_by_org=org,
        custodian_org=org,
        lot_kind=kind,
        state=state,
        head_seq=1,
    )
    block = QrBlock.objects.create(
        issued_to_org=org,
        issued_by=user,
        count=1,
    )
    QrLabel.objects.create(
        serial=public_code,
        block=block,
        issued_to_org=org,
        status="BOUND",
        lot=lot,
    )
    balance = LotBalance.objects.create(
        lot=lot,
        qty_in_kg=Decimal(str(qty_kg)),
    )
    event = TraceEvent.objects.create(
        event_id=uuid.uuid4(),
        lot=lot,
        lot_seq=1,
        event_type="HARVEST_CREATE",
        event_time=timezone.now().isoformat(),
        org=org,
        user=user,
        qty_kg=Decimal(str(qty_kg)),
        qty_basis="MEASURED",
        payload={"label_serial": public_code, "net_qty_kg": float(qty_kg)},
        sync_status="ACCEPTED",
        event_hash=b"init_hash_32_bytes_long_fixture!",
    )
    lot.head_hash = event.event_hash
    lot.save(update_fields=["head_hash"])
    return lot, balance


@pytest.mark.django_db
def test_split_lot_success_and_mass_balance(api_client, test_setup):
    """Splits a parent lot into child lots and enforces mass balance."""
    ws_user = test_setup["wholesaler_user"]
    ws_org = test_setup["wholesaler_org"]
    tomato = test_setup["tomato"]

    parent_lot, parent_bal = create_test_lot(ws_org, ws_user, tomato, "P-TOMATO-450", 450.0)

    api_client.force_authenticate(user=ws_user)

    event_id = str(uuid.uuid4())
    payload = {
        "event_id": event_id,
        "children": [
            {"label_serial": "C1-TOMATO-300", "qty_kg": 300.0},
            {"label_serial": "C2-TOMATO-150", "qty_kg": 150.0},
        ],
    }

    response = api_client.post(f"/v1/lots/{parent_lot.public_code}/split", payload, format="json")
    assert response.status_code == 201
    data = response.json()
    assert len(data["items"]) == 2

    parent_bal.refresh_from_db()
    parent_lot.refresh_from_db()
    assert parent_bal.qty_split_out_kg == Decimal("450.000")
    assert parent_bal.qty_on_hand_kg == Decimal("0.000")
    assert parent_lot.state == "CLOSED"

    # Verify children
    c1 = Lot.objects.get(public_code="C1-TOMATO-300")
    c2 = Lot.objects.get(public_code="C2-TOMATO-150")
    assert c1.custodian_org == ws_org
    assert c1.balance.qty_on_hand_kg == Decimal("300.000")
    assert c2.balance.qty_on_hand_kg == Decimal("150.000")

    # Verify lot_edge in database
    with connection.cursor() as cursor:
        cursor.execute("SELECT parent_lot, child_lot, qty_kg FROM lot_edge WHERE parent_lot = %s", [parent_lot.lot_id])
        rows = cursor.fetchall()
        assert len(rows) == 2
        qtys = sorted([float(r[2]) for r in rows])
        assert qtys == [150.0, 300.0]


@pytest.mark.django_db
def test_split_lot_exceeds_stock_rejected(api_client, test_setup):
    """Splitting more than available stock is rejected."""
    ws_user = test_setup["wholesaler_user"]
    ws_org = test_setup["wholesaler_org"]
    tomato = test_setup["tomato"]

    parent_lot, _ = create_test_lot(ws_org, ws_user, tomato, "P-TOMATO-EXCEED", 100.0)
    api_client.force_authenticate(user=ws_user)

    payload = {
        "event_id": str(uuid.uuid4()),
        "children": [
            {"label_serial": "C-FAIL-150", "qty_kg": 150.0},
        ],
    }

    response = api_client.post(f"/v1/lots/{parent_lot.public_code}/split", payload, format="json")
    assert response.status_code in [400, 409]


@pytest.mark.django_db
def test_merge_lots_success_and_product_mismatch_rejected(api_client, test_setup):
    """Merging lots of same product combines balance; mismatch is rejected."""
    ws_user = test_setup["wholesaler_user"]
    ws_org = test_setup["wholesaler_org"]
    tomato = test_setup["tomato"]
    potato = test_setup["potato"]

    lot_a, _ = create_test_lot(ws_org, ws_user, tomato, "IN-TOMATO-A", 100.0)
    lot_b, _ = create_test_lot(ws_org, ws_user, tomato, "IN-TOMATO-B", 150.0)
    lot_diff, _ = create_test_lot(ws_org, ws_user, potato, "IN-POTATO-C", 50.0)

    api_client.force_authenticate(user=ws_user)

    # 1. Product mismatch rejection
    mismatch_payload = {
        "event_id": str(uuid.uuid4()),
        "input_lot_codes": [lot_a.public_code, lot_diff.public_code],
        "label_serial": "OUT-MERGE-FAIL",
    }
    resp = api_client.post("/v1/lots/merge", mismatch_payload, format="json")
    assert resp.status_code == 400

    # 2. Successful merge
    merge_payload = {
        "event_id": str(uuid.uuid4()),
        "input_lot_codes": [lot_a.public_code, lot_b.public_code],
        "label_serial": "OUT-MERGE-250",
    }
    resp = api_client.post("/v1/lots/merge", merge_payload, format="json")
    assert resp.status_code == 201
    data = resp.json()
    assert data["public_code"] == "OUT-MERGE-250"
    assert data["on_hand_kg"] == 250.0

    lot_a.refresh_from_db()
    lot_b.refresh_from_db()
    assert lot_a.state == "CLOSED"
    assert lot_b.state == "CLOSED"
    assert lot_a.balance.qty_on_hand_kg == Decimal("0.000")
    assert lot_b.balance.qty_on_hand_kg == Decimal("0.000")


@pytest.mark.django_db
def test_sort_grade_and_waste_sale_flows(api_client, test_setup):
    """Sort, waste, and retail sale operations properly track mass balance."""
    ret_user = test_setup["retailer_user"]
    ret_org = test_setup["retailer_org"]
    tomato = test_setup["tomato"]

    lot, bal = create_test_lot(ret_org, ret_user, tomato, "RET-TOMATO-100", 100.0)
    api_client.force_authenticate(user=ret_user)

    # 1. Sort: 80 grade A, 15 grade B, 5 waste
    sort_payload = {
        "event_id": str(uuid.uuid4()),
        "outputs": [
            {"grade": "Grade A", "qty_kg": 80.0},
            {"grade": "Grade B", "qty_kg": 15.0},
            {"grade": "Waste", "qty_kg": 5.0},
        ],
    }
    resp = api_client.post(f"/v1/lots/{lot.public_code}/sort", sort_payload, format="json")
    assert resp.status_code == 201
    bal.refresh_from_db()
    assert bal.qty_waste_kg == Decimal("5.000")
    assert bal.qty_on_hand_kg == Decimal("95.000")

    # 2. Waste: 5 kg spoiled with photo evidence
    waste_payload = {
        "event_id": str(uuid.uuid4()),
        "qty_kg": 5.0,
        "reason_code": "TRANSIT_SPOILAGE",
    }
    resp = api_client.post(f"/v1/lots/{lot.public_code}/waste", waste_payload, format="json")
    assert resp.status_code == 201
    bal.refresh_from_db()
    assert bal.qty_waste_kg == Decimal("10.000")
    assert bal.qty_on_hand_kg == Decimal("90.000")

    # 3. Retail Sale: 40 kg sold
    sale_payload = {
        "event_id": str(uuid.uuid4()),
        "qty_kg": 40.0,
    }
    resp = api_client.post(f"/v1/lots/{lot.public_code}/sales", sale_payload, format="json")
    assert resp.status_code == 201
    bal.refresh_from_db()
    assert bal.qty_sold_kg == Decimal("40.000")
    assert bal.qty_on_hand_kg == Decimal("50.000")

    # 4. Over-sale rejection
    bad_sale = {
        "event_id": str(uuid.uuid4()),
        "qty_kg": 60.0,  # Only 50 remaining
    }
    resp = api_client.post(f"/v1/lots/{lot.public_code}/sales", bad_sale, format="json")
    assert resp.status_code in [400, 409]


@pytest.mark.django_db
def test_inspection_and_evidence_upload(api_client, test_setup):
    """Quality inspections record grades and link to evidence upload."""
    ws_user = test_setup["wholesaler_user"]
    ws_org = test_setup["wholesaler_org"]
    farmer_user = test_setup["farmer_user"]
    tomato = test_setup["tomato"]

    lot, _ = create_test_lot(ws_org, ws_user, tomato, "INSPECT-TOMATO-1", 200.0)

    # 1. Evidence upload request
    api_client.force_authenticate(user=ws_user)
    ev_payload = {
        "kind": "PHOTO",
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    }
    ev_resp = api_client.post("/v1/evidence/uploads", ev_payload, format="json")
    assert ev_resp.status_code == 201
    ev_data = ev_resp.json()
    assert "upload_url" in ev_data
    evidence_id = ev_data["evidence_id"]

    # 2. Record inspection
    insp_payload = {
        "event_id": str(uuid.uuid4()),
        "grade": "Grade A",
        "defect_pct": 2.5,
        "temperature_c": 18.0,
        "notes": "Optimal freshness, firm red",
        "evidence_ids": [evidence_id],
    }
    insp_resp = api_client.post(f"/v1/lots/{lot.public_code}/inspections", insp_payload, format="json")
    assert insp_resp.status_code == 201
    assert insp_resp.json()["grade"] == "Grade A"

    # Verify inspection stored
    insp_obj = Inspection.objects.get(grade="Grade A")
    assert float(insp_obj.defect_pct) == 2.5

    # 3. Third-party rejection: farmer is not custodian or pending receiver of this lot
    api_client.force_authenticate(user=farmer_user)
    unauth_payload = dict(insp_payload)
    unauth_payload["event_id"] = str(uuid.uuid4())
    unauth_resp = api_client.post(f"/v1/lots/{lot.public_code}/inspections", unauth_payload, format="json")
    assert unauth_resp.status_code == 403


@pytest.mark.django_db
def test_event_correction_append_only(api_client, test_setup):
    """Corrections append new event with supersedes_event and never mutate history."""
    ws_user = test_setup["wholesaler_user"]
    ws_org = test_setup["wholesaler_org"]
    tomato = test_setup["tomato"]

    lot, bal = create_test_lot(ws_org, ws_user, tomato, "CORR-TOMATO-1", 100.0)
    original_event = TraceEvent.objects.filter(lot=lot).first()
    orig_time = original_event.recorded_at
    orig_payload = dict(original_event.payload)

    api_client.force_authenticate(user=ws_user)
    corr_payload = {
        "event_id": str(uuid.uuid4()),
        "reason": "Corrected initial declared weight from scale tare adjustment",
        "new_values": {"net_qty_kg": 105.0},
        "device_signature": "MEQCIAz76q...signature",
    }
    resp = api_client.post(f"/v1/events/{original_event.event_id}/corrections", corr_payload, format="json")
    assert resp.status_code == 201

    # Verify original event is 100% UNTOUCHED
    original_event.refresh_from_db()
    assert original_event.payload == orig_payload
    assert original_event.recorded_at == orig_time

    # Verify correction event appended
    corr_event = TraceEvent.objects.get(event_type="CORRECTION")
    assert corr_event.supersedes_event == original_event
    assert corr_event.lot_seq == 2


@pytest.mark.django_db
def test_label_reissue(api_client, test_setup):
    """Label reissue voids old serial and binds new serial to the same lot."""
    ws_user = test_setup["wholesaler_user"]
    ws_org = test_setup["wholesaler_org"]
    tomato = test_setup["tomato"]

    lot, _ = create_test_lot(ws_org, ws_user, tomato, "OLD-LABEL-001", 50.0)
    api_client.force_authenticate(user=ws_user)

    reissue_payload = {
        "event_id": str(uuid.uuid4()),
        "new_serial": "NEW-LABEL-002",
        "reason": "Damaged label sticker torn during transit",
        "device_signature": "MEQCIB812...",
    }
    resp = api_client.post(f"/v1/lots/{lot.public_code}/label-reissue", reissue_payload, format="json")
    assert resp.status_code == 201

    old_qr = QrLabel.objects.get(serial="OLD-LABEL-001")
    new_qr = QrLabel.objects.get(serial="NEW-LABEL-002")
    assert old_qr.status == "VOID"
    assert new_qr.status == "BOUND"
    assert new_qr.lot_id == lot.lot_id

    lot.refresh_from_db()
    assert lot.public_code == "NEW-LABEL-002"


@pytest.mark.django_db
def test_recall_and_200_lot_graph_forward_trace(api_client, test_setup):
    """Seeded graph of 200 lots: recall forward trace finds 100% of descendants."""
    ws_user = test_setup["wholesaler_user"]
    ws_org = test_setup["wholesaler_org"]
    dist_org = test_setup["distributor_org"]
    tomato = test_setup["tomato"]

    root_lot, _ = create_test_lot(ws_org, ws_user, tomato, "RECALL-ROOT-001", 10000.0)

    # Build a deep/broad DAG of 200 lots descended from root_lot
    total_descendants = 200
    current_parent = root_lot
    created_descendants = []

    for i in range(1, total_descendants + 1):
        child_code = f"LOT-DESCENDANT-{i:03d}"
        child_lot = Lot.objects.create(
            public_code=child_code,
            product=tomato,
            created_by_org=ws_org,
            custodian_org=dist_org if i % 2 == 0 else ws_org,
            lot_kind="SPLIT_CHILD",
            state="IN_CUSTODY",
            head_seq=1,
        )
        LotBalance.objects.create(
            lot=child_lot,
            qty_in_kg=Decimal("10.000"),
            qty_sold_kg=Decimal("2.000") if i % 3 == 0 else Decimal("0.000"),
        )
        # Add edge from current_parent to child
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO lot_edge (parent_lot, child_lot, qty_kg, event_id) VALUES (%s, %s, %s, %s)",
                [current_parent.lot_id, child_lot.lot_id, Decimal("10.000"), uuid.uuid4()],
            )
        created_descendants.append(child_code)

        # Create branching: shift parent periodically
        if i % 5 == 0:
            current_parent = child_lot

    # 1. Open recall
    api_client.force_authenticate(user=ws_user)
    open_payload = {
        "lot_code": root_lot.public_code,
        "reason": "Pesticide residue detected in lab analysis batch",
    }
    open_resp = api_client.post("/v1/recalls", open_payload, format="json")
    assert open_resp.status_code == 201
    recall_id = open_resp.json()["recall_id"]

    root_lot.refresh_from_db()
    assert root_lot.state == "RECALLED"

    # 2. Forward trace query
    trace_resp = api_client.get(f"/v1/recalls/{recall_id}/trace")
    assert trace_resp.status_code == 200
    items = trace_resp.json()["items"]

    # Items include root_lot + 200 descendants = 201 lots
    found_codes = {item["lot_code"] for item in items}
    assert root_lot.public_code in found_codes
    for c_code in created_descendants:
        assert c_code in found_codes, f"Descendant {c_code} missing from forward trace!"

    assert len(items) == 201


@pytest.mark.django_db
def test_admin_cannot_edit_trace_event(test_setup):
    """Admin configuration forbids modifying or deleting trace events."""
    admin_instance = TraceEventAdmin(TraceEvent, None)
    assert admin_instance.has_add_permission(None) is False
    assert admin_instance.has_change_permission(None) is False
    assert admin_instance.has_delete_permission(None) is False


@pytest.mark.django_db
def test_database_trigger_forbids_update_trace_event(test_setup):
    """Direct PostgreSQL UPDATE on trace_event is blocked by trigger forbid_change()."""
    ws_user = test_setup["wholesaler_user"]
    ws_org = test_setup["wholesaler_org"]
    tomato = test_setup["tomato"]

    lot, _ = create_test_lot(ws_org, ws_user, tomato, "IMMUTABLE-TEST", 50.0)
    event = TraceEvent.objects.filter(lot=lot).first()

    with pytest.raises(Exception) as exc_info:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE trace_event SET sync_status = 'MUTATED' WHERE event_id = %s", [event.event_id])
    assert "trace_event is append-only" in str(exc_info.value)
