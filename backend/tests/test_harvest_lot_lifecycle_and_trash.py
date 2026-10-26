import uuid
import pytest
from rest_framework import status
from apps.identity.models import AppUser, EntityProfile, VerificationReview
from apps.organisations.models import Organisation, Plot
from apps.lots.models import Lot, Product
from apps.inventory.models import LotBalance
from apps.identity.services.token import TokenService


@pytest.fixture
def test_setup(db):
    org = Organisation.objects.create(
        org_id=uuid.uuid4(),
        name="Biswas Agro Test",
        org_type="FARMER",
        verification="VERIFIED",
    )
    user = AppUser.objects.create(
        user_id=uuid.uuid4(),
        org=org,
        role="OWNER",
        phone_e164="+919876500001",
    )
    token = TokenService.issue_token_pair(user)["access_token"]

    # Create admin user
    admin_org = Organisation.objects.create(
        org_id=uuid.uuid4(),
        name="AnnaSutra Admin Node",
        org_type="OPERATOR",
        verification="VERIFIED",
    )
    admin_user = AppUser.objects.create(
        user_id=uuid.uuid4(),
        org=admin_org,
        role="STAFF",
        phone_e164="+919999900001",
    )
    admin_token = TokenService.issue_token_pair(admin_user)["access_token"]

    # Create EntityProfile
    profile = EntityProfile.objects.create(
        entity_id=uuid.uuid4(),
        user_id=user.user_id,
        role="PRODUCER",
        first_name="Ramesh",
        last_name="Biswas",
        organisation_name="Biswas Agro Test",
        phone_e164="+919876500001",
        village_town="Naihati",
        district="North 24 Parganas",
        state="West Bengal",
        pincode="743165",
        status="VERIFIED",
        entity_code="PRODUCER-WB-000001",
    )

    from apps.organisations.models import FarmerProfile
    fp = FarmerProfile.objects.create(
        farmer_org=org,
        registered_by_user=user,
    )
    plot = Plot.objects.create(
        plot_id=uuid.uuid4(),
        farmer_org=fp,
        village="Naihati",
        district="North 24 Parganas",
        area_ha=1.0,
    )

    return {
        "org": org,
        "user": user,
        "token": token,
        "admin_org": admin_org,
        "admin_user": admin_user,
        "admin_token": admin_token,
        "profile": profile,
        "plot": plot,
    }


def test_harvest_lot_create_list_and_edit_lifecycle(api_client, test_setup):
    token = test_setup["token"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # 1. Create a rich harvest lot without specifying label_serial (auto-minted)
    payload = {
        "crop": "Tomato",
        "variety": "Hybrid Red 105",
        "category": "Vegetable",
        "net_qty_kg": 750.0,
        "unit": "Kg",
        "packages_count": 25,
        "package_type": "Plastic Crates",
        "origin_plot_id": str(test_setup["plot"].plot_id),
        "grade": "Grade A",
        "farming_method": "Organic NPOP",
        "moisture_pct": 12.4,
        "base_price_per_unit": 28.50,
        "estimated_value": 21375.0,
        "payment_status": "PENDING",
        "intended_buyer": "APMC Mandi Aggregator",
        "remarks": "Early morning harvest, pre-cooled.",
    }

    resp = api_client.post("/api/v1/lots/", payload, format="json")
    assert resp.status_code == status.HTTP_201_CREATED, resp.data
    lot_code = resp.data["public_code"]
    assert lot_code is not None
    assert len(lot_code) == 12
    assert resp.data["is_editable"] is True

    # 2. List lots with filter by crop
    list_resp = api_client.get("/api/v1/lots/?crop=Tomato", format="json")
    assert list_resp.status_code == status.HTTP_200_OK
    items = list_resp.data["items"]
    assert len(items) >= 1
    found = next(i for i in items if i["public_code"] == lot_code)
    assert found["crop"] == "Tomato"
    assert found["variety"] == "Hybrid Red 105"
    assert found["grade"] == "Grade A"
    assert found["is_editable"] is True

    # 3. Edit the lot while in farm custody (allowed)
    edit_payload = {
        "crop": "Tomato",
        "variety": "Hybrid Red 105 Premium",
        "net_qty_kg": 800.0,
        "grade": "Grade A+",
        "remarks": "Updated harvest weight after weighing.",
    }
    edit_resp = api_client.put(f"/api/v1/lots/{lot_code}", edit_payload, format="json")
    assert edit_resp.status_code == status.HTTP_200_OK
    assert edit_resp.data["is_editable"] is True

    # 4. Lock the lot by changing state to IN_TRANSIT (simulate handover dispatch)
    lot = Lot.objects.get(public_code=lot_code)
    lot.pending_receiver_org = test_setup["admin_org"]
    lot.state = "IN_TRANSIT"
    lot.save()

    # 5. Attempting to edit now MUST be forbidden with LOT_LOCKED
    locked_resp = api_client.put(f"/api/v1/lots/{lot_code}", edit_payload, format="json")
    assert locked_resp.status_code == status.HTTP_403_FORBIDDEN
    assert locked_resp.data["code"] == "LOT_LOCKED"


def test_admin_producer_trash_restore_and_purge(api_client, test_setup):
    admin_token = test_setup["admin_token"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
    entity_id = str(test_setup["profile"].entity_id)

    # 1. Admin moves entity to TRASH
    trash_resp = api_client.post(
        f"/api/v1/admin/entities/{entity_id}/decision",
        {"decision": "TRASH", "reason": "Moved to trash test."},
        format="json",
    )
    assert trash_resp.status_code == status.HTTP_200_OK
    assert trash_resp.data["status"] == "TRASH"

    # 2. Check that active list excludes trash, but trash filter returns it
    all_resp = api_client.get("/api/v1/admin/reviews?status=ALL", format="json")
    assert not any(r["entity_id"] == entity_id for r in all_resp.data["results"])

    trash_list = api_client.get("/api/v1/admin/reviews?status=TRASH", format="json")
    assert any(r["entity_id"] == entity_id for r in trash_list.data["results"])

    # 3. Admin restores entity from TRASH
    restore_resp = api_client.post(f"/api/v1/admin/entities/{entity_id}/restore", {}, format="json")
    assert restore_resp.status_code == status.HTTP_200_OK
    assert restore_resp.data["status"] in ("VERIFIED", "SUBMITTED")

    # 4. Move to trash again and purge with word confirmation 'DELETE'
    api_client.post(
        f"/api/v1/admin/entities/{entity_id}/decision",
        {"decision": "TRASH", "reason": "Purge test."},
        format="json",
    )

    # Purge without confirmation fails
    bad_purge = api_client.post(f"/api/v1/admin/entities/{entity_id}/purge", {"confirmation": "WRONG"}, format="json")
    assert bad_purge.status_code == status.HTTP_400_BAD_REQUEST

    # Purge with confirmation 'DELETE' succeeds
    good_purge = api_client.post(f"/api/v1/admin/entities/{entity_id}/purge", {"confirmation": "DELETE"}, format="json")
    assert good_purge.status_code == status.HTTP_200_OK
    assert not EntityProfile.objects.filter(entity_id=entity_id).exists()
