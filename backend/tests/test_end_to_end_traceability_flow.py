import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestEndToEndTraceabilityFlow:
    def test_google_signin_and_deterministic_farmer_id(self):
        client = APIClient()
        resp = client.post(
            "/api/v1/auth/google",
            {
                "email": "ramesh.kisan@gmail.com",
                "full_name": "Ramesh Chandra Kisan",
                "phone_e164": "+919876543210",
                "role": "PRODUCER",
            },
            format="json",
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["authenticated"] is True
        assert data["auth_provider"] == "GOOGLE"
        # REQUIREMENT 0: Unapproved producer must NOT have a farmer_uid upon initial sign-in
        assert not data.get("farmer_uid")

        # Check profile endpoint returns null / empty farmer_uid before admin approval
        token = data["access_token"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}", HTTP_X_ENTITY_PHONE="+919876543210")
        prof_resp = client.get("/api/v1/me/profile")
        assert prof_resp.status_code == 200
        assert not prof_resp.json().get("farmer_uid")

        # Admin approves the producer registration
        from apps.identity.models import EntityProfile, AppUser
        from apps.identity.services.entity_allocation import approve_entity_registration
        profile = EntityProfile.objects.get(phone_e164="+919876543210")
        admin_user = AppUser.objects.filter(role__in=["OWNER", "STAFF"]).first()
        res = approve_entity_registration(entity=profile, admin_user=admin_user)
        assert res["status"] == "VERIFIED"
        farmer_uid = res["farmer_uid"]
        # Format: YYYYMMDDHHMMSS (14 digits) + 919876543210 (12 digits) = 26 digits
        assert farmer_uid.isdigit()
        assert farmer_uid.endswith("919876543210")
        assert len(farmer_uid) == 26

        # Now verified profile endpoint returns the minted deterministic farmer_uid
        prof_resp2 = client.get("/api/v1/me/profile")
        assert prof_resp2.status_code == 200
        assert prof_resp2.json()["farmer_uid"] == farmer_uid

    def test_all_10_product_categories_and_full_custody_handover_to_retailer(self):
        farmer_client = APIClient()
        auth_resp = farmer_client.post(
            "/api/v1/auth/google",
            {
                "email": "farmer.origin@annasutra.in",
                "full_name": "Subhash Maity",
                "phone_e164": "+919830011223",
                "role": "PRODUCER",
            },
            format="json",
        )
        assert auth_resp.status_code == 200
        farmer_token = auth_resp.json()["access_token"]
        farmer_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {farmer_token}",
            HTTP_X_ENTITY_PHONE="+919830011223",
        )

        # Verify all 10 official product category codes mint non-colliding 32-char Lot IDs
        categories = ["FG", "PU", "OI", "FR", "VG", "SP", "CC", "LS", "SC", "OT"]
        minted_codes = set()
        fr_lot_code = None

        for idx, cat_code in enumerate(categories, start=1):
            create_resp = farmer_client.post(
                "/api/v1/lots/",
                {
                    "crop": f"Crop_{cat_code}",
                    "product_category_code": cat_code,
                    "variety": "Premium Hybrid",
                    "net_qty_kg": 500,
                    "grade": "Grade A",
                    "farming_method": "Organic NPOP",
                },
                format="json",
            )
            assert create_resp.status_code == 201
            lot_data = create_resp.json()
            code = lot_data["public_code"]
            assert code not in minted_codes
            minted_codes.add(code)
            assert len(code) == 32
            assert "919830011223" in code
            assert f"{cat_code}{idx:03d}" in code
            assert lot_data["product_category_code"] == cat_code
            if cat_code == "FR":
                fr_lot_code = code

        assert len(minted_codes) == 10
        assert fr_lot_code is not None

        # Step 1: Before Retailer verification, public view must show is_retailer_verified = False
        pub_pre = farmer_client.get(f"/api/v1/public/lots/{fr_lot_code}")
        assert pub_pre.status_code == 200
        assert pub_pre.json()["is_retailer_verified"] is False
        assert pub_pre.json()["product_category_code"] == "FR"

        html_pre = farmer_client.get(f"/l/{fr_lot_code}")
        assert html_pre.status_code == 200
        assert "Supply-Chain In-Transit Gatekeeper" in html_pre.content.decode("utf-8")

        # Step 2: Farmer requests custody handover to AGGREGATOR
        ho_req = farmer_client.post(
            f"/api/v1/lots/{fr_lot_code}/handover-request",
            {
                "to_role": "AGGREGATOR",
                "to_name": "Hooghly APMC Aggregator Hub",
                "to_phone": "+919830099887",
                "declared_qty_kg": 500,
                "vehicle_no": "WB-15-8899",
            },
            format="json",
        )
        assert ho_req.status_code in (200, 201)
        assert ho_req.json()["pending_handover"]["status"] == "PENDING_ACCEPTANCE"

        # Step 3: Aggregator logs in, checks incoming handovers, and accepts custody
        agg_client = APIClient()
        agg_auth = agg_client.post(
            "/api/v1/auth/google",
            {
                "email": "aggregator@annasutra.in",
                "full_name": "Hooghly APMC Aggregator Hub",
                "phone_e164": "+919830099887",
                "role": "AGGREGATOR",
            },
            format="json",
        )
        agg_token = agg_auth.json()["access_token"]
        agg_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {agg_token}",
            HTTP_X_ENTITY_PHONE="+919830099887",
        )

        inc_resp = agg_client.get("/api/v1/lots/handovers/incoming")
        assert inc_resp.status_code == 200
        incoming_codes = [item["public_code"] for item in inc_resp.json()["incoming_requests"]]
        assert fr_lot_code in incoming_codes

        accept_resp = agg_client.post(
            f"/api/v1/lots/{fr_lot_code}/handover-accept",
            {
                "actor_role": "AGGREGATOR",
                "actor_name": "Hooghly APMC Aggregator Hub",
                "received_qty_kg": 498.5,
                "condition": "FRESH_GRADE_A",
                "storage_temp": "12C",
                "lat": 22.9012,
                "lng": 88.3891,
            },
            format="json",
        )
        assert accept_resp.status_code == 200
        assert accept_resp.json()["current_custodian_role"] == "AGGREGATOR"
        assert accept_resp.json()["is_editable"] is False

        # Verify Farmer can no longer edit the batch once custody is handed over
        edit_attempt = farmer_client.put(
            f"/api/v1/lots/{fr_lot_code}",
            {"net_qty_kg": 999},
            format="json",
        )
        assert edit_attempt.status_code in (403, 409)
        assert edit_attempt.json()["code"] == "LOT_LOCKED"

        # Step 4: Distributor appends QR scan telemetry (weight, condition, photo, GPS)
        append_resp = agg_client.post(
            f"/api/v1/lots/{fr_lot_code}/append-scan",
            {
                "actor_role": "DISTRIBUTOR",
                "actor_name": "Bengal Cold-Chain Fleet",
                "weight_kg": 497.0,
                "condition": "COLD_CHAIN_INTACT",
                "storage_temp": "4.0C",
                "lat": 22.6510,
                "lng": 88.3420,
            },
            format="json",
        )
        assert append_resp.status_code in (200, 201)
        assert append_resp.json()["is_retailer_verified"] is False

        # Step 5: Retailer accepts custody at retail shop -> unlocks Consumer Trust Passport!
        retail_resp = agg_client.post(
            f"/api/v1/lots/{fr_lot_code}/handover-accept",
            {
                "actor_role": "RETAILER",
                "actor_name": "Kolkata Fresh Mart Retail",
                "received_qty_kg": 496.5,
                "condition": "GOOD_MARKET_READY",
                "storage_temp": "6.0C Shelf",
                "lat": 22.5726,
                "lng": 88.3639,
            },
            format="json",
        )
        assert retail_resp.status_code == 200
        assert retail_resp.json()["is_retailer_verified"] is True
        assert len(retail_resp.json()["journey_checkpoints"]) == 4

        # Step 5B: Retailer splits accepted lot into Small Packet Batch (200 x 500g = 100 kg) with Child Batch QR
        pkt_resp = agg_client.post(
            f"/api/v1/lots/{fr_lot_code}/packet-batches",
            {
                "actor_role": "RETAILER",
                "actor_name": "Kolkata Fresh Mart Retail",
                "packet_weight_g": 500,
                "packet_count": 200,
                "package_label": "500g Retail Pouch",
                "location_name": "Kolkata Fresh Mart Pack Counter",
            },
            format="json",
        )
        assert pkt_resp.status_code == 201
        pkt_data = pkt_resp.json()["packet_batch"]
        child_code = pkt_data["public_code"]
        assert len(child_code) == 32
        assert pkt_data["parent_lot_code"] == fr_lot_code
        assert pkt_data["packet_weight_g"] == 500.0
        assert pkt_data["packet_count"] == 200
        # Parent balance should now be reduced by 100 kg (from 496.5 to 396.5)
        assert pkt_resp.json()["parent_lot"]["on_hand_kg"] == pytest.approx(396.5, 0.01)

        # Consumer scans child packet batch QR -> sees full upstream lineage & Retailer unlocked view
        child_pub = farmer_client.get(f"/api/v1/public/lots/{child_code}")
        assert child_pub.status_code == 200
        child_pub_json = child_pub.json()
        assert child_pub_json["parent_lot_code"] == fr_lot_code
        assert child_pub_json["packet_weight_g"] == 500.0
        assert child_pub_json["is_retailer_verified"] is True
        assert len(child_pub_json["journey_hops"]) >= 5

        # Step 6: Consumer scans parent QR at Retailer shop -> sees unlocked Consumer Trust Passport!
        pub_post = farmer_client.get(f"/api/v1/public/lots/{fr_lot_code}")
        assert pub_post.status_code == 200
        pub_json = pub_post.json()
        assert pub_json["is_retailer_verified"] is True
        assert pub_json["current_stage_role"] == "RETAILER"
        assert len(pub_json["journey_hops"]) >= 4

        html_post = farmer_client.get(f"/l/{fr_lot_code}")
        assert html_post.status_code == 200
        html_text = html_post.content.decode("utf-8")
        assert "Retailer Shop Checked-In — Full Consumer Trust Passport Unlocked" in html_text
        assert "Verified Farm-to-Retailer Custody &amp; Condition Ledger" in html_text

        # Step 7: Consumer Scan Ping with Opt-In GPS -> Haversine distance & Admin Analytics
        ping_resp = farmer_client.post(
            f"/api/v1/public/lots/{child_code}/scan-ping",
            {"latitude": 22.5800, "longitude": 88.3700, "device_type": "Android APK"},
            format="json",
        )
        assert ping_resp.status_code == 200
        ping_data = ping_resp.json()
        assert ping_data["status"] == "ok"
        assert ping_data["distance_km"] is not None

    def test_gmail_multi_role_portal_and_single_admin_lock(self):
        """
        Verifies Phases 1 & 2:
        - Gmail primary identity without mobile phone gets 26-digit Role ID using 000000xxxx serial
        - One Gmail can register multiple roles (PRODUCER + AGGREGATOR) via /api/v1/me/registrations
        - Single Admin Lock: only devnetraconsultancy@gmail.com can access /api/v1/admin/* (403 otherwise)
        """
        from apps.identity.models import AppUser, EntityProfile
        from apps.identity.services.entity_allocation import approve_entity_registration
        from apps.organisations.models import Organisation

        org = Organisation.objects.create(
            name="Kisan MultiRole Org",
            org_type="FARMER",
        )

        # 1. Create a Gmail-only user (no phone_e164)
        gmail_user = AppUser.objects.create(
            org=org,
            email="kisan.multirole@gmail.com",
            phone_e164=None,
            role="OWNER",
            status="ACTIVE",
        )
        client = APIClient()
        client.force_authenticate(user=gmail_user)

        # Non-admin Gmail must receive 403 on Admin endpoints
        forbidden_res = client.get("/api/v1/admin/reviews")
        assert forbidden_res.status_code == 403

        # 2. Create PRODUCER and AGGREGATOR registrations under the same Gmail via Portal API
        r1 = client.post("/api/v1/me/registrations", {"role": "PRODUCER"}, format="json")
        assert r1.status_code in (200, 201)
        r2 = client.post("/api/v1/me/registrations", {"role": "AGGREGATOR"}, format="json")
        assert r2.status_code in (200, 201)

        portal_res = client.get("/api/v1/me/registrations")
        assert portal_res.status_code == 200
        portal_json = portal_res.json()
        assert portal_json["email"] == "kisan.multirole@gmail.com"
        assert portal_json["is_admin"] is False
        reg_map = {item["role"]: item for item in portal_json["registrations"]}
        assert reg_map["PRODUCER"]["registered"] is True
        assert reg_map["AGGREGATOR"]["registered"] is True
        assert reg_map["RETAILER"]["registered"] is False

        # 3. Approve PRODUCER registration without mobile -> mints 26-digit Role ID with 000000xxxx serial
        prod_profile = EntityProfile.objects.get(user_id=gmail_user.user_id, role="PRODUCER")
        admin_user = AppUser.objects.create(
            org=org,
            email="devnetraconsultancy@gmail.com",
            phone_e164="+919000000099",
            role="OWNER",
            status="ACTIVE",
        )
        approval = approve_entity_registration(
            entity=prod_profile,
            admin_user=admin_user,
            review_notes="Approved Gmail-only",
        )
        role_uid = approval["farmer_uid"]
        assert len(role_uid) == 26
        assert role_uid[14:16] == "91"
        assert role_uid[-10:].startswith("000000")

        # 4. Single Admin Lock allows devnetraconsultancy@gmail.com
        admin_client = APIClient()
        admin_client.force_authenticate(user=admin_user)
        admin_res = admin_client.get("/api/v1/admin/reviews")
        assert admin_res.status_code == 200

