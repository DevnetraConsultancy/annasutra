"""Django management command to run daily hash verification and anchoring."""
import datetime
from django.core.management.base import BaseCommand
from apps.ledger.services.anchor_service import run_daily_anchoring


class Command(BaseCommand):
    help = "Re-verifies per-lot hash chains and computes the daily Merkle root anchor."

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=str,
            help="Anchor date in YYYY-MM-DD format (defaults to today).",
        )
        parser.add_argument(
            "--location",
            type=str,
            default="s3://annasutra-anchors/daily/",
            help="External write-once anchor location URI.",
        )

    def handle(self, *args, **options):
        date_str = options.get("date")
        if date_str:
            target_date = datetime.date.fromisoformat(date_str)
        else:
            target_date = None

        location = options.get("location")
        self.stdout.write(f"Starting daily anchor verification for date: {target_date or 'today'}...")

        root_hash, verified_count, corrupted_count = run_daily_anchoring(
            anchor_date=target_date,
            location=location,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Completed: verified {verified_count} lots, found {corrupted_count} corrupted lots. "
                f"Merkle root: {root_hash.hex()}"
            )
        )
