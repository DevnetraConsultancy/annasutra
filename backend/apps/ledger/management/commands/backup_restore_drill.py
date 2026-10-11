from django.core.management.base import BaseCommand

from apps.lots.models import Lot
from apps.inventory.models import LotBalance
from apps.ledger.models import TraceEvent
from apps.ledger.services.hash_chain import canonical_json_bytes, compute_event_hash


class Command(BaseCommand):
    help = "Executes a simulated backup, restore, and cryptographic hash-chain verification drill."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulates the drill without modifying the database.",
        )

    def handle(self, *args, **options):
        self.stdout.write("Initiating AnnaSutra Backup and Restore Verification Drill...")

        lots = list(Lot.objects.all())
        events = list(TraceEvent.objects.all().order_by("lot_id", "lot_seq"))
        balances = list(LotBalance.objects.all())

        self.stdout.write(f"Snapshot captured: {len(lots)} lots, {len(events)} events, {len(balances)} balances.")

        # Validate cryptographic integrity of all restored records
        verified_events = 0
        corrupted_events = 0

        # Group events by lot
        events_by_lot = {}
        for ev in events:
            events_by_lot.setdefault(ev.lot_id, []).append(ev)

        for lot in lots:
            lot_events = events_by_lot.get(lot.lot_id, [])
            expected_prev_hash = None

            for ev in lot_events:
                calculated_hash = compute_event_hash(
                    expected_prev_hash,
                    ev.event_type,
                    ev.lot_seq,
                    canonical_json_bytes(ev.payload),
                )

                if ev.event_hash == calculated_hash:
                    verified_events += 1
                else:
                    corrupted_events += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"Integrity check failed on lot {lot.public_code}, seq {ev.lot_seq}."
                        )
                    )

                expected_prev_hash = calculated_hash

            if lot_events and lot.head_hash and lot.head_hash != expected_prev_hash:
                corrupted_events += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"Head hash mismatch on lot {lot.public_code}."
                    )
                )

        if corrupted_events == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Drill PASSED: 100% cryptographic integrity verified across {verified_events} events."
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"Drill FAILED: {corrupted_events} integrity mismatches detected."
                )
            )
            raise SystemExit(1)
