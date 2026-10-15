"""Phase 2 tests: Producer Registration Wizard APIs (Draft, Submit, Plots, Sensitive, Photo, Consent)."""

import io
import uuid
import pytest
from PIL import Image
from rest_framework.test import APIClient

from apps.identity.models import (
    AppUser,
    EntityPlot,
    EntityProfile,
    EntitySensitive,
)
from apps.identity.services.token import TokenService
from apps.organisations.models import Organisation


@pytest.fixture
def test_user(db):
    org = Organisation.objects.create(
        name="Test Farmer Org",
        org_type="FARMER",
        verification="PENDING",
    )
    user = AppUser.objects.create(
        user_id=uuid.uuid4(),
        org=org,
        phone_e164="+919876543210",
        role="OWNER",
        status="ACTIVE",
    )
    return user


@pytest.fixture
def auth_client(test_user):
    client = APIClient()
    token_pair = TokenService.issue_token_pair(test_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_pair['access_token']}")
    return client


@pytest.fixture
def second_user(db):
    org = Organisation.objects.create(
        name="Second Farmer Org",
        org_type="FARMER",
        verification="PENDING",
    )
    user = AppUser.objects.create(
        user_id=uuid.uuid4(),
        org=org,
        phone_e164="+919876543211",
        role="OWNER",
        status="ACTIVE",
    )
    return user


@pytest.fixture
def second_auth_client(second_user):
    client = APIClient()
    token_pair = TokenService.issue_token_pair(second_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_pair['access_token']}")
    return client


def test_my_profile_unauthenticated(db):
    client = APIClient()
    res = client.get("/api/v1/me/profile")
    assert res.status_code in (401, 403)


def test_my_profile_draft_and_optimistic_locking(auth_client, test_user):
    # 1. First GET on empty profile returns NEW status
    res = auth_client.get("/api/v1/me/profile")
    assert res.status_code == 200
    assert res.data["status"] == "NEW"

    # 2. Save partial draft
    draft_data = {
        "first_name": "Ramesh",
        "last_name": "Ghosh",
        "organisation_name": "Ghosh Organic Farm",
        "village_town": "Nabagram",
        "district": "Purba Bardhaman",
        "state": "West Bengal",
        "pincode": "713101",
        "role_details": {
            "farm_type": "INDIVIDUAL",
            "commodities": ["Tomato", "Chilli"],
            "irrigation": "TUBEWELL",
        },
    }
    res = auth_client.put("/api/v1/me/profile", draft_data, format="json")
    assert res.status_code == 200
    assert res.data["first_name"] == "Ramesh"
    assert res.data["status"] == "DRAFT"
    server_version = res.data["version"]
    assert server_version == 2

    # 3. Optimistic locking check: sending an outdated version returns 409 Conflict
    res_conflict = auth_client.put(
        "/api/v1/me/profile",
        {"first_name": "Ramesh Updated", "version": server_version - 1},
        format="json",
    )
    assert res_conflict.status_code == 409
    assert res_conflict.data["code"] == "VERSION_CONFLICT"

    # 4. Correct version update succeeds
    res_ok = auth_client.put(
        "/api/v1/me/profile",
        {"first_name": "Ramesh Updated", "version": server_version},
        format="json",
    )
    assert res_ok.status_code == 200
    assert res_ok.data["first_name"] == "Ramesh Updated"
    assert res_ok.data["version"] == 3


def test_sensitive_encryption_and_validation(auth_client, test_user):
    # First ensure profile draft exists
    auth_client.put("/api/v1/me/profile", {"first_name": "Ramesh", "last_name": "Ghosh"}, format="json")

    # 1. Invalid PAN format rejected
    res_bad_pan = auth_client.put("/api/v1/me/sensitive", {"pan": "INVALID123"}, format="json")
    assert res_bad_pan.status_code == 400
    assert res_bad_pan.data["code"] == "INVALID_PAN"

    # 2. Full Aadhaar (12-digit) STRICTLY REJECTED under RULE 5
    res_full_aadhaar = auth_client.put("/api/v1/me/sensitive", {"aadhaar_last4": "123456789012"}, format="json")
    assert res_full_aadhaar.status_code == 400
    assert res_full_aadhaar.data["code"] == "INVALID_AADHAAR"

    # 3. Valid sensitive data submission
    valid_sensitive = {
        "pan": "ABCDE1234F",
        "aadhaar_last4": "5678",
        "bank_name": "State Bank of India",
        "bank_account": "123456789012",
        "bank_holder_name": "Ramesh Ghosh",
        "ifsc": "SBIN0001234",
    }
    res_sens = auth_client.put("/api/v1/me/sensitive", valid_sensitive, format="json")
    assert res_sens.status_code == 200
    assert res_sens.data["pan_masked"] == "AB******4F"
    assert res_sens.data["aadhaar_last4"] == "5678"
    assert res_sens.data["bank_account_masked"] == "XXXXXXXX9012"

    # 4. Verify raw DB contains only encrypted ciphertext
    profile = EntityProfile.objects.get(user_id=test_user.user_id)
    db_sens = EntitySensitive.objects.get(entity=profile)
    assert bytes(db_sens.pan_enc) != b"ABCDE1234F"
    assert b"ABCDE1234F" not in bytes(db_sens.pan_enc)
    assert b"123456789012" not in bytes(db_sens.account_no_enc)
    assert db_sens.pan_hmac is not None
    assert len(db_sens.pan_hmac) == 32

    # 5. GET /api/v1/me/sensitive returns masked data only
    res_get = auth_client.get("/api/v1/me/sensitive")
    assert res_get.status_code == 200
    assert res_get.data["pan_masked"] == "AB******4F"
    assert res_get.data["aadhaar_last4"] == "5678"
    assert res_get.data["bank_name"] == "State Bank of India"
    assert res_get.data["bank_account_masked"] == "XXXXXXXX9012"


def test_plots_encryption_roundtrip(auth_client, test_user):
    # Ensure profile exists
    auth_client.put("/api/v1/me/profile", {"first_name": "Ramesh", "last_name": "Ghosh"}, format="json")

    # 1. Submit 2 plots with polygon GeoJSON
    plots_payload = {
        "plots": [
            {
                "plot_name": "North Field",
                "area_acres": 2.5,
                "district": "Purba Bardhaman",
                "geojson": {
                    "type": "Polygon",
                    "coordinates": [[[87.85, 23.24], [87.86, 23.24], [87.86, 23.25], [87.85, 23.25], [87.85, 23.24]]],
                },
            },
            {
                "plot_name": "South Orchard",
                "area_acres": 1.75,
                "district": "Purba Bardhaman",
                "geojson": {
                    "type": "Polygon",
                    "coordinates": [[[87.86, 23.23], [87.87, 23.23], [87.87, 23.24], [87.86, 23.24], [87.86, 23.23]]],
                },
            },
        ]
    }
    res = auth_client.put("/api/v1/me/plots", plots_payload, format="json")
    assert res.status_code == 200
    assert len(res.data["plots"]) == 2
    assert res.data["total_acres"] == 4.25

    # 2. Check DB storage is encrypted
    profile = EntityProfile.objects.get(user_id=test_user.user_id)
    db_plot = EntityPlot.objects.filter(entity=profile, plot_name="North Field").first()
    assert db_plot is not None
    assert b"coordinates" not in bytes(db_plot.geojson_enc)

    # 3. GET /api/v1/me/plots decrypts successfully
    res_get = auth_client.get("/api/v1/me/plots")
    assert res_get.status_code == 200
    plots_list = res_get.data["plots"]
    assert len(plots_list) == 2
    assert plots_list[0]["plot_name"] == "North Field"
    assert plots_list[0]["geojson"]["type"] == "Polygon"
    assert len(plots_list[0]["geojson"]["coordinates"][0]) == 5


def test_photo_upload_and_exif_strip(auth_client, test_user):
    auth_client.put("/api/v1/me/profile", {"first_name": "Ramesh", "last_name": "Ghosh"}, format="json")

    # Generate an in-memory image
    img = Image.new("RGB", (640, 480), color=(34, 197, 94))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    buf.name = "producer_photo.jpg"

    res = auth_client.post("/api/v1/me/photo", {"photo": buf}, format="multipart")
    assert res.status_code == 201
    assert "photo_object_key" in res.data
    assert res.data["photo_object_key"].startswith("photos/")

    # Profile photo key is updated
    profile = EntityProfile.objects.get(user_id=test_user.user_id)
    assert profile.photo_object_key == res.data["photo_object_key"]


def test_consent_and_full_submit_flow(auth_client, test_user):
    # 1. Incomplete profile submission fails with 422
    auth_client.put("/api/v1/me/profile", {"first_name": "Ramesh"}, format="json")
    res_incomplete = auth_client.post("/api/v1/me/profile/submit")
    assert res_incomplete.status_code == 422
    assert res_incomplete.data["code"] == "VALIDATION_FAILED"
    assert "last_name" in res_incomplete.data["errors"]
    assert "pincode" in res_incomplete.data["errors"]

    # 2. Complete all required fields
    auth_client.put(
        "/api/v1/me/profile",
        {
            "first_name": "Ramesh",
            "last_name": "Ghosh",
            "organisation_name": "Ghosh Farm Ltd",
            "address_line1": "Station Road",
            "village_town": "Nabagram",
            "district": "Purba Bardhaman",
            "state": "West Bengal",
            "pincode": "713101",
            "photo_object_key": "photos/test_verified.jpg",
            "role_details": {
                "farm_type": "INDIVIDUAL",
                "commodities": ["Tomato", "Potato"],
            },
        },
        format="json",
    )

    # Add plot
    auth_client.put(
        "/api/v1/me/plots",
        {
            "plots": [
                {
                    "plot_name": "Field 1",
                    "area_acres": 3.0,
                    "district": "Purba Bardhaman",
                    "geojson": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]},
                }
            ]
        },
        format="json",
    )

    # Add sensitive
    auth_client.put(
        "/api/v1/me/sensitive",
        {
            "pan": "ABCDE1234F",
            "aadhaar_last4": "9999",
            "bank_name": "State Bank of India",
            "bank_account": "98765432100",
            "bank_holder_name": "Ramesh Ghosh",
            "ifsc": "SBIN0001234",
        },
        format="json",
    )

    # Record consent
    res_consent = auth_client.post(
        "/api/v1/me/consent",
        {
            "notice_version": "v1.0-2026",
            "language": "en",
            "purposes": ["DPDP_PURPOSE_LIMITATION", "AADHAAR_VOLUNTARY_LAST4", "TRACEABILITY_PILOT_TERMS"],
        },
        format="json",
    )
    assert res_consent.status_code == 201

    # 3. Submit profile
    res_submit = auth_client.post("/api/v1/me/profile/submit")
    assert res_submit.status_code == 200
    assert res_submit.data["status"] == "SUBMITTED"

    profile = EntityProfile.objects.get(user_id=test_user.user_id)
    assert profile.status == "SUBMITTED"
    assert profile.submitted_at is not None

    # 4. Subsequent draft edit is locked
    res_locked = auth_client.put("/api/v1/me/profile", {"first_name": "Attempt Change"}, format="json")
    assert res_locked.status_code == 400
    assert res_locked.data["code"] == "PROFILE_LOCKED"


def test_cross_entity_isolation(auth_client, second_auth_client, test_user, second_user):
    # User 1 creates profile and sensitive data
    auth_client.put(
        "/api/v1/me/profile",
        {"first_name": "UserOne", "last_name": "Farmer", "organisation_name": "Org One"},
        format="json",
    )
    auth_client.put(
        "/api/v1/me/sensitive",
        {"pan": "AAAAA1111A", "bank_name": "Bank One", "bank_account": "1111111111", "ifsc": "SBIN0001111"},
        format="json",
    )

    # User 2 reads their own profile
    res2 = second_auth_client.get("/api/v1/me/profile")
    assert res2.status_code == 200
    # User 2 profile is empty or new, NOT User 1's data
    assert res2.data.get("first_name") != "UserOne"

    # User 2 reads their sensitive data -> returns None
    res2_sens = second_auth_client.get("/api/v1/me/sensitive")
    assert res2_sens.status_code == 200
    assert res2_sens.data.get("pan_masked") != "AA******1A"
