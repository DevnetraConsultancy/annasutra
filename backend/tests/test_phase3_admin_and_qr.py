"""Phase 3 Test Suite: Admin Review Queue, Atomic QR Block Allocation & Printable PDF.
Verifies Handover Sections 9, 10, 11:
- Crockford Base32 13-char serial generation and checksum
- Sequential entity code generation {ROLE}-{STATE}-{SEQ6}
- Admin review queue, detail, and DPDP-audited sensitive reveal
- Atomic approval transaction and initial QR block issuance (50 for Producer)
- A4 sticker PDF sheet generation with QR codes
- Real database-backed role stats
"""

import json
import uuid
import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.identity.models import (
    AppUser,
    EntityProfile,
    EntitySensitive,
    EntityPlot,
    VerificationReview,
    SensitiveAccessLog,
    EntityConsentRecord,
)
from apps.identity.services.crypto import CryptoService
from apps.identity.services.entity_allocation import (
    CROCKFORD_ALPHABET,
    generate_crockford_13,
    verify_crockford_13,
    generate_entity_code,
    approve_entity_registration,
)
from apps.identity.services.token import TokenService
from apps.labels.models import QrBlock
from apps.organisations.models import Organisation


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_setup():
    org = Organisation.objects.create(
        org_id=uuid.uuid4(),
        name="Platform Secretariat Admin",
        org_type="OPERATOR",
        verification="VERIFIED",
    )
    user = AppUser.objects.create(
        user_id=uuid.uuid4(),
        org=org,
        phone_e164="+919999999999",
        role="OWNER",
        status="ACTIVE",
    )
    token = TokenService.issue_token_pair(user)["access_token"]
    return {"org": org, "user": user, "token": token}


@pytest.fixture
def submitted_producer():
    org = Organisation.objects.create(
        org_id=uuid.uuid4(),
        name="Nadia Organic Farmers Trust",
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
    token = TokenService.issue_token_pair(user)["access_token"]

    profile = EntityProfile.objects.create(
        entity_id=uuid.uuid4(),
        user_id=user.user_id,
        role="PRODUCER",
        first_name="Ramesh",
        last_name="Ghosh",
        organisation_name="Nadia Organic Farmers Trust",
        phone_e164="+919876543210",
        state="West Bengal",
        district="Nadia",
        village_town="Shantipur",
        pincode="741404",
        address_line1="Plot 42, Riverbank Road",
        total_land_acres=4.750,
        photo_object_key="/media/photos/sample_farmer.jpg",
        status="SUBMITTED",
        submitted_at=timezone.now(),
    )

    # Sensitive data encrypted
    eid = str(profile.entity_id)
    pan_enc = CryptoService.encrypt("ABCDE1234F", entity_id=eid)
    pan_hmac = CryptoService.blind_index_pan("ABCDE1234F")
    acc_enc = CryptoService.encrypt("123456789012", entity_id=eid)
    ifsc_enc = CryptoService.encrypt("SBIN0001234", entity_id=eid)

    EntitySensitive.objects.create(
        entity=profile,
        aadhaar_last4="9876",
        pan_enc=pan_enc,
        pan_hmac=pan_hmac,
        bank_name="State Bank of India",
        account_no_enc=acc_enc,
        account_last4="9012",
        ifsc_enc=ifsc_enc,
        enc_key_id="k1-2026",
    )

    # Plot with encrypted GeoJSON
    polygon_geojson = json.dumps({
        "type": "Polygon",
        "coordinates": [[[88.42, 23.24], [88.43, 23.24], [88.43, 23.25], [88.42, 23.25], [88.42, 23.24]]]
    })
    poly_enc = CryptoService.encrypt(polygon_geojson, entity_id=eid)
    EntityPlot.objects.create(
        plot_id=uuid.uuid4(),
        entity=profile,
        plot_name="Riverbank North Plot",
        area_acres=4.750,
        district="Nadia",
        geojson_enc=poly_enc,
        enc_key_id="k1-2026",
    )

    EntityConsentRecord.objects.create(
        consent_id=uuid.uuid4(),
        entity=profile,
        notice_version="v1.0-2026",
        language="en",
        purposes="DPDP_PURPOSE_LIMITATION,AADHAAR_VOLUNTARY_LAST4",
    )

    return {"org": org, "user": user, "token": token, "profile": profile}


@pytest.mark.django_db
def test_crockford_13_generation_and_checksum_verification():
    """Verify Crockford Base32 13-character serial generation and checksum validation."""
    serials = [generate_crockford_13() for _ in range(50)]
    assert len(set(serials)) == 50  # All unique

    for s in serials:
        assert len(s) == 13
        assert all(c in CROCKFORD_ALPHABET for c in s)
        # Checksum validates
        assert verify_crockford_13(s) is True

    # Tampered serial fails checksum
    tampered = serials[0][:12] + ("Z" if serials[0][12] != "Z" else "A")
    assert verify_crockford_13(tampered) is False


@pytest.mark.django_db
def test_sequential_entity_code_generation():
    """Verify {ROLE}-{STATE}-{SEQ6} code generation adheres to Section 9."""
    code1 = generate_entity_code("PRODUCER", "West Bengal")
    assert code1 == "PR-WB-000101"

    # Simulate profile existing with code1
    user_id = uuid.uuid4()
    EntityProfile.objects.create(
        entity_id=uuid.uuid4(),
        user_id=user_id,
        role="PRODUCER",
        entity_code=code1,
        first_name="Farmer",
        last_name="One",
        organisation_name="Farm 1",
        phone_e164="+919000000001",
        state="West Bengal",
        district="Nadia",
        village_town="Village",
        pincode="741404",
        address_line1="Add 1",
        photo_object_key="/media/photos/1.jpg",
        status="VERIFIED",
    )

    code2 = generate_entity_code("PRODUCER", "West Bengal")
    assert code2 == "PR-WB-000102"

    code_mh = generate_entity_code("AGGREGATOR", "Maharashtra")
    assert code_mh == "AG-MH-000101"


@pytest.mark.django_db
def test_admin_review_queue_and_filters(api_client, admin_setup, submitted_producer):
    """Admin review queue lists submitted entities and supports filtering."""
    client = api_client
    admin_token = admin_setup["token"]

    # Draft profile (should not appear in SUBMITTED queue)
    EntityProfile.objects.create(
        entity_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        role="PRODUCER",
        first_name="Draft",
        last_name="User",
        organisation_name="Draft Org",
        phone_e164="+919111111111",
        state="Bihar",
        district="Patna",
        village_town="Town",
        pincode="800001",
        address_line1="Street 1",
        photo_object_key="/media/photos/draft.jpg",
        status="DRAFT",
    )

    resp = client.get("/api/v1/admin/reviews?status=SUBMITTED", HTTP_AUTHORIZATION=f"Bearer {admin_token}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 1
    assert data["results"][0]["full_name"] == "Ramesh Ghosh"
    assert data["results"][0]["status"] == "SUBMITTED"

    # Query ALL
    resp_all = client.get("/api/v1/admin/reviews?status=ALL", HTTP_AUTHORIZATION=f"Bearer {admin_token}")
    assert resp_all.status_code == 200
    assert resp_all.json()["count"] == 2


@pytest.mark.django_db
def test_admin_entity_detail_view(api_client, admin_setup, submitted_producer):
    """Admin can view detailed profile with decrypted plots and masked sensitive data."""
    client = api_client
    admin_token = admin_setup["token"]
    entity_id = submitted_producer["profile"].entity_id

    resp = client.get(f"/api/v1/admin/entities/{entity_id}", HTTP_AUTHORIZATION=f"Bearer {admin_token}")
    assert resp.status_code == 200
    data = resp.json()

    assert data["first_name"] == "Ramesh"
    assert data["status"] == "SUBMITTED"
    # Plots decrypted for admin map view
    assert len(data["plots"]) == 1
    assert data["plots"][0]["plot_name"] == "Riverbank North Plot"
    assert data["plots"][0]["geojson"]["type"] == "Polygon"

    # Sensitive values remain masked by default
    assert data["sensitive"]["pan_masked"] == "AB******4F"
    assert data["sensitive"]["account_no_masked"] == "XXXXXXXX9012"
    assert data["sensitive"]["aadhaar_last4"] == "9876"


@pytest.mark.django_db
def test_admin_reveal_sensitive_field_audit_logged(api_client, admin_setup, submitted_producer):
    """Revealing sensitive field requires justification and records immutable SensitiveAccessLog."""
    client = api_client
    admin_token = admin_setup["token"]
    entity_id = submitted_producer["profile"].entity_id

    # 1. Missing reason fails
    resp_fail = client.post(
        f"/api/v1/admin/entities/{entity_id}/reveal",
        data={"field": "pan", "reason": "too short"},
        HTTP_AUTHORIZATION=f"Bearer {admin_token}",
    )
    assert resp_fail.status_code == 400
    assert resp_fail.json()["code"] == "REASON_REQUIRED"

    # 2. Valid reason reveals plaintext and creates audit log
    resp_ok = client.post(
        f"/api/v1/admin/entities/{entity_id}/reveal",
        data={
            "field": "pan",
            "reason": "Auditing bank payout KYC discrepancy for APMC mandi registration.",
        },
        HTTP_AUTHORIZATION=f"Bearer {admin_token}",
    )
    assert resp_ok.status_code == 200
    assert resp_ok.json()["plaintext"] == "ABCDE1234F"
    assert resp_ok.json()["field"] == "pan"

    # Verify immutable log row exists in database
    log_row = SensitiveAccessLog.objects.filter(entity_id=entity_id, field_name="pan").first()
    assert log_row is not None
    assert "APMC mandi registration" in log_row.reason
    assert log_row.actor_id == admin_setup["user"].user_id


@pytest.mark.django_db
def test_admin_approval_atomic_transaction_and_qr_issuance(api_client, admin_setup, submitted_producer):
    """Approving an entity assigns code, transitions status to VERIFIED, and allocates 50 QR labels."""
    client = api_client
    admin_token = admin_setup["token"]
    entity = submitted_producer["profile"]
    entity_id = entity.entity_id

    resp = client.post(
        f"/api/v1/admin/entities/{entity_id}/decision",
        data={
            "decision": "APPROVED",
            "reason": "Verified agricultural land records and valid DPDP statutory consent.",
            "qr_count": 50,
        },
        HTTP_AUTHORIZATION=f"Bearer {admin_token}",
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "VERIFIED"
    assert data["entity_code"] == "PR-WB-000101"
    assert data["qr_count"] == 50
    assert "block_id" in data

    # Verify DB state
    entity.refresh_from_db()
    assert entity.status == "VERIFIED"
    assert entity.entity_code == "PR-WB-000101"
    assert entity.verified_at is not None

    # Organisation is verified
    submitted_producer["org"].refresh_from_db()
    assert submitted_producer["org"].verification == "VERIFIED"

    # VerificationReview logged
    review = VerificationReview.objects.filter(entity=entity, decision="APPROVED").first()
    assert review is not None

    # QrBlock & QrLabels created
    block = QrBlock.objects.get(block_id=data["block_id"])
    assert block.count == 50
    assert block.labels.count() == 50
    assert block.labels.filter(status="ISSUED").count() == 50


@pytest.mark.django_db
def test_my_qr_blocks_and_pdf_sheet_download(api_client, admin_setup, submitted_producer):
    """Producer can view allocated QR blocks and download printable A4 PDF sticker sheet."""
    client = api_client
    producer_token = submitted_producer["token"]
    entity = submitted_producer["profile"]

    # First approve entity
    approve_entity_registration(
        entity=entity,
        admin_user=admin_setup["user"],
        qr_count=50,
    )

    # 1. GET /api/v1/me/qr-blocks
    resp_blocks = client.get("/api/v1/me/qr-blocks", HTTP_AUTHORIZATION=f"Bearer {producer_token}")
    assert resp_blocks.status_code == 200
    data = resp_blocks.json()
    assert len(data["blocks"]) == 1
    assert data["total_issued"] == 50
    assert data["total_available"] == 50
    assert data["total_bound"] == 0
    block_id = data["blocks"][0]["block_id"]

    # 2. GET /api/v1/me/qr-blocks/{block_id}/sheet.pdf
    resp_pdf = client.get(f"/api/v1/me/qr-blocks/{block_id}/sheet.pdf", HTTP_AUTHORIZATION=f"Bearer {producer_token}")
    assert resp_pdf.status_code == 200
    assert resp_pdf["Content-Type"] == "application/pdf"
    assert resp_pdf.content.startswith(b"%PDF-")
    assert len(resp_pdf.content) > 5000  # Multi-page valid PDF binary


@pytest.mark.django_db
def test_my_role_stats_real_database_aggregates(api_client, admin_setup, submitted_producer):
    """GET /api/v1/me/stats returns accurate database-computed metrics without simulations."""
    client = api_client
    producer_token = submitted_producer["token"]
    entity = submitted_producer["profile"]

    # Approve and allocate 50 QR labels
    approve_entity_registration(
        entity=entity,
        admin_user=admin_setup["user"],
        qr_count=50,
    )

    resp_stats = client.get("/api/v1/me/stats", HTTP_AUTHORIZATION=f"Bearer {producer_token}")
    assert resp_stats.status_code == 200
    data = resp_stats.json()

    assert data["role"] == "PRODUCER"
    assert data["status"] == "VERIFIED"
    assert data["entity_code"] == "PR-WB-000101"
    stats = data["stats"]
    assert stats["qr_labels_available"] == 50
    assert stats["qr_labels_bound"] == 0
    assert stats["batches_created"] == 0
    assert stats["total_kg_declared"] == 0.0
    assert stats["plots_count"] == 1
    assert stats["total_land_acres"] == 4.750
