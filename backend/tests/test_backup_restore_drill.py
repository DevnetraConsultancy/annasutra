"""Tests for disaster recovery and automated backup restore verification drill."""

import io
import uuid
from decimal import Decimal
import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.organisations.models import Organisation
from apps.lots.models import Lot, Product
from apps.inventory.models import LotBalance
from apps.ledger.models import TraceEvent
from apps.ledger.services.hash_chain import canonical_json_bytes, compute_event_hash


@pytest.fixture
def setup_lot_with_events(db):
    org = Organisation.objects.create(name="Drill Farm Org", org_type="FARMER", verification="VERIFIED")
    user = AppUser.objects.create(org=org, phone_e164="+919876540001", role="OWNER", status="ACTIVE")
    prod = Product.objects.create(name="Tomato", variety="Hybrid")

    lot = Lot.objects.create(
        public_code="DRILL-TOMATO-100",
        product=prod,
        created_by_org=org,
        custodian_org=org,
        lot_kind="HARVEST",
        state="IN_CUSTODY",
        head_seq=1,
    )
    LotBalance.objects.create(lot=lot, qty_in_kg=Decimal("100.000"))

    payload = {"label_serial": "DRILL-TOMATO-100", "net_qty_kg": 100.0}
    event_hash = compute_event_hash(None, "HARVEST_CREATE", 1, canonical_json_bytes(payload))

    event = TraceEvent.objects.create(
        event_id=uuid.uuid4(),
        lot=lot,
        lot_seq=1,
        event_type="HARVEST_CREATE",
        event_time=timezone.now().isoformat(),
        org=org,
        user=user,
        qty_kg=Decimal("100.000"),
        qty_basis="MEASURED",
        payload=payload,
        sync_status="ACCEPTED",
        event_hash=event_hash,
    )

    lot.head_hash = event_hash
    lot.save(update_fields=["head_hash"])

    return lot, event


@pytest.mark.django_db
def test_backup_restore_drill_passes_on_valid_ledger(setup_lot_with_events):
    """The backup and restore verification drill succeeds when ledger hash chains are intact."""
    out = io.StringIO()
    call_command("backup_restore_drill", stdout=out)
    output = out.getvalue()

    assert "Drill PASSED: 100% cryptographic integrity verified" in output


@pytest.mark.django_db
def test_backup_restore_drill_fails_on_corrupted_hash(setup_lot_with_events):
    """The drill detects tamper and fails if head_hash does not match the computed chain."""
    lot, _ = setup_lot_with_events
    lot.head_hash = b"corrupted_invalid_tampered_hash"
    lot.save(update_fields=["head_hash"])

    out = io.StringIO()
    with pytest.raises(SystemExit):
        call_command("backup_restore_drill", stdout=out)

    output = out.getvalue()
    assert "Head hash mismatch" in output
    assert "Drill FAILED" in output


@pytest.mark.django_db
def test_pilot_metrics_command_executes_successfully(setup_lot_with_events):
    """The pilot metrics command compiles aggregate lots, produce, and compliance metrics."""
    out = io.StringIO()
    call_command("pilot_metrics", stdout=out)
    output = out.getvalue()

    assert "AnnaSutra Pilot Operational Metrics" in output
    assert "Total Lots: 1" in output
    assert "Total Ingested / Harvested: 100.000 kg" in output
