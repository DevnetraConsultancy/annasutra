import uuid
from django.db import models
from django.utils import timezone


class Handover(models.Model):
    STATE_CHOICES = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("ACCEPTED_WITH_DISCREPANCY", "Accepted With Discrepancy"),
        ("DISPUTED", "Disputed"),
        ("REJECTED", "Rejected"),
        ("EXPIRED", "Expired"),
    ]

    handover_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    lot = models.ForeignKey("lots.Lot", on_delete=models.CASCADE, related_name="handovers", db_column="lot_id")
    from_org = models.ForeignKey("organisations.Organisation", on_delete=models.CASCADE, related_name="outbound_handovers", db_column="from_org")
    to_org = models.ForeignKey("organisations.Organisation", on_delete=models.CASCADE, related_name="inbound_handovers", db_column="to_org")
    declared_qty_kg = models.DecimalField(max_digits=12, decimal_places=3)
    received_qty_kg = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    state = models.TextField(choices=STATE_CHOICES)
    opened_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "handover"
