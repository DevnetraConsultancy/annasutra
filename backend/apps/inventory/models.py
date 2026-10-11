from django.db import models


class LotBalance(models.Model):
    lot = models.OneToOneField("lots.Lot", primary_key=True, on_delete=models.CASCADE, related_name="balance", db_column="lot_id")
    qty_in_kg = models.DecimalField(max_digits=12, decimal_places=3)
    qty_out_transferred_kg = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    qty_split_out_kg = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    qty_rejected_kg = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    qty_waste_kg = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    qty_sold_kg = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    qty_variance_kg = models.DecimalField(max_digits=12, decimal_places=3, default=0)

    class Meta:
        db_table = "lot_balance"

    @property
    def qty_on_hand_kg(self):
        return (
            self.qty_in_kg
            - (self.qty_out_transferred_kg or 0)
            - (self.qty_split_out_kg or 0)
            - (self.qty_rejected_kg or 0)
            - (self.qty_waste_kg or 0)
            - (self.qty_sold_kg or 0)
            - (self.qty_variance_kg or 0)
        )
