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
