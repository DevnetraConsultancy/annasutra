import uuid
from django.db import models
from django.utils import timezone


class AppUser(models.Model):
    ROLE_CHOICES = [
        ("OWNER", "Owner"),
        ("STAFF", "Staff"),
        ("VIEWER", "Viewer"),
        ("AGENT", "Agent"),
    ]
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("LOCKED", "Locked"),
        ("DISABLED", "Disabled"),
    ]

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("organisations.Organisation", on_delete=models.CASCADE, related_name="users", db_column="org_id")
    phone_e164 = models.TextField(unique=True)
    role = models.TextField(choices=ROLE_CHOICES)
    status = models.TextField(choices=STATUS_CHOICES, default="ACTIVE")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "app_user"

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False


class Device(models.Model):
    device_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="devices", db_column="user_id")
    public_key = models.BinaryField()
    key_alg = models.TextField(default="ES256")
    label = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "device"


class PasskeyCredential(models.Model):
    credential_id = models.BinaryField(primary_key=True)
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="passkeys", db_column="user_id")
    public_key = models.BinaryField()
    sign_count = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "passkey_credential"


class ConsentRecord(models.Model):
    METHOD_CHOICES = [
        ("SELF", "Self"),
        ("ASSISTED", "Assisted"),
    ]

    consent_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="consents", db_column="user_id")
    notice_version = models.TextField()
    language = models.TextField()
    method = models.TextField(choices=METHOD_CHOICES)
    given_at = models.DateTimeField(default=timezone.now)
    withdrawn_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "consent_record"


class EntityProfile(models.Model):
    ROLE_CHOICES = [
        ("PRODUCER", "Producer"),
        ("AGGREGATOR", "Aggregator"),
        ("PROCESSOR", "Processor / Manufacturer"),
        ("WHOLESALER", "Wholesaler"),
        ("DISTRIBUTOR", "Distributor"),
        ("RETAILER", "Retailer"),
    ]
    GENDER_CHOICES = [
        ("FEMALE", "Female"),
        ("MALE", "Male"),
        ("OTHER", "Other"),
        ("UNSPECIFIED", "Unspecified"),
    ]
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("SUBMITTED", "Submitted"),
        ("NEEDS_CHANGES", "Needs Changes"),
        ("VERIFIED", "Verified"),
        ("REJECTED", "Rejected"),
        ("SUSPENDED", "Suspended"),
        ("TRASH", "Trash"),
        ("DELETION_REQUESTED", "Deletion Requested"),
        ("DEACTIVATED", "Deactivated"),
    ]

    entity_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    entity_code = models.CharField(max_length=24, null=True, blank=True, unique=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    organisation_name = models.CharField(max_length=160)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default="UNSPECIFIED")
    phone_e164 = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=190, null=True, blank=True)
    total_land_acres = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, null=True, blank=True)
    village_town = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    photo_object_key = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    version = models.IntegerField(default=1)
    submitted_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "entity_profile"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(total_land_acres__isnull=True) | models.Q(total_land_acres__gt=0),
                name="chk_land",
            ),
            models.CheckConstraint(
                condition=~models.Q(status="VERIFIED") | models.Q(entity_code__isnull=False),
                name="chk_verified",
            ),
        ]


class EntitySensitive(models.Model):
    entity = models.OneToOneField(EntityProfile, primary_key=True, on_delete=models.CASCADE, related_name="sensitive", db_column="entity_id")
    aadhaar_last4 = models.CharField(max_length=4, null=True, blank=True)
    pan_enc = models.BinaryField(max_length=256, null=True, blank=True)
    pan_hmac = models.BinaryField(max_length=32, null=True, blank=True, unique=True)
    bank_holder_enc = models.BinaryField(max_length=256, null=True, blank=True)
    bank_name = models.CharField(max_length=120, null=True, blank=True)
    account_no_enc = models.BinaryField(max_length=256, null=True, blank=True)
    account_last4 = models.CharField(max_length=4, null=True, blank=True)
    ifsc_enc = models.BinaryField(max_length=128, null=True, blank=True)
    upi_enc = models.BinaryField(max_length=256, null=True, blank=True)
    enc_key_id = models.CharField(max_length=32, default="k1-2026")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "entity_sensitive"


class EntityPlot(models.Model):
    plot_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity = models.ForeignKey(EntityProfile, on_delete=models.CASCADE, related_name="plots", db_column="entity_id")
    plot_name = models.CharField(max_length=80)
    area_acres = models.DecimalField(max_digits=10, decimal_places=3)
    district = models.CharField(max_length=100)
    geojson_enc = models.BinaryField()
    enc_key_id = models.CharField(max_length=32, default="k1-2026")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "entity_plot"
        unique_together = (("entity", "plot_name"),)
        constraints = [
            models.CheckConstraint(
                condition=models.Q(area_acres__gt=0),
                name="chk_plot_area",
            ),
        ]


class EntityFacility(models.Model):
    facility_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity = models.ForeignKey(EntityProfile, on_delete=models.CASCADE, related_name="facilities", db_column="entity_id")
    name = models.CharField(max_length=120)
    facility_type = models.CharField(max_length=40)
    address = models.CharField(max_length=300)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    capacity_kg = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    location_enc = models.BinaryField(null=True, blank=True)
    enc_key_id = models.CharField(max_length=32, null=True, blank=True)

    class Meta:
        db_table = "entity_facility"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(capacity_kg__isnull=True) | models.Q(capacity_kg__gt=0),
                name="chk_facility_cap",
            ),
        ]


class EntityRoleDetails(models.Model):
    entity = models.OneToOneField(EntityProfile, primary_key=True, on_delete=models.CASCADE, related_name="role_details", db_column="entity_id")
    details = models.JSONField(default=dict)

    class Meta:
        db_table = "entity_role_details"


class EntityDocument(models.Model):
    DOC_TYPE_CHOICES = [
        ("PAN_IMAGE", "Pan Image"),
        ("FSSAI", "Fssai"),
        ("GST", "Gst"),
        ("TRADE_LICENCE", "Trade Licence"),
        ("MANDI_LICENCE", "Mandi Licence"),
        ("SCALE_CALIBRATION", "Scale Calibration"),
        ("LAND_RECORD", "Land Record"),
        ("FPO_REG", "FPO Registration"),
        ("ORGANIC_CERT", "Organic Certificate"),
        ("OTHER", "Other"),
    ]
    REVIEW_CHOICES = [
        ("UNREVIEWED", "Unreviewed"),
        ("ACCEPTED", "Accepted"),
        ("REJECTED", "Rejected"),
    ]

    doc_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity = models.ForeignKey(EntityProfile, on_delete=models.CASCADE, related_name="documents", db_column="entity_id")
    doc_type = models.CharField(max_length=32, choices=DOC_TYPE_CHOICES)
    doc_number_enc = models.BinaryField(max_length=256, null=True, blank=True)
    object_key = models.CharField(max_length=255)
    sha256 = models.BinaryField(max_length=32)
    review = models.CharField(max_length=20, choices=REVIEW_CHOICES, default="UNREVIEWED")
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "entity_document"


class VerificationReview(models.Model):
    DECISION_CHOICES = [
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("NEEDS_CHANGES", "Needs Changes"),
        ("SUSPENDED", "Suspended"),
        ("TRASH", "Moved to Trash"),
        ("RESTORED", "Restored"),
        ("DELETION_REQUESTED", "Deletion Requested"),
        ("DEACTIVATED", "Deactivated"),
    ]

    review_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity = models.ForeignKey(EntityProfile, on_delete=models.CASCADE, related_name="reviews", db_column="entity_id")
    reviewer_id = models.UUIDField()
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES)
    reason = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "verification_review"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise PermissionError("Append-only log: verification_review updates are strictly forbidden.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError("Append-only log: verification_review deletions are strictly forbidden.")


class ProfileChangeLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    entity = models.ForeignKey(EntityProfile, on_delete=models.CASCADE, related_name="change_logs", db_column="entity_id")
    changed_by = models.UUIDField()
    field_group = models.CharField(max_length=40)
    before_hash = models.BinaryField(max_length=32, null=True, blank=True)
    after_hash = models.BinaryField(max_length=32)
    at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "profile_change_log"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise PermissionError("Append-only log: profile_change_log updates are strictly forbidden.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError("Append-only log: profile_change_log deletions are strictly forbidden.")


class SensitiveAccessLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    entity_id = models.UUIDField()
    actor_id = models.UUIDField()
    field_name = models.CharField(max_length=40)
    reason = models.CharField(max_length=300)
    at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "sensitive_access_log"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise PermissionError("Append-only log: sensitive_access_log updates are strictly forbidden.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError("Append-only log: sensitive_access_log deletions are strictly forbidden.")


class EntityConsentRecord(models.Model):
    consent_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity = models.ForeignKey(EntityProfile, on_delete=models.CASCADE, related_name="consent_records", db_column="entity_id")
    notice_version = models.CharField(max_length=20)
    language = models.CharField(max_length=5)
    purposes = models.CharField(max_length=300)
    given_at = models.DateTimeField(default=timezone.now)
    withdrawn_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "entity_consent_record"


class EntityDeletionRequest(models.Model):
    REASON_CHOICES = [
        ("CEASING_OPERATIONS", "Ceasing agricultural / business operations"),
        ("LAND_TRANSFER", "Sale, transfer, or lease termination of land/premises"),
        ("DPDP_ERASURE", "Account deletion and data privacy request"),
        ("DUPLICATE", "Duplicate or accidental registration"),
        ("OTHER", "Other"),
    ]
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("CANCELLED", "Cancelled"),
    ]

    request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity = models.ForeignKey(EntityProfile, on_delete=models.CASCADE, related_name="deletion_requests", db_column="entity_id")
    requested_by_user_id = models.UUIDField()
    reason = models.CharField(max_length=40, choices=REASON_CHOICES)
    remarks = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    admin_remarks = models.TextField(null=True, blank=True)
    reviewed_by = models.UUIDField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "entity_deletion_request"

