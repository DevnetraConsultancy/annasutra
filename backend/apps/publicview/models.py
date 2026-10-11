from django.db import models


class PublicView(models.Model):
    lot = models.OneToOneField("lots.Lot", primary_key=True, on_delete=models.CASCADE, related_name="public_view", db_column="lot_id")
    public_code = models.TextField(unique=True)
    payload = models.JSONField(default=dict)
    refreshed_at = models.DateTimeField()

    class Meta:
        db_table = "public_view"
