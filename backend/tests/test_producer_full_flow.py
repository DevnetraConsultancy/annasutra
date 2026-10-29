import pytest
import uuid
from rest_framework.test import APIClient
from apps.identity.models import EntityProfile, AppUser, EntityPlot
from apps.organisations.models import Organisation
from apps.lots.models import Lot
from apps.alerts.models import ScanLog


@pytest.mark.django_db
class TestProducerFullFlowAndCustody:
    def test_complete_producer_lifecycle_from_registration_to_handover(self):
        # 1. First-time producer registration via Google / OTP
        client = APIClient()
        signup_resp = client.post(
            "/api/v1/auth/google",
            {
                "email": "kisan.flow@annasutra.in",
                "full_name": "Rameshwardas Patel",
                "phone_e164": "+919876543299",
                "role": "PRODUCER",
            },
            format="json",
        )
        assert signup_resp.status_code == 200
        signup_data = signup_resp.json()
        token = signup_data["access_token"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}", HTTP_X_ENTITY_PHONE="+919876543299")

        # RULE 0: Unapproved producer must NOT have a Unique Farmer ID
        assert not signup_data.get("farmer_uid")
        prof_pre = client.get("/api/v1/me/profile")
        assert prof_pre.status_code == 200
        assert not prof_pre.json().get("farmer_uid")
        assert prof_pre.json()["status"] in ("DRAFT", "SUBMITTED")

        # 2. Producer submits profile for review
        submit_resp = client.post("/api/v1/me/profile/submit", {}, credentials="same-origin")
        # In test mode or draft, submit transitions or marks for review
        profile = EntityProfile.objects.get(phone_e164="+919876543299")

        # 3. Admin review queue inspection: Farmer UID is None before approval
        admin_client = APIClient()
        admin_org = Organisation.objects.create(org_id=uuid.uuid4(), name="National Authority", org_type="OPERATOR", verification="VERIFIED")
        admin_user = AppUser.objects.create(user_id=uuid.uuid4(), org=admin_org, phone_e164="+919999999999", role="OWNER", status="ACTIVE")
        admin_client.force_authenticate(user=admin_user)

        admin_detail = admin_client.get(f"/api/v1/admin/entities/{profile.entity_id}")
        assert admin_detail.status_code == 200
        assert not admin_detail.json().get("farmer_uid")

        # 4. Admin approves producer
        decision_resp = admin_client.post(
            f"/api/v1/admin/entities/{profile.entity_id}/decision",
            {"decision": "APPROVED", "reason": "All farm plots and statutory KYC verified."},
            format="json",
        )
        assert decision_resp.status_code == 200
        approved_data = decision_resp.json()
        assert approved_data["status"] == "VERIFIED"
        farmer_uid = approved_data["farmer_uid"]
        assert farmer_uid.isdigit()
        assert farmer_uid.endswith("919876543299")
        assert len(farmer_uid) == 24

        # 5. Now verified producer profile endpoint returns the minted Unique Farmer ID
        prof_post = client.get("/api/v1/me/profile")
        assert prof_post.status_code == 200
        assert prof_post.json()["farmer_uid"] == farmer_uid
        assert prof_post.json()["status"] == "VERIFIED"

        # 6. Producer self-editable basic profile update under A. Profile
        update_resp = client.put(
            "/api/v1/me/profile",
            {
                "alt_phone": "9876543298",
                "email": "kisan.updated@annasutra.in",
                "village_town": "Bardhaman Rural",
                "district": "Purba Bardhaman",
                "pincode": "713101",
                "override_lock": True,
            },
            format="json",
        )
        assert update_resp.status_code == 200

        # 7. Producer adds a farm plot (Step 2 under Profile)
        plot_resp = client.put(
            "/api/v1/me/plots",
            {
                "plots": [
                    {
                        "plot_name": "North Field Potato Parcel",
                        "khasra_survey_no": "KH-842/1",
                        "area_acres": 3.75,
                        "geojson": {"type": "Polygon", "coordinates": [[[87.86, 23.23], [87.87, 23.23], [87.87, 23.24], [87.86, 23.24], [87.86, 23.23]]]}
                    }
                ],
                "override_lock": True,
            },
            format="json",
        )
        assert plot_resp.status_code == 200
        assert plot_resp.json()["total_acres"] == 3.75

        # 8. Batch / Lot Creation via create-with-qr
        batch_resp = client.post(
            "/api/v1/lots/create-with-qr",
            {
                "crop": "Potato",
                "variety": "Kufri Jyoti",
                "crop_category": "VG",
                "quantity_kg": 750.0,
                "crate_count": 30,
                "grade": "Grade A",
                "farming_method": "Conventional",
                "shelf_life_days": 18,
                "price_per_kg": 35,
            },
            format="json",
        )
        assert batch_resp.status_code == 201
        lot_data = batch_resp.json()
        lot_code = lot_data["public_code"]
        assert "919876543299" in lot_code
        assert lot_data["batch_id"] == lot_code
        assert lot_data["on_hand_kg"] == 750.0
        assert lot_data["product_category_code"] == "VG"

        # 9. Verify QR Image Generation Endpoint
        qr_img_resp = client.get(f"/api/v1/lots/{lot_code}/qr-image")
        assert qr_img_resp.status_code == 200
        assert qr_img_resp["Content-Type"] == "image/png"
        assert len(qr_img_resp.content) > 100

        # 10. Verify Printable Sticker Sheet PDF Endpoint
        pdf_resp = client.get(f"/api/v1/lots/{lot_code}/sticker-pdf?count=24")
        assert pdf_resp.status_code == 200
        assert pdf_resp["Content-Type"] == "application/pdf"
        assert len(pdf_resp.content) > 500

        # 11. Producer edits lot details before handover
        edit_resp = client.put(
            f"/api/v1/lots/{lot_code}",
            {
                "variety": "Kufri Jyoti Premium Certified",
                "net_qty_kg": 745.0,
                "grade": "Export Quality",
                "remarks": "Harvested early morning, sorted and packed in sanitized crates.",
            },
            format="json",
        )
        assert edit_resp.status_code == 200
        assert edit_resp.json()["variety"] == "Kufri Jyoti Premium Certified"
        assert edit_resp.json()["on_hand_kg"] == 745.0

        # 12. Set up Mandi Aggregator entity & user
        from django.utils import timezone
        agg_org = Organisation.objects.create(org_id=uuid.uuid4(), name="Bardhaman Agro Mandi FPO", org_type="AGGREGATOR", verification="VERIFIED")
        agg_user = AppUser.objects.create(user_id=uuid.uuid4(), org=agg_org, phone_e164="+919830022334", role="OWNER", status="ACTIVE")
        agg_profile = EntityProfile.objects.create(
            entity_id=uuid.uuid4(),
            user_id=agg_user.user_id,
            role="AGGREGATOR",
            organisation_name="Bardhaman Agro Mandi FPO",
            phone_e164="+919830022334",
            entity_code="AG-WB-000101",
            status="VERIFIED",
            verified_at=timezone.now(),
            verified_by=admin_user.user_id,
        )

        agg_client = APIClient()
        agg_client.force_authenticate(user=agg_user)

        # 13. Producer dispatches custody handover to Mandi Aggregator
        dispatch_resp = client.post(
            f"/api/v1/lots/{lot_code}/handover-request",
            {
                "target_phone": "+919830022334",
                "target_role": "AGGREGATOR",
                "target_org_id": str(agg_org.org_id),
                "declared_qty_kg": 745.0,
                "vehicle_no": "WB-39-B-8421",
                "handover_pin": "4829",
                "remarks": "Dispatched via refrigerated mini truck.",
            },
            format="json",
        )
        assert dispatch_resp.status_code in (200, 201)
        lot_in_transit = Lot.objects.get(public_code=lot_code)
        assert lot_in_transit.state == "IN_TRANSIT"
        assert lot_in_transit.pending_receiver_org == agg_org

        # 14. Mandi Aggregator receives and accepts custody handover
        accept_resp = agg_client.post(
            f"/api/v1/lots/{lot_code}/handover-accept",
            {
                "received_qty_kg": 745.0,
                "condition": "Excellent Freshness Verified",
                "actor_role": "AGGREGATOR",
                "actor_name": "Bardhaman Agro Mandi FPO",
                "remarks": "Physical crate count matched (30 crates, 745 kg). Temperature 12°C checked.",
            },
            format="json",
        )
        assert accept_resp.status_code == 200
        lot_accepted = Lot.objects.get(public_code=lot_code)
        assert lot_accepted.state == "IN_CUSTODY"
        assert lot_accepted.custodian_org == agg_org
        assert lot_accepted.pending_receiver_org is None

        # 15. Producer can NO LONGER modify lot once handed over (Diamond Rule: Immutability)
        locked_resp = client.put(
            f"/api/v1/lots/{lot_code}",
            {"net_qty_kg": 500.0},
            format="json",
        )
        assert locked_resp.status_code in (403, 404)

        # 16. Admin Consumer Scans endpoint verification (Strict zero fake data)
        # First check with 0 scans
        admin_scans_resp = admin_client.get("/api/v1/admin/consumer-scans")
        assert admin_scans_resp.status_code == 200
        scans_data = admin_scans_resp.json()
        assert scans_data["total_scans"] == 0
        assert scans_data["opt_in_gps_pct"] is None
        assert scans_data["avg_distance_km"] is None
        assert len(scans_data["scans"]) == 0

        # Simulate a real public scan on the lot
        ScanLog.objects.create(
            serial=lot_code,
            coarse_area="Kolkata",
            result="GENUINE",
        )

        admin_scans_post = admin_client.get("/api/v1/admin/consumer-scans")
        assert admin_scans_post.status_code == 200
        scans_data_post = admin_scans_post.json()
        assert scans_data_post["total_scans"] == 1
        assert scans_data_post["opt_in_gps_pct"] == 100.0
        assert len(scans_data_post["scans"]) == 1
        assert scans_data_post["scans"][0]["serial"] == lot_code
        assert scans_data_post["scans"][0]["city_coarse"] == "Kolkata"
