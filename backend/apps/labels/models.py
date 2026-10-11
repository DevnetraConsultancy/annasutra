import uuid
from django.db import models
from django.utils import timezone


class QrBlock(models.Model):
    block_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issued_to_org = models.ForeignKey("organisations.Organisation", on_delete=models.CASCADE, related_name="qr_blocks", db_column="issued_to_org")
    issued_by = models.ForeignKey("identity.AppUser", on_delete=models.CASCADE, related_name="issued_qr_blocks", db_column="issued_by")
    issued_at = models.DateTimeField(default=timezone.now)
    count = models.IntegerField()

    class Meta:
        db_table = "qr_block"


class QrLabel(models.Model):
    STATUS_CHOICES = [
        ("ISSUED", "Issued"),
        ("BOUND", "Bound"),
        ("VOID", "Void"),
    ]

    serial = models.TextField(primary_key=True)
    block = models.ForeignKey(QrBlock, on_delete=models.CASCADE, related_name="labels", db_column="block_id")
    issued_to_org = models.ForeignKey("organisations.Organisation", on_delete=models.CASCADE, related_name="labels", db_column="issued_to_org")
    lot = models.ForeignKey("lots.Lot", null=True, blank=True, on_delete=models.SET_NULL, related_name="labels", db_column="lot_id")
    status = models.TextField(choices=STATUS_CHOICES)
    bound_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "qr_label"
