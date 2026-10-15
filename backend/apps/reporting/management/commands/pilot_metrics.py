"""Django management command to generate pilot readiness & operational metrics."""

from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db.models import Sum, Count, Q

from apps.lots.models import Lot
from apps.inventory.models import LotBalance
from apps.custody.models import Handover
from apps.alerts.models import Alert, ScanLog
from apps.ledger.models import HashAnchor


class Command(BaseCommand):
    help = "Displays a summary of AnnaSutra pilot operational metrics."

    def handle(self, *args, **options):
        self.stdout.write("=== AnnaSutra Pilot Operational Metrics ===")

        # 1. Lots by state
        lot_counts = Lot.objects.aggregate(
            total=Count("lot_id"),
            in_custody=Count("lot_id", filter=Q(state="IN_CUSTODY")),
            in_transit=Count("lot_id", filter=Q(state="IN_TRANSIT")),
            closed=Count("lot_id", filter=Q(state="CLOSED")),
            recalled=Count("lot_id", filter=Q(state="RECALLED")),
            disputed=Count("lot_id", filter=Q(state="DISPUTED")),
        )

        self.stdout.write(f"Total Lots: {lot_counts['total']}")
        self.stdout.write(f" - In Custody: {lot_counts['in_custody']}")
        self.stdout.write(f" - In Transit: {lot_counts['in_transit']}")
        self.stdout.write(f" - Closed: {lot_counts['closed']}")
        self.stdout.write(f" - Recalled: {lot_counts['recalled']}")
        self.stdout.write(f" - Disputed: {lot_counts['disputed']}")

        # 2. Cumulative Mass Metrics
        balances = LotBalance.objects.aggregate(
            total_in=Sum("qty_in_kg"),
            total_out=Sum("qty_out_transferred_kg"),
            total_split=Sum("qty_split_out_kg"),
            total_waste=Sum("qty_waste_kg"),
            total_sold=Sum("qty_sold_kg"),
        )
        total_in = Decimal(str(balances['total_in'] or '0.000'))
        total_sold = Decimal(str(balances['total_sold'] or '0.000'))
        total_waste = Decimal(str(balances['total_waste'] or '0.000'))
        self.stdout.write(f" - Total Ingested / Harvested: {total_in:.3f} kg")
        self.stdout.write(f" - Retail Sold: {total_sold:.3f} kg")
        self.stdout.write(f" - Waste / Spoilage: {total_waste:.3f} kg")

        # 3. Handover Quality & Discrepancies
        handovers = Handover.objects.aggregate(
            total=Count("handover_id"),
            accepted=Count("handover_id", filter=Q(state="ACCEPTED")),
            with_discrepancy=Count(
                "handover_id", filter=Q(state="ACCEPTED_WITH_DISCREPANCY")
            ),
            disputed=Count("handover_id", filter=Q(state="DISPUTED")),
            expired=Count("handover_id", filter=Q(state="EXPIRED")),
        )
        self.stdout.write("\nHandover Operations:")
        self.stdout.write(f" - Total Handovers: {handovers['total']}")
        self.stdout.write(f" - Perfect Handovers: {handovers['accepted']}")
        self.stdout.write(f" - Tolerated Discrepancies: {handovers['with_discrepancy']}")
        self.stdout.write(f" - Disputed Handovers: {handovers['disputed']}")

        # 4. Security & Alert Triage
        alerts = Alert.objects.aggregate(
            total=Count("alert_id"),
            unresolved=Count("alert_id", filter=Q(status="OPEN")),
        )
        scan_logs = ScanLog.objects.count()
        anchors = HashAnchor.objects.count()

        self.stdout.write("\nAudit & Compliance:")
        self.stdout.write(f" - Total Public QR Scans: {scan_logs}")
        self.stdout.write(f" - Total Security Alerts: {alerts['total']} ({alerts['unresolved']} unresolved)")
        self.stdout.write(f" - Daily External Anchors: {anchors}")
        self.stdout.write("===========================================")
