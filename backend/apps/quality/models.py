import uuid
from django.db import models


class Inspection(models.Model):
    inspection_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    event = models.OneToOneField("ledger.TraceEvent", on_delete=models.CASCADE, related_name="inspection", db_column="event_id")
    grade = models.TextField(null=True, blank=True)
    defect_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature_c = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "inspection"


class Evidence(models.Model):
    KIND_CHOICES = [
        ("PHOTO", "Photo"),
        ("SCALE_PHOTO", "Scale Photo"),
        ("LAB_CERT", "Lab Certificate"),
        ("DOC", "Document"),
    ]

    evidence_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    event = models.ForeignKey("ledger.TraceEvent", on_delete=models.CASCADE, related_name="evidences", db_column="event_id")
    kind = models.TextField(choices=KIND_CHOICES)
    object_key = models.TextField()
    sha256 = models.BinaryField()

    class Meta:
        db_table = "evidence"


class LabCertificate(models.Model):
    cert_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    lot = models.ForeignKey("lots.Lot", on_delete=models.CASCADE, related_name="lab_certificates", db_column="lot_id")
    lab_org = models.ForeignKey("organisations.Organisation", on_delete=models.CASCADE, related_name="issued_certificates", db_column="lab_org")
    lab_accreditation_no = models.TextField(null=True, blank=True)
    certificate_no = models.TextField()

    class Meta:
        db_table = "lab_certificate"
        unique_together = (("lab_org", "certificate_no"),)
