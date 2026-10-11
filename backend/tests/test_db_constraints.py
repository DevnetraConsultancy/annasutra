"""Tests verifying database constraints and triggers from db/schema.sql."""

import uuid

from django.db import IntegrityError, InternalError, connection
from django.utils import timezone
import pytest


@pytest.mark.django_db(transaction=True)
def test_trace_event_append_only_trigger():
    """Verify trace_event prevents UPDATE and DELETE via forbid_change trigger."""
    with connection.cursor() as cursor:
        # Create prerequisite organisation, user, product, lot
        org_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        product_id = str(uuid.uuid4())
        lot_id = str(uuid.uuid4())
        event_id = str(uuid.uuid4())

        cursor.execute(
            "INSERT INTO organisation (org_id, name, org_type) VALUES (%s, %s, %s)",
            [org_id, "Test Org", "FARMER"],
        )
        cursor.execute(
            "INSERT INTO app_user (user_id, org_id, phone_e164, role) VALUES (%s, %s, %s, %s)",
            [user_id, org_id, "+919876543210", "OWNER"],
        )
        cursor.execute(
            "INSERT INTO product (product_id, name, variety) VALUES (%s, %s, %s)",
            [product_id, "Tomato", "Roma"],
        )
        cursor.execute(
            "INSERT INTO lot (lot_id, public_code, product_id, created_by_org, lot_kind, state, custodian_org) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            [lot_id, "TESTCODE12345", product_id, org_id, "HARVEST", "CREATED", org_id],
        )

        # Insert a trace_event
        cursor.execute(
            "INSERT INTO trace_event (event_id, lot_id, lot_seq, event_type, event_time, org_id, user_id, payload, event_hash) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            [event_id, lot_id, 1, "HARVEST_CREATE", timezone.now(), org_id, user_id, "{}", b"dummyhash"],
        )

        # Attempt UPDATE -> must fail with exception from trigger
        with pytest.raises((IntegrityError, InternalError, Exception)) as exc_info:
            cursor.execute("UPDATE trace_event SET event_type = 'MUTATED' WHERE event_id = %s", [event_id])
        assert "append-only" in str(exc_info.value).lower()

        # Attempt DELETE -> must fail with exception from trigger
        with pytest.raises((IntegrityError, InternalError, Exception)) as exc_info:
            cursor.execute("DELETE FROM trace_event WHERE event_id = %s", [event_id])
        assert "append-only" in str(exc_info.value).lower()


@pytest.mark.django_db(transaction=True)
def test_one_open_handover_constraint():
    """Verify partial unique index permits only one open PENDING handover per lot."""
    with connection.cursor() as cursor:
        org_a = str(uuid.uuid4())
        org_b = str(uuid.uuid4())
        product_id = str(uuid.uuid4())
        lot_id = str(uuid.uuid4())

        cursor.execute("INSERT INTO organisation (org_id, name, org_type) VALUES (%s, %s, %s)", [org_a, "Org A", "FARMER"])
        cursor.execute("INSERT INTO organisation (org_id, name, org_type) VALUES (%s, %s, %s)", [org_b, "Org B", "AGGREGATOR"])
        cursor.execute("INSERT INTO product (product_id, name, variety) VALUES (%s, %s, %s)", [product_id, "Tomato", "Cherry"])
        cursor.execute(
            "INSERT INTO lot (lot_id, public_code, product_id, created_by_org, lot_kind, state, custodian_org) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            [lot_id, "TESTCODE54321", product_id, org_a, "HARVEST", "CREATED", org_a],
        )

        # First PENDING handover succeeds
        ho1 = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO handover (handover_id, lot_id, from_org, to_org, declared_qty_kg, state, expires_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            [ho1, lot_id, org_a, org_b, 100.0, "PENDING", timezone.now()],
        )

        # Second PENDING handover on same lot must violate one_open_handover
        ho2 = str(uuid.uuid4())
        with pytest.raises(IntegrityError):
            cursor.execute(
                "INSERT INTO handover (handover_id, lot_id, from_org, to_org, declared_qty_kg, state, expires_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                [ho2, lot_id, org_a, org_b, 50.0, "PENDING", timezone.now()],
            )


@pytest.mark.django_db(transaction=True)
def test_on_hand_nonnegative_constraint():
    """Verify check constraint on lot_balance prevents negative on-hand quantities."""
    with connection.cursor() as cursor:
        org_id = str(uuid.uuid4())
        product_id = str(uuid.uuid4())
        lot_id = str(uuid.uuid4())

        cursor.execute("INSERT INTO organisation (org_id, name, org_type) VALUES (%s, %s, %s)", [org_id, "Org Farm", "FARMER"])
        cursor.execute("INSERT INTO product (product_id, name, variety) VALUES (%s, %s, %s)", [product_id, "Tomato", "Beefsteak"])
        cursor.execute(
            "INSERT INTO lot (lot_id, public_code, product_id, created_by_org, lot_kind, state, custodian_org) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            [lot_id, "BALANCE-TEST-1", product_id, org_id, "HARVEST", "CREATED", org_id],
        )

        # Insert 100 kg in
        cursor.execute("INSERT INTO lot_balance (lot_id, qty_in_kg) VALUES (%s, %s)", [lot_id, 100.0])

        # Attempt to transfer 150 kg out (outputs > inputs + 0.001) -> must fail CHECK
        with pytest.raises(IntegrityError):
            cursor.execute("UPDATE lot_balance SET qty_out_transferred_kg = 150.0 WHERE lot_id = %s", [lot_id])
