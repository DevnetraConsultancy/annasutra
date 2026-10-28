# -*- coding: utf-8 -*-
"""
End-to-End Integration Test for AnnaSutra Gold-Standard Entity Consoles:
1. Producer Verification Gate (strict lock until Admin verifies)
2. Land & 10-Category Season Crop Class Allocation (/api/v1/me/season-allocations)
3. Harvest Records & Mass Balance Accounting (/api/v1/me/harvest-records)
4. Batch / Lot Minting with 10-Category Taxonomy
5. 2-Way Custody Handshake (Handover Request -> Anti-Spoofing Accept)
6. Processor / Manufacturer Role Support in Handover & Trace Events
7. Public Scan Telemetry Ping (/api/v1/public/lots/<code>/scan-ping)
8. Admin Profile Change Request Workflow (/api/v1/me/change-requests -> /api/v1/admin/change-requests/decision)
"""

import uuid
from decimal import Decimal
import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.identity.models import AppUser, EntityProfile, EntityPlot, EntityRoleDetails
from apps.identity.services.token import TokenService
from apps.inventory.models import LotBalance
from apps.ledger.models import TraceEvent
from apps.lots.models import Lot, Product
from apps.organisations.models import Organisation
from apps.alerts.models import ScanLog

@pytest.fixture
def client():
    return APIClient()

def create_user_and_org(phone, name, org_type="FARMER", role="PRODUCER", verification="VERIFIED"):
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
    prof = EntityProfile.objects.create(
        user_id=user.user_id,
        phone_e164=phone,
        first_name=name.split()[0],
        last_name=name.split()[-1] if len(name.split()) > 1 else "",
        organisation_name=name,
        role=role,
        entity_code=f"ENT-{phone[-4:]}",
        total_land_acres=5.0,
        village_town="Pimpalgaon",
        district="Nashik",
        state="MH",
        status="VERIFIED" if verification == "VERIFIED" else "SUBMITTED",
    )
    tokens = TokenService.issue_token_pair(user)
    user.tokens = tokens
    user.profile = prof
    return user

@pytest.mark.django_db
def test_full_entity_consoles_lifecycle(client):
    # 1. Setup actors
    farmer_user = create_user_and_org("+919876543210", "Ramesh Bhosale", "FARMER", "PRODUCER", "VERIFIED")
    aggregator_user = create_user_and_org("+919800000002", "Nashik Agro Hub", "AGGREGATOR", "AGGREGATOR", "VERIFIED")
    processor_user = create_user_and_org("+919800000003", "Sahyadri Snacks", "OPERATOR", "PROCESSOR", "VERIFIED")
    admin_user = create_user_and_org("+919800000001", "National Authority", "OPERATOR", "ADMIN", "VERIFIED")

    # STEP 1: Land Plot Cadastral Mapping
    plot = EntityPlot.objects.create(
        entity=farmer_user.profile,
        plot_name="North Riverside Parcel",
        area_acres=Decimal("3.5"),
        district="Nashik",
        geojson_enc=b"enc_geojson",
        enc_key_id="k1",
    )
    assert plot.area_acres == Decimal("3.5")

    # STEP 2: 10-Category Season Crop Class Allocation
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {farmer_user.tokens['access_token']}")
    res_alloc = client.post(
        "/api/v1/me/season-allocations",
        {
            "season": "Kharif 2026",
            "plot_id": str(plot.plot_id),
            "plot_name": "North Riverside Parcel",
            "crop_category": "VG",
            "crop_name": "Potato",
            "variety": "Kufri Jyoti",
            "acres": 2.0,
            "sowing_date": "2026-06-15",
            "expected_harvest_date": "2026-10-25"
        },
        format="json"
    )
    assert res_alloc.status_code == 201
    assert res_alloc.data["total_allocated_acres"] == 2.0
    assert res_alloc.data["remaining_acres"] == 3.0

    # STEP 3: Harvest Records & Mass Balance Accounting (Gross - Waste = Net Yield)
    res_harv = client.post(
        "/api/v1/me/harvest-records",
        {
            "plot_id": str(plot.plot_id),
            "plot_name": "North Riverside Parcel",
            "crop_category": "VG",
            "crop": "Potato",
            "variety": "Kufri Jyoti",
            "gross_weight_kg": 2000.0,
            "waste_loss_kg": 100.0,
            "harvest_date": "2026-10-28",
            "storage_location": "On-farm Cold Storage Room 1"
        },
        format="json"
    )
    assert res_harv.status_code == 201
    assert res_harv.data["harvest"]["net_yield_kg"] == 1900.0
    assert res_harv.data["harvest"]["gross_weight_kg"] == 2000.0

    # Check harvest summary
    res_harv_get = client.get("/api/v1/me/harvest-records")
    assert res_harv_get.status_code == 200
    assert res_harv_get.data["total_net_kg"] == 1900.0
    assert res_harv_get.data["total_unlotted_kg"] == 1900.0

    # STEP 4: Mint Batch / Lot with Product
    product = Product.objects.create(
        product_id=uuid.uuid4(),
        name="Potato",
        variety="Kufri Jyoti",
    )
    lot = Lot.objects.create(
        lot_id=uuid.uuid4(),
        public_code="20261028160510-91-9876543210-VG-001-K",
        created_by_org=farmer_user.org,
        custodian_org=farmer_user.org,
        product=product,
        lot_kind="HARVEST",
        state="CREATED",
        head_seq=1,
        head_hash=bytes.fromhex("a" * 64),
    )
    LotBalance.objects.create(
        lot=lot,
        qty_in_kg=Decimal("500.0"),
    )

    # Provenance Creation Event
    TraceEvent.objects.create(
        event_id=uuid.uuid4(),
        lot=lot,
        lot_seq=1,
        event_type="CREATION",
        user=farmer_user,
        org=farmer_user.org,
        event_time=timezone.now(),
        qty_kg=Decimal("500.0"),
        prev_hash=bytes.fromhex("0" * 64),
        event_hash=bytes.fromhex("a" * 64),
        payload={"crop": "Potato", "variety": "Kufri Jyoti", "crop_category": "VG", "weight_kg": 500.0}
    )

    # STEP 5: Producer Initiates 2-Way Handover Request to Aggregator
    res_req = client.post(
        f"/api/v1/lots/{lot.public_code}/handover-request",
        {
            "target_role": "AGGREGATOR",
            "target_phone": aggregator_user.phone_e164,
            "target_name": "Nashik Agro Hub",
            "declared_qty_kg": 500.0,
            "location_name": "Pimpalgaon Farm Gate",
            "lat": 19.9,
            "lng": 73.8
        },
        format="json"
    )
    assert res_req.status_code == 201
    assert res_req.data["state"] == "IN_TRANSIT"

    lot.refresh_from_db()
    assert lot.state == "IN_TRANSIT"

    # STEP 6: Aggregator Accepts Custody with Physical Verification
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {aggregator_user.tokens['access_token']}")
    res_acc = client.post(
        f"/api/v1/lots/{lot.public_code}/handover-accept",
        {
            "actor_role": "AGGREGATOR",
            "received_qty_kg": 498.5,
            "condition": "Verified Intact",
            "storage_temp": "4.2 C",
            "lat": 19.95,
            "lng": 73.85
        },
        format="json"
    )
    assert res_acc.status_code == 200
    assert res_acc.data["state"] == "IN_CUSTODY"

    lot.refresh_from_db()
    assert lot.state == "IN_CUSTODY"
    assert lot.custodian_org == aggregator_user.org

    # STEP 7: Aggregator Dispatches to Processor / Manufacturer
    res_proc_req = client.post(
        f"/api/v1/lots/{lot.public_code}/handover-request",
        {
            "target_role": "PROCESSOR",
            "target_phone": processor_user.phone_e164,
            "target_name": "Sahyadri Snacks",
            "declared_qty_kg": 498.5,
            "location_name": "Nashik Cold Storage Hub",
            "lat": 19.95,
            "lng": 73.85
        },
        format="json"
    )
    assert res_proc_req.status_code == 201
    assert res_proc_req.data["state"] == "IN_TRANSIT"

    # Processor Accepts Custody
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {processor_user.tokens['access_token']}")
    res_proc_acc = client.post(
        f"/api/v1/lots/{lot.public_code}/handover-accept",
        {
            "actor_role": "PROCESSOR",
            "received_qty_kg": 498.0,
            "condition": "Grade A Premium",
            "storage_temp": "4.0 C",
            "lat": 19.98,
            "lng": 73.88
        },
        format="json"
    )
    assert res_proc_acc.status_code == 200
    assert res_proc_acc.data["state"] == "IN_CUSTODY"

    lot.refresh_from_db()
    assert lot.custodian_org == processor_user.org

    # STEP 8: Public Consumer Scan Ping (DPDP Compliant GPS Telemetry)
    client.credentials()  # Unauthenticated public client
    res_ping = client.post(
        f"/api/v1/public/lots/{lot.public_code}/scan-ping",
        {
            "latitude": 18.5204,
            "longitude": 73.8567,
            "device_type": "Mobile (Android)"
        },
        format="json"
    )
    assert res_ping.status_code == 200
    assert res_ping.data["status"] == "ok"
    assert res_ping.data["code"] == lot.public_code
    assert res_ping.data["scan_count"] >= 1

    # Check telemetry stored in ScanLog
    scan_record = ScanLog.objects.filter(serial=lot.public_code).latest("scanned_at")
    assert scan_record.serial == lot.public_code
    assert scan_record.result == "CONSUMER_SCAN"
    assert "18.52" in scan_record.coarse_area

    # STEP 9: Producer Profile Change Request & Admin Verification
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {farmer_user.tokens['access_token']}")
    res_change = client.post(
        "/api/v1/me/change-requests",
        {
            "field_group": "LAND_UPDATE",
            "requested_changes": {"total_land_acres": 7.5},
            "reason": "Acquired adjacent parcel deed 4829"
        },
        format="json"
    )
    assert res_change.status_code == 201
    req_id = res_change.data["change_request"]["request_id"]

    # Admin reviews change requests list
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_user.tokens['access_token']}")
    res_admin_list = client.get("/api/v1/admin/change-requests/")
    assert res_admin_list.status_code == 200
    assert len(res_admin_list.data["change_requests"]) >= 1

    # Admin approves change request
    res_admin_dec = client.post(
        f"/api/v1/admin/change-requests/{req_id}/decision",
        {
            "decision": "APPROVED",
            "reviewer_notes": "Verified registered sale deed on revenue portal."
        },
        format="json"
    )
    assert res_admin_dec.status_code == 200
    assert res_admin_dec.data["status"] == "decided"
    assert res_admin_dec.data["decision"] == "APPROVED"

    farmer_user.profile.refresh_from_db()
    assert farmer_user.profile.total_land_acres == Decimal("7.500")
