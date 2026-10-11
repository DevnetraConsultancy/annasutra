import uuid
from django.db import models
from django.utils import timezone


class Product(models.Model):
    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    variety = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "product"
        unique_together = (("name", "variety"),)


class Lot(models.Model):
    LOT_KIND_CHOICES = [
        ("HARVEST", "Harvest"),
        ("SPLIT_CHILD", "Split Child"),
        ("MERGED", "Merged"),
        ("SORTED", "Sorted"),
    ]
    STATE_CHOICES = [
        ("CREATED", "Created"),
        ("IN_TRANSIT", "In Transit"),
        ("IN_CUSTODY", "In Custody"),
        ("DISPUTED", "Disputed"),
        ("CLOSED", "Closed"),
        ("RECALLED", "Recalled"),
    ]

    lot_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    public_code = models.TextField(unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="lots", db_column="product_id")
    origin_plot = models.ForeignKey("organisations.Plot", null=True, blank=True, on_delete=models.SET_NULL, related_name="lots", db_column="origin_plot_id")
    created_by_org = models.ForeignKey("organisations.Organisation", on_delete=models.CASCADE, related_name="created_lots", db_column="created_by_org")
    lot_kind = models.TextField(choices=LOT_KIND_CHOICES)
    state = models.TextField(choices=STATE_CHOICES)
    custodian_org = models.ForeignKey("organisations.Organisation", on_delete=models.CASCADE, related_name="custody_lots", db_column="custodian_org")
    pending_receiver_org = models.ForeignKey("organisations.Organisation", null=True, blank=True, on_delete=models.SET_NULL, related_name="pending_receipt_lots", db_column="pending_receiver_org")
    version = models.BigIntegerField(default=0)
    head_seq = models.BigIntegerField(default=0)
    head_hash = models.BinaryField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "lot"


class LotEdge(models.Model):
    parent_lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name="child_edges", db_column="parent_lot", primary_key=True)
    child_lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name="parent_edges", db_column="child_lot")
    qty_kg = models.DecimalField(max_digits=12, decimal_places=3)
    event_id = models.UUIDField()

    class Meta:
        db_table = "lot_edge"
        unique_together = (("parent_lot", "child_lot"),)
