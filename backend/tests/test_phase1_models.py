"""Unit tests for Phase 1 database models, encryption binding, and append-only audit enforcement."""

import uuid
import pytest
from django.utils import timezone
from apps.identity.models import (
    EntityProfile,
    EntitySensitive,
    EntityPlot,
    VerificationReview,
    ProfileChangeLog,
    SensitiveAccessLog,
    EntityConsentRecord,
)
from apps.identity.services.crypto import (
    encrypt_field,
    decrypt_field,
    compute_pan_hmac,
)


@pytest.mark.django_db
def test_entity_profile_draft_and_sensitive_encryption():
    """Verify EntityProfile creation in DRAFT status and associated AES-256-GCM encrypted sensitive fields."""
    user_id = uuid.uuid4()
    profile = EntityProfile.objects.create(
        user_id=user_id,
        role="PRODUCER",
        first_name="Ramesh",
        last_name="Kumar",
        organisation_name="Bardhaman Organic Co-op",
        phone_e164="+919876543210",
        village_town="Shaktigarh",
        district="Purba Bardhaman",
        state="West Bengal",
        pincode="713101",
        photo_object_key="photos/ramesh_profile.jpg",
        total_land_acres=4.250,
        status="DRAFT",
    )
    assert profile.entity_id is not None
    assert profile.status == "DRAFT"
    assert profile.entity_code is None

    # Sensitive data binding
    pan_raw = "ABCDE1234F"
    pan_enc, key_id = encrypt_field(pan_raw, str(profile.entity_id))
    pan_hmac = compute_pan_hmac(pan_raw)
    acc_enc, _ = encrypt_field("123456789012", str(profile.entity_id))

    sens = EntitySensitive.objects.create(
        entity=profile,
        aadhaar_last4="1234",
        pan_enc=pan_enc,
        pan_hmac=pan_hmac,
        account_no_enc=acc_enc,
        account_last4="9012",
        bank_name="State Bank of India",
        enc_key_id=key_id,
    )
    assert sens.entity_id == profile.entity_id
    assert sens.aadhaar_last4 == "1234"

    # Decrypt and verify matching plaintexts
    decrypted_pan = decrypt_field(sens.pan_enc, str(profile.entity_id), sens.enc_key_id)
    assert decrypted_pan == pan_raw
    decrypted_acc = decrypt_field(sens.account_no_enc, str(profile.entity_id), sens.enc_key_id)
    assert decrypted_acc == "123456789012"


@pytest.mark.django_db
def test_entity_plot_encrypted_polygon():
    """Verify plot polygon encryption and acre area persistence."""
    profile = EntityProfile.objects.create(
        user_id=uuid.uuid4(),
        role="PRODUCER",
        first_name="Balaram",
        last_name="Maji",
        organisation_name="Maji Krishi Farms",
        phone_e164="+919876543211",
        village_town="Memari",
        district="Purba Bardhaman",
        state="West Bengal",
        pincode="713146",
        photo_object_key="photos/balaram.jpg",
        status="DRAFT",
    )

    sample_geojson = '{"type":"Polygon","coordinates":[[[88.1,23.2],[88.11,23.2],[88.11,23.21],[88.1,23.21],[88.1,23.2]]]}'
    geojson_enc, key_id = encrypt_field(sample_geojson, str(profile.entity_id))

    plot = EntityPlot.objects.create(
        entity=profile,
        plot_name="North Field A-1",
        area_acres=2.150,
        district="Purba Bardhaman",
        geojson_enc=geojson_enc,
        enc_key_id=key_id,
    )
    assert plot.plot_id is not None
    assert plot.area_acres == 2.150

    decrypted_geo = decrypt_field(plot.geojson_enc, str(profile.entity_id), plot.enc_key_id)
    assert decrypted_geo == sample_geojson


@pytest.mark.django_db
def test_append_only_audit_log_enforcement():
    """Verify that update and delete operations on audit log models raise PermissionError."""
    profile = EntityProfile.objects.create(
        user_id=uuid.uuid4(),
        role="PRODUCER",
        first_name="Sunil",
        last_name="Das",
        organisation_name="Individual Farmer",
        phone_e164="+919876543212",
        village_town="Galsi",
        district="Purba Bardhaman",
        state="West Bengal",
        pincode="713406",
        photo_object_key="photos/sunil.jpg",
    )

    # 1. VerificationReview
    review = VerificationReview.objects.create(
        entity=profile,
        reviewer_id=uuid.uuid4(),
        decision="NEEDS_CHANGES",
        reason="Clearer photo requested",
    )
    with pytest.raises(PermissionError, match="Append-only log"):
        review.reason = "Tampered reason"
        review.save()

    with pytest.raises(PermissionError, match="Append-only log"):
        review.delete()

    # 2. ProfileChangeLog
    change = ProfileChangeLog.objects.create(
        entity=profile,
        changed_by=uuid.uuid4(),
        field_group="address",
        before_hash=b"\x00" * 32,
        after_hash=b"\x01" * 32,
    )
    with pytest.raises(PermissionError, match="Append-only log"):
        change.field_group = "identity"
        change.save()

    with pytest.raises(PermissionError, match="Append-only log"):
        change.delete()

    # 3. SensitiveAccessLog
    sens_log = SensitiveAccessLog.objects.create(
        entity_id=profile.entity_id,
        actor_id=uuid.uuid4(),
        field_name="pan_enc",
        reason="Verification audit review",
    )
    with pytest.raises(PermissionError, match="Append-only log"):
        sens_log.reason = "Tampered reason"
        sens_log.save()

    with pytest.raises(PermissionError, match="Append-only log"):
        sens_log.delete()


@pytest.mark.django_db
def test_consent_record_lifecycle():
    """Verify statutory consent recording and withdrawal timestamping."""
    profile = EntityProfile.objects.create(
        user_id=uuid.uuid4(),
        role="PRODUCER",
        first_name="Amina",
        last_name="Khatun",
        organisation_name="Amina Organic Farm",
        phone_e164="+919876543213",
        village_town="Katwa",
        district="Purba Bardhaman",
        state="West Bengal",
        pincode="713130",
        photo_object_key="photos/amina.jpg",
    )

    consent = EntityConsentRecord.objects.create(
        entity=profile,
        notice_version="2026.1",
        language="bn",
        purposes="traceability,food_safety,mandi_verification",
    )
    assert consent.given_at is not None
    assert consent.withdrawn_at is None

    # Withdrawal
    consent.withdrawn_at = timezone.now()
    consent.save()
    consent.refresh_from_db()
    assert consent.withdrawn_at is not None
