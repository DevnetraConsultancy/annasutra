import uuid
from django.db import models
from django.utils import timezone


class TraceEvent(models.Model):
    QTY_BASIS_CHOICES = [
        ("MEASURED", "Measured"),
        ("ESTIMATED", "Estimated"),
        ("DECLARED", "Declared"),
    ]

    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    lot = models.ForeignKey("lots.Lot", on_delete=models.CASCADE, related_name="events", db_column="lot_id")
    lot_seq = models.BigIntegerField()
    event_type = models.TextField()
    event_time = models.DateTimeField()
    recorded_at = models.DateTimeField(default=timezone.now)
    org = models.ForeignKey("organisations.Organisation", on_delete=models.CASCADE, related_name="events", db_column="org_id")
    user = models.ForeignKey("identity.AppUser", on_delete=models.CASCADE, related_name="events", db_column="user_id")
    device = models.ForeignKey("identity.Device", null=True, blank=True, on_delete=models.SET_NULL, related_name="events", db_column="device_id")
    on_behalf_of = models.ForeignKey("organisations.Organisation", null=True, blank=True, on_delete=models.SET_NULL, related_name="on_behalf_events", db_column="on_behalf_of")
    facility = models.ForeignKey("organisations.Facility", null=True, blank=True, on_delete=models.SET_NULL, related_name="events", db_column="facility_id")
    counterparty_org = models.ForeignKey("organisations.Organisation", null=True, blank=True, on_delete=models.SET_NULL, related_name="counterparty_events", db_column="counterparty_org")
    qty_kg = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    qty_basis = models.TextField(choices=QTY_BASIS_CHOICES, null=True, blank=True)
    payload = models.JSONField(default=dict)
    supersedes_event = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="superseded_by", db_column="supersedes_event")
    sync_status = models.TextField(default="ACCEPTED")
    device_signature = models.BinaryField(null=True, blank=True)
    prev_hash = models.BinaryField(null=True, blank=True)
    event_hash = models.BinaryField()

    class Meta:
        db_table = "trace_event"
        unique_together = (("lot", "lot_seq"),)


class HashAnchor(models.Model):
    anchor_date = models.DateField(primary_key=True)
    root_hash = models.BinaryField()
    location = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "hash_anchor"
