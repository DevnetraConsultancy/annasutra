"""Genealogy and lot transformation services for AnnaSutra.

Implements Split, Merge, Sort, Repack, Waste, and Retail Sales
enforcing Single Write Path, append-only trace events, mass balance invariants,
and acyclic genealogy.
"""

import uuid
from decimal import Decimal
from django.db import connection, transaction
from django.utils import timezone
from rest_framework import exceptions

from apps.inventory.models import LotBalance
from apps.labels.models import QrBlock, QrLabel
from apps.ledger.models import TraceEvent
from apps.ledger.services.hash_chain import (
    canonical_json_bytes,
    compute_event_hash,
)
from apps.lots.models import Lot
from apps.publicview.services import refresh_public_view


def _check_genealogy_cycle(parent_lot_id: uuid.UUID, child_lot_id: uuid.UUID) -> None:
    """Ensures adding edge (parent_lot -> child_lot) does not introduce a cycle."""
    if parent_lot_id == child_lot_id:
        raise exceptions.ValidationError(
            {"detail": "Genealogy self-parent loop is forbidden.", "code": "CYCLIC_GENEALOGY"}
        )

    # Check if parent is already a descendant of child
    query = """
    WITH RECURSIVE descendants AS (
        SELECT child_lot FROM lot_edge WHERE parent_lot = %s
        UNION ALL
        SELECT e.child_lot
        FROM lot_edge e
        JOIN descendants d ON e.parent_lot = d.child_lot
    )
    SELECT 1 FROM descendants WHERE child_lot = %s LIMIT 1;
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [child_lot_id, parent_lot_id])
        if cursor.fetchone():
            raise exceptions.ValidationError(
                {"detail": "Genealogy cycle detected.", "code": "CYCLIC_GENEALOGY"}
            )


def split_lot(user, parent_lot_code: str, data: dict) -> dict:
    """Splits a parent lot into child lots with new QR labels."""
    event_id_str = data.get("event_id")
    if not event_id_str:
        raise exceptions.ValidationError({"detail": "event_id is required.", "code": "FIELD_REQUIRED"})
    try:
        event_id = uuid.UUID(str(event_id_str))
    except ValueError:
        raise exceptions.ValidationError({"detail": "Invalid event_id UUID.", "code": "INVALID_UUID"})

    user_org = user.org
    if not user_org or user_org.verification != "VERIFIED":
        raise exceptions.PermissionDenied(
            {"detail": "Organisation is not verified.", "code": "ORG_UNVERIFIED"}
        )

    # Idempotency check: if event already exists, return child lots
    existing_event = TraceEvent.objects.filter(event_id=event_id).first()
    if existing_event:
        child_edges = []
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT child_lot FROM lot_edge WHERE parent_lot = %s AND event_id = %s",
                [existing_event.lot_id, event_id],
            )
            child_edges = [row[0] for row in cursor.fetchall()]
        child_lots = Lot.objects.filter(lot_id__in=child_edges)
        items = []
        for cl in child_lots:
            bal = LotBalance.objects.filter(lot=cl).first()
            items.append({
                "lot_id": str(cl.lot_id),
                "public_code": cl.public_code,
                "state": cl.state,
                "custodian_org": str(cl.custodian_org_id),
                "pending_receiver_org": str(cl.pending_receiver_org_id) if cl.pending_receiver_org_id else None,
                "on_hand_kg": float(bal.qty_on_hand_kg) if bal else 0.0,
                "lot_seq": cl.head_seq,
            })
        return {"items": items, "next_cursor": None}

    children_data = data.get("children", [])
    if not children_data or not isinstance(children_data, list):
        raise exceptions.ValidationError({"detail": "children array is required.", "code": "FIELD_REQUIRED"})

    total_split_qty = Decimal("0")
    parsed_children = []
    for item in children_data:
        serial = item.get("label_serial")
        if not serial:
            raise exceptions.ValidationError({"detail": "label_serial is required for each child.", "code": "FIELD_REQUIRED"})
        try:
            qty = Decimal(str(item.get("qty_kg", "0")))
        except Exception:
            raise exceptions.ValidationError({"detail": "Invalid child qty_kg.", "code": "INVALID_QTY"})
        if qty <= 0:
            raise exceptions.ValidationError({"detail": "Child quantity must be positive.", "code": "INVALID_QTY"})
        total_split_qty += qty
        parsed_children.append({"label_serial": serial, "qty_kg": qty})

    event_time_str = data.get("event_time", timezone.now().isoformat())
    device_sig = data.get("device_signature")
    sig_bytes = str(device_sig).encode("utf-8") if device_sig else None

    with transaction.atomic():
        parent_lot = Lot.objects.select_for_update().filter(public_code=parent_lot_code).first()
        if not parent_lot:
            raise exceptions.NotFound({"detail": "Parent lot not found.", "code": "NOT_FOUND"})

        if parent_lot.custodian_org_id != user_org.org_id:
            raise exceptions.PermissionDenied(
                {"detail": "Only current custodian can split this lot.", "code": "NOT_CUSTODIAN"}
            )

        if parent_lot.state not in ["CREATED", "IN_CUSTODY"]:
            raise exceptions.ValidationError(
                {"detail": f"Cannot split lot in state {parent_lot.state}.", "code": "INVALID_STATE"}
            )

        parent_balance = LotBalance.objects.select_for_update().filter(lot=parent_lot).first()
        if not parent_balance:
            raise exceptions.ValidationError({"detail": "Parent balance not found.", "code": "BALANCE_NOT_FOUND"})

        # Invariant 2: Sum of split children plus remainder <= parent on-hand
        if parent_balance.qty_on_hand_kg < total_split_qty:
            raise exceptions.ValidationError(
                {
                    "detail": f"Split outputs ({total_split_qty} kg) exceed parent on-hand ({parent_balance.qty_on_hand_kg} kg).",
                    "code": "INSUFFICIENT_STOCK",
                }
            )

        # Verify child QR labels
        qr_labels = {}
        for child_item in parsed_children:
            serial = child_item["label_serial"]
            qr_label = QrLabel.objects.select_for_update().filter(serial=serial).first()
            if not qr_label:
                block = QrBlock.objects.create(
                    block_id=uuid.uuid4(),
                    issued_to_org=user_org,
                    issued_by=user,
                    count=1,
                )
                qr_label = QrLabel.objects.create(
                    serial=serial,
                    block=block,
                    issued_to_org=user_org,
                    status="ISSUED",
                )
            if qr_label.lot_id or qr_label.status == "BOUND":
                raise exceptions.Conflict(
                    {"detail": f"QR label {serial} is already bound to a lot.", "code": "LABEL_ALREADY_USED"}
                )
            qr_labels[serial] = qr_label

        # 1. Update parent balance
        parent_balance.qty_split_out_kg += total_split_qty
        parent_balance.save(update_fields=["qty_split_out_kg"])

        # 2. Append parent SPLIT event
        parent_seq = parent_lot.head_seq + 1
        payload = {
            "children": [
                {"label_serial": c["label_serial"], "qty_kg": str(c["qty_kg"])}
                for c in parsed_children
            ],
            "total_split_qty_kg": str(total_split_qty),
        }
        prev_hash = bytes(parent_lot.head_hash) if parent_lot.head_hash else None
        event_hash = compute_event_hash(
            prev_hash,
            "SPLIT",
            parent_seq,
            canonical_json_bytes(payload),
        )

        TraceEvent.objects.create(
            event_id=event_id,
            lot=parent_lot,
            lot_seq=parent_seq,
            event_type="SPLIT",
            event_time=event_time_str,
            org=user_org,
            user=user,
            qty_kg=total_split_qty,
            qty_basis="MEASURED",
            payload=payload,
            sync_status="ACCEPTED",
            device_signature=sig_bytes,
            prev_hash=prev_hash,
            event_hash=event_hash,
        )

        parent_lot.head_seq = parent_seq
        parent_lot.head_hash = event_hash
        if parent_balance.qty_on_hand_kg <= Decimal("0.001"):
            parent_lot.state = "CLOSED"
        parent_lot.save(update_fields=["head_seq", "head_hash", "state"])
        refresh_public_view(parent_lot)

        # 3. Create child lots and edges
        child_items = []
        for child_item in parsed_children:
            serial = child_item["label_serial"]
            child_qty = child_item["qty_kg"]
            child_lot_id = uuid.uuid4()

            _check_genealogy_cycle(parent_lot.lot_id, child_lot_id)

            child_lot = Lot.objects.create(
                lot_id=child_lot_id,
                public_code=serial,
                product=parent_lot.product,
                origin_plot=parent_lot.origin_plot,
                created_by_org=user_org,
                lot_kind="SPLIT_CHILD",
                state="IN_CUSTODY",
                custodian_org=user_org,
                head_seq=1,
            )

            qr_label = qr_labels[serial]
            qr_label.lot = child_lot
            qr_label.status = "BOUND"
            qr_label.bound_at = timezone.now()
            qr_label.save(update_fields=["lot", "status", "bound_at"])

            child_balance = LotBalance.objects.create(
                lot=child_lot,
                qty_in_kg=child_qty,
            )

            # Insert lot_edge
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO lot_edge (parent_lot, child_lot, qty_kg, event_id) VALUES (%s, %s, %s, %s)",
                    [parent_lot.lot_id, child_lot.lot_id, child_qty, event_id],
                )

            # Child initial trace event
            child_payload = {
                "parent_lot_code": parent_lot.public_code,
                "label_serial": serial,
                "qty_kg": str(child_qty),
            }
            child_event_hash = compute_event_hash(
                None,
                "SPLIT_CHILD",
                1,
                canonical_json_bytes(child_payload),
            )
            TraceEvent.objects.create(
                event_id=uuid.uuid4(),
                lot=child_lot,
                lot_seq=1,
                event_type="SPLIT_CHILD",
                event_time=event_time_str,
                org=user_org,
                user=user,
                qty_kg=child_qty,
                qty_basis="MEASURED",
                payload=child_payload,
                sync_status="ACCEPTED",
                event_hash=child_event_hash,
            )
            child_lot.head_hash = child_event_hash
            child_lot.save(update_fields=["head_hash"])
            refresh_public_view(child_lot)

            child_items.append({
                "lot_id": str(child_lot.lot_id),
                "public_code": child_lot.public_code,
                "state": child_lot.state,
                "custodian_org": str(child_lot.custodian_org_id),
                "pending_receiver_org": None,
                "on_hand_kg": float(child_balance.qty_on_hand_kg),
                "lot_seq": 1,
            })

    return {"items": child_items, "next_cursor": None}


def merge_lots(user, data: dict) -> dict:
    """Merges multiple parent lots into a single new lot."""
    event_id_str = data.get("event_id")
    if not event_id_str:
        raise exceptions.ValidationError({"detail": "event_id is required.", "code": "FIELD_REQUIRED"})
    try:
        event_id = uuid.UUID(str(event_id_str))
    except ValueError:
        raise exceptions.ValidationError({"detail": "Invalid event_id UUID.", "code": "INVALID_UUID"})

    user_org = user.org
    if not user_org or user_org.verification != "VERIFIED":
        raise exceptions.PermissionDenied(
            {"detail": "Organisation is not verified.", "code": "ORG_UNVERIFIED"}
        )

    # Idempotency check: if event exists, return the merged child lot
    existing_event = TraceEvent.objects.filter(event_id=event_id).first()
    if existing_event:
        merged_lot = existing_event.lot
        bal = LotBalance.objects.filter(lot=merged_lot).first()
        return {
            "lot_id": str(merged_lot.lot_id),
            "public_code": merged_lot.public_code,
            "state": merged_lot.state,
            "custodian_org": str(merged_lot.custodian_org_id),
            "pending_receiver_org": str(merged_lot.pending_receiver_org_id) if merged_lot.pending_receiver_org_id else None,
            "on_hand_kg": float(bal.qty_on_hand_kg) if bal else 0.0,
            "lot_seq": merged_lot.head_seq,
        }

    input_codes = data.get("input_lot_codes", [])
    if not input_codes or len(input_codes) < 2:
        raise exceptions.ValidationError(
            {"detail": "At least 2 input lots are required to merge.", "code": "FIELD_REQUIRED"}
        )

    output_serial = data.get("label_serial")
    if not output_serial:
        raise exceptions.ValidationError({"detail": "label_serial is required for merged lot.", "code": "FIELD_REQUIRED"})

    event_time_str = data.get("event_time", timezone.now().isoformat())
    device_sig = data.get("device_signature")
    sig_bytes = str(device_sig).encode("utf-8") if device_sig else None

    with transaction.atomic():
        parent_lots = list(Lot.objects.select_for_update().filter(public_code__in=input_codes))
        if len(parent_lots) != len(input_codes):
            raise exceptions.NotFound({"detail": "One or more input lots not found.", "code": "NOT_FOUND"})

        first_product_id = parent_lots[0].product_id
        for p in parent_lots:
            if p.custodian_org_id != user_org.org_id:
                raise exceptions.PermissionDenied(
                    {"detail": f"Not custodian of input lot {p.public_code}.", "code": "NOT_CUSTODIAN"}
                )
            if p.product_id != first_product_id:
                raise exceptions.ValidationError(
                    {"detail": "All merged lots must be the same product.", "code": "PRODUCT_MISMATCH"}
                )
            if p.state not in ["CREATED", "IN_CUSTODY"]:
                raise exceptions.ValidationError(
                    {"detail": f"Cannot merge lot in state {p.state}.", "code": "INVALID_STATE"}
                )

        # Check output label
        qr_label = QrLabel.objects.select_for_update().filter(serial=output_serial).first()
        if not qr_label:
            block = QrBlock.objects.create(
                block_id=uuid.uuid4(),
                issued_to_org=user_org,
                issued_by=user,
                count=1,
            )
            qr_label = QrLabel.objects.create(
                serial=output_serial,
                block=block,
                issued_to_org=user_org,
                status="ISSUED",
            )
        if qr_label.lot_id or qr_label.status == "BOUND":
            raise exceptions.Conflict(
                {"detail": f"QR label {output_serial} is already bound.", "code": "LABEL_ALREADY_USED"}
            )

        merged_lot_id = uuid.uuid4()
        total_merged_qty = Decimal("0")

        # 1. Deduct inputs and create lot_edges
        for p in parent_lots:
            _check_genealogy_cycle(p.lot_id, merged_lot_id)
            bal = LotBalance.objects.select_for_update().filter(lot=p).first()
            if not bal or bal.qty_on_hand_kg <= 0:
                raise exceptions.ValidationError(
                    {"detail": f"Lot {p.public_code} has zero on-hand quantity.", "code": "INSUFFICIENT_STOCK"}
                )
            input_qty = bal.qty_on_hand_kg
            total_merged_qty += input_qty

            bal.qty_split_out_kg += input_qty
            bal.save(update_fields=["qty_split_out_kg"])

            p_seq = p.head_seq + 1
            p_payload = {"merged_into_serial": output_serial, "qty_kg": str(input_qty)}
            p_prev = bytes(p.head_hash) if p.head_hash else None
            p_hash = compute_event_hash(p_prev, "MERGE", p_seq, canonical_json_bytes(p_payload))

            TraceEvent.objects.create(
                event_id=uuid.uuid4(),
                lot=p,
                lot_seq=p_seq,
                event_type="MERGE",
                event_time=event_time_str,
                org=user_org,
                user=user,
                qty_kg=input_qty,
                qty_basis="MEASURED",
                payload=p_payload,
                sync_status="ACCEPTED",
                prev_hash=p_prev,
                event_hash=p_hash,
            )
            p.head_seq = p_seq
            p.head_hash = p_hash
            p.state = "CLOSED"
            p.save(update_fields=["head_seq", "head_hash", "state"])
            refresh_public_view(p)

            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO lot_edge (parent_lot, child_lot, qty_kg, event_id) VALUES (%s, %s, %s, %s)",
                    [p.lot_id, merged_lot_id, input_qty, event_id],
                )

        # 2. Create merged lot
        merged_lot = Lot.objects.create(
            lot_id=merged_lot_id,
            public_code=output_serial,
            product=parent_lots[0].product,
            origin_plot=None,
            created_by_org=user_org,
            lot_kind="MERGED",
            state="IN_CUSTODY",
            custodian_org=user_org,
            head_seq=1,
        )

        qr_label.lot = merged_lot
        qr_label.status = "BOUND"
        qr_label.bound_at = timezone.now()
        qr_label.save(update_fields=["lot", "status", "bound_at"])

        merged_balance = LotBalance.objects.create(
            lot=merged_lot,
            qty_in_kg=total_merged_qty,
        )

        m_payload = {
            "input_lot_codes": input_codes,
            "total_merged_qty_kg": str(total_merged_qty),
        }
        m_hash = compute_event_hash(None, "MERGE", 1, canonical_json_bytes(m_payload))

        TraceEvent.objects.create(
            event_id=event_id,
            lot=merged_lot,
            lot_seq=1,
            event_type="MERGE",
            event_time=event_time_str,
            org=user_org,
            user=user,
            qty_kg=total_merged_qty,
            qty_basis="MEASURED",
            payload=m_payload,
            sync_status="ACCEPTED",
            device_signature=sig_bytes,
            event_hash=m_hash,
        )

        merged_lot.head_hash = m_hash
        merged_lot.save(update_fields=["head_hash"])
        refresh_public_view(merged_lot)

    return {
        "lot_id": str(merged_lot.lot_id),
        "public_code": merged_lot.public_code,
        "state": merged_lot.state,
        "custodian_org": str(merged_lot.custodian_org_id),
        "pending_receiver_org": None,
        "on_hand_kg": float(merged_balance.qty_on_hand_kg),
        "lot_seq": 1,
    }


def sort_lot(user, lot_code: str, data: dict) -> dict:
    """Sorts or grades produce. Validates mass balance."""
    event_id_str = data.get("event_id")
    if not event_id_str:
        raise exceptions.ValidationError({"detail": "event_id is required.", "code": "FIELD_REQUIRED"})
    try:
        event_id = uuid.UUID(str(event_id_str))
    except ValueError:
        raise exceptions.ValidationError({"detail": "Invalid event_id UUID.", "code": "INVALID_UUID"})

    user_org = user.org
    if not user_org or user_org.verification != "VERIFIED":
        raise exceptions.PermissionDenied(
            {"detail": "Organisation is not verified.", "code": "ORG_UNVERIFIED"}
        )

    # Idempotency check
    existing_event = TraceEvent.objects.filter(event_id=event_id).first()
    if existing_event:
        lot = existing_event.lot
        bal = LotBalance.objects.filter(lot=lot).first()
        return {
            "items": [{
                "lot_id": str(lot.lot_id),
                "public_code": lot.public_code,
                "state": lot.state,
                "custodian_org": str(lot.custodian_org_id),
                "pending_receiver_org": str(lot.pending_receiver_org_id) if lot.pending_receiver_org_id else None,
                "on_hand_kg": float(bal.qty_on_hand_kg) if bal else 0.0,
                "lot_seq": lot.head_seq,
            }],
            "next_cursor": None,
        }

    outputs = data.get("outputs", [])
    if not outputs or not isinstance(outputs, list):
        raise exceptions.ValidationError({"detail": "outputs array is required.", "code": "FIELD_REQUIRED"})

    total_output = Decimal("0")
    total_waste = Decimal("0")
    total_rejected = Decimal("0")
    for out in outputs:
        try:
            qty = Decimal(str(out.get("qty_kg", "0")))
        except Exception:
            raise exceptions.ValidationError({"detail": "Invalid output qty_kg.", "code": "INVALID_QTY"})
        if qty < 0:
            raise exceptions.ValidationError({"detail": "Output qty must be non-negative.", "code": "INVALID_QTY"})
        total_output += qty
        grade = str(out.get("grade", "")).upper()
        if "WASTE" in grade or "SPOIL" in grade:
            total_waste += qty
        elif "REJECT" in grade:
            total_rejected += qty

    event_time_str = data.get("event_time", timezone.now().isoformat())

    with transaction.atomic():
        lot = Lot.objects.select_for_update().filter(public_code=lot_code).first()
        if not lot:
            raise exceptions.NotFound({"detail": "Lot not found.", "code": "NOT_FOUND"})

        if lot.custodian_org_id != user_org.org_id:
            raise exceptions.PermissionDenied(
                {"detail": "Only custodian can sort this lot.", "code": "NOT_CUSTODIAN"}
            )

        balance = LotBalance.objects.select_for_update().filter(lot=lot).first()
        if not balance:
            raise exceptions.ValidationError({"detail": "Lot balance not found.", "code": "BALANCE_NOT_FOUND"})

        # Mass balance invariant: outputs cannot exceed current on-hand
        if total_output > balance.qty_on_hand_kg + Decimal("0.001"):
            raise exceptions.ValidationError(
                {
                    "detail": f"Sorted outputs ({total_output} kg) exceed on-hand ({balance.qty_on_hand_kg} kg).",
                    "code": "MASS_BALANCE_VIOLATION",
                }
            )

        if total_waste > 0:
            balance.qty_waste_kg += total_waste
        if total_rejected > 0:
            balance.qty_rejected_kg += total_rejected
        balance.save()

        lot_seq = lot.head_seq + 1
        payload = {"outputs": [{"grade": o.get("grade"), "qty_kg": str(o.get("qty_kg"))} for o in outputs]}
        prev_hash = bytes(lot.head_hash) if lot.head_hash else None
        event_hash = compute_event_hash(prev_hash, "SORT_GRADE", lot_seq, canonical_json_bytes(payload))

        TraceEvent.objects.create(
            event_id=event_id,
            lot=lot,
            lot_seq=lot_seq,
            event_type="SORT_GRADE",
            event_time=event_time_str,
            org=user_org,
            user=user,
            qty_kg=total_output,
            qty_basis="MEASURED",
            payload=payload,
            sync_status="ACCEPTED",
            prev_hash=prev_hash,
            event_hash=event_hash,
        )

        lot.head_seq = lot_seq
        lot.head_hash = event_hash
        lot.save(update_fields=["head_seq", "head_hash"])
        refresh_public_view(lot)

    return {
        "items": [{
            "lot_id": str(lot.lot_id),
            "public_code": lot.public_code,
            "state": lot.state,
            "custodian_org": str(lot.custodian_org_id),
            "pending_receiver_org": None,
            "on_hand_kg": float(balance.qty_on_hand_kg),
            "lot_seq": lot_seq,
        }],
        "next_cursor": None,
    }


def repack_lot(user, lot_code: str, data: dict) -> dict:
    """Repacks container for the same lot."""
    event_id_str = data.get("event_id")
    if not event_id_str:
        raise exceptions.ValidationError({"detail": "event_id is required.", "code": "FIELD_REQUIRED"})
    try:
        event_id = uuid.UUID(str(event_id_str))
    except ValueError:
        raise exceptions.ValidationError({"detail": "Invalid event_id UUID.", "code": "INVALID_UUID"})

    user_org = user.org
    if not user_org or user_org.verification != "VERIFIED":
        raise exceptions.PermissionDenied(
            {"detail": "Organisation is not verified.", "code": "ORG_UNVERIFIED"}
        )

    existing_event = TraceEvent.objects.filter(event_id=event_id).first()
    if existing_event:
        return {"event_id": str(event_id), "status": "ACCEPTED", "lot_seq": existing_event.lot_seq}

    crates = data.get("crates")
    note = data.get("note")
    event_time_str = data.get("event_time", timezone.now().isoformat())

    with transaction.atomic():
        lot = Lot.objects.select_for_update().filter(public_code=lot_code).first()
        if not lot:
            raise exceptions.NotFound({"detail": "Lot not found.", "code": "NOT_FOUND"})

        if lot.custodian_org_id != user_org.org_id:
            raise exceptions.PermissionDenied(
                {"detail": "Only custodian can repack this lot.", "code": "NOT_CUSTODIAN"}
            )

        lot_seq = lot.head_seq + 1
        payload = {"crates": crates, "note": note}
        prev_hash = bytes(lot.head_hash) if lot.head_hash else None
        event_hash = compute_event_hash(prev_hash, "REPACK", lot_seq, canonical_json_bytes(payload))

        TraceEvent.objects.create(
            event_id=event_id,
            lot=lot,
            lot_seq=lot_seq,
            event_type="REPACK",
            event_time=event_time_str,
            org=user_org,
            user=user,
            payload=payload,
            sync_status="ACCEPTED",
            prev_hash=prev_hash,
            event_hash=event_hash,
        )

        lot.head_seq = lot_seq
        lot.head_hash = event_hash
        lot.save(update_fields=["head_seq", "head_hash"])
        refresh_public_view(lot)

    return {"event_id": str(event_id), "status": "ACCEPTED", "lot_seq": lot_seq}


def record_waste(user, lot_code: str, data: dict) -> dict:
    """Records waste or spoilage for a lot."""
    event_id_str = data.get("event_id")
    if not event_id_str:
        raise exceptions.ValidationError({"detail": "event_id is required.", "code": "FIELD_REQUIRED"})
    try:
        event_id = uuid.UUID(str(event_id_str))
    except ValueError:
        raise exceptions.ValidationError({"detail": "Invalid event_id UUID.", "code": "INVALID_UUID"})

    user_org = user.org
    if not user_org or user_org.verification != "VERIFIED":
        raise exceptions.PermissionDenied(
            {"detail": "Organisation is not verified.", "code": "ORG_UNVERIFIED"}
        )

    existing_event = TraceEvent.objects.filter(event_id=event_id).first()
    if existing_event:
        return {"event_id": str(event_id), "status": "ACCEPTED", "lot_seq": existing_event.lot_seq}

    try:
        qty_kg = Decimal(str(data.get("qty_kg", "0")))
    except Exception:
        raise exceptions.ValidationError({"detail": "Invalid qty_kg.", "code": "INVALID_QTY"})

    if qty_kg <= 0:
        raise exceptions.ValidationError({"detail": "Waste quantity must be positive.", "code": "INVALID_QTY"})

    reason_code = data.get("reason_code")
    if not reason_code:
        raise exceptions.ValidationError({"detail": "reason_code is mandatory for waste.", "code": "FIELD_REQUIRED"})

    evidence_ids = data.get("evidence_ids", [])
    event_time_str = data.get("event_time", timezone.now().isoformat())

    with transaction.atomic():
        lot = Lot.objects.select_for_update().filter(public_code=lot_code).first()
        if not lot:
            raise exceptions.NotFound({"detail": "Lot not found.", "code": "NOT_FOUND"})

        if lot.custodian_org_id != user_org.org_id:
            raise exceptions.PermissionDenied(
                {"detail": "Only custodian can record waste.", "code": "NOT_CUSTODIAN"}
            )

        balance = LotBalance.objects.select_for_update().filter(lot=lot).first()
        if not balance:
            raise exceptions.ValidationError({"detail": "Lot balance not found.", "code": "BALANCE_NOT_FOUND"})

        if qty_kg > balance.qty_on_hand_kg:
            raise exceptions.ValidationError(
                {
                    "detail": f"Waste ({qty_kg} kg) exceeds on-hand ({balance.qty_on_hand_kg} kg).",
                    "code": "INSUFFICIENT_STOCK",
                }
            )

        balance.qty_waste_kg += qty_kg
        balance.save(update_fields=["qty_waste_kg"])

        lot_seq = lot.head_seq + 1
        payload = {
            "waste_qty_kg": str(qty_kg),
            "reason_code": reason_code,
            "evidence_ids": [str(eid) for eid in evidence_ids],
        }
        prev_hash = bytes(lot.head_hash) if lot.head_hash else None
        event_hash = compute_event_hash(prev_hash, "WASTE", lot_seq, canonical_json_bytes(payload))

        TraceEvent.objects.create(
            event_id=event_id,
            lot=lot,
            lot_seq=lot_seq,
            event_type="WASTE",
            event_time=event_time_str,
            org=user_org,
            user=user,
            qty_kg=qty_kg,
            qty_basis="MEASURED",
            payload=payload,
            sync_status="ACCEPTED",
            prev_hash=prev_hash,
            event_hash=event_hash,
        )

        lot.head_seq = lot_seq
        lot.head_hash = event_hash
        lot.save(update_fields=["head_seq", "head_hash"])
        refresh_public_view(lot)

    return {"event_id": str(event_id), "status": "ACCEPTED", "lot_seq": lot_seq}


def record_sale(user, lot_code: str, data: dict) -> dict:
    """Records retail sale. Never records customer personal information."""
    event_id_str = data.get("event_id")
    if not event_id_str:
        raise exceptions.ValidationError({"detail": "event_id is required.", "code": "FIELD_REQUIRED"})
    try:
        event_id = uuid.UUID(str(event_id_str))
    except ValueError:
        raise exceptions.ValidationError({"detail": "Invalid event_id UUID.", "code": "INVALID_UUID"})

    user_org = user.org
    if not user_org or user_org.verification != "VERIFIED":
        raise exceptions.PermissionDenied(
            {"detail": "Organisation is not verified.", "code": "ORG_UNVERIFIED"}
        )

    existing_event = TraceEvent.objects.filter(event_id=event_id).first()
    if existing_event:
        return {"event_id": str(event_id), "status": "ACCEPTED", "lot_seq": existing_event.lot_seq}

    try:
        qty_kg = Decimal(str(data.get("qty_kg", "0")))
    except Exception:
        raise exceptions.ValidationError({"detail": "Invalid qty_kg.", "code": "INVALID_QTY"})

    if qty_kg <= 0:
        raise exceptions.ValidationError({"detail": "Sale quantity must be positive.", "code": "INVALID_QTY"})

    event_time_str = data.get("event_time", timezone.now().isoformat())

    with transaction.atomic():
        lot = Lot.objects.select_for_update().filter(public_code=lot_code).first()
        if not lot:
            raise exceptions.NotFound({"detail": "Lot not found.", "code": "NOT_FOUND"})

        if lot.custodian_org_id != user_org.org_id:
            raise exceptions.PermissionDenied(
                {"detail": "Only custodian can record sale.", "code": "NOT_CUSTODIAN"}
            )

        balance = LotBalance.objects.select_for_update().filter(lot=lot).first()
        if not balance:
            raise exceptions.ValidationError({"detail": "Lot balance not found.", "code": "BALANCE_NOT_FOUND"})

        if qty_kg > balance.qty_on_hand_kg:
            raise exceptions.ValidationError(
                {
                    "detail": f"Sale ({qty_kg} kg) exceeds on-hand ({balance.qty_on_hand_kg} kg).",
                    "code": "INSUFFICIENT_STOCK",
                }
            )

        balance.qty_sold_kg += qty_kg
        balance.save(update_fields=["qty_sold_kg"])

        lot_seq = lot.head_seq + 1
        payload = {
            "sold_qty_kg": str(qty_kg),
            "channel": "RETAIL",
        }
        prev_hash = bytes(lot.head_hash) if lot.head_hash else None
        event_hash = compute_event_hash(prev_hash, "SELL_RETAIL", lot_seq, canonical_json_bytes(payload))

        TraceEvent.objects.create(
            event_id=event_id,
            lot=lot,
            lot_seq=lot_seq,
            event_type="SELL_RETAIL",
            event_time=event_time_str,
            org=user_org,
            user=user,
            qty_kg=qty_kg,
            qty_basis="MEASURED",
            payload=payload,
            sync_status="ACCEPTED",
            prev_hash=prev_hash,
            event_hash=event_hash,
        )

        lot.head_seq = lot_seq
        lot.head_hash = event_hash
        lot.save(update_fields=["head_seq", "head_hash"])
        refresh_public_view(lot)

    return {"event_id": str(event_id), "status": "ACCEPTED", "lot_seq": lot_seq}
