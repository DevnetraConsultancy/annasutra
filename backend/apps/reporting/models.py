import uuid
from django.db import models
from django.utils import timezone


class Recall(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("CLOSED", "Closed"),
    ]

    recall_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    initiated_by_org = models.ForeignKey("organisations.Organisation", on_delete=models.CASCADE, related_name="initiated_recalls", db_column="initiated_by_org")
    root_lot = models.ForeignKey("lots.Lot", on_delete=models.CASCADE, related_name="recalls", db_column="root_lot")
    reason = models.TextField()
    opened_at = models.DateTimeField(default=timezone.now)
    status = models.TextField(choices=STATUS_CHOICES)

    class Meta:
        db_table = "recall"


class AuditAccessLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.UUIDField()
    resource = models.TextField()
    resource_id = models.TextField(null=True, blank=True)
    at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "audit_access_log"
