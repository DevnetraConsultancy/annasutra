import uuid
from django.db import models
from django.utils import timezone


class ScanLog(models.Model):
    scan_id = models.BigAutoField(primary_key=True)
    serial = models.TextField()
    user_id = models.UUIDField(null=True, blank=True)
    scanned_at = models.DateTimeField(default=timezone.now)
    coarse_area = models.TextField(null=True, blank=True)
    result = models.TextField()

    class Meta:
        db_table = "scan_log"


class Alert(models.Model):
    SEVERITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
    ]
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("REVIEWING", "Reviewing"),
        ("CLOSED", "Closed"),
    ]

    alert_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    rule = models.TextField()
    lot = models.ForeignKey("lots.Lot", null=True, blank=True, on_delete=models.SET_NULL, related_name="alerts", db_column="lot_id")
    severity = models.TextField(choices=SEVERITY_CHOICES)
    detail = models.JSONField(default=dict)
    status = models.TextField(choices=STATUS_CHOICES, default="OPEN")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "alert"
