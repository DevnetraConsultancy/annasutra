"""Recall management and recursive genealogy forward trace services for AnnaSutra."""

import uuid
from django.db import connection, transaction
from django.utils import timezone
from rest_framework import exceptions

from apps.ledger.models import TraceEvent
from apps.ledger.services.hash_chain import (
    canonical_json_bytes,
    compute_event_hash,
)
from apps.lots.models import Lot
from apps.publicview.services import refresh_public_view
from apps.reporting.models import Recall


def to_db_uuid(val):
    if val is None:
        return None
    if not connection.features.has_native_uuid_field:
        if hasattr(val, "hex"):
            return val.hex
        return str(val).replace("-", "")
    return val


def open_recall(user, data: dict) -> dict:
    """Opens a product recall on a root lot and marks it RECALLED."""
    lot_code = data.get("lot_code")
    if not lot_code:
        raise exceptions.ValidationError({"detail": "lot_code is required.", "code": "FIELD_REQUIRED"})

    reason = data.get("reason")
    if not reason:
        raise exceptions.ValidationError({"detail": "reason is required.", "code": "FIELD_REQUIRED"})

    user_org = user.org
    if not user_org or user_org.verification != "VERIFIED":
        raise exceptions.PermissionDenied(
            {"detail": "Organisation is not verified.", "code": "ORG_UNVERIFIED"}
        )

    with transaction.atomic():
        root_lot = Lot.objects.select_for_update().filter(public_code=lot_code).first()
        if not root_lot:
            raise exceptions.NotFound({"detail": "Lot not found.", "code": "NOT_FOUND"})

        # Only custodian or admin (operator) can open recall
        is_custodian = (root_lot.custodian_org_id == user_org.org_id)
        is_operator = (user_org.org_type == "OPERATOR" or user.role == "OWNER")
        if not (is_custodian or is_operator):
            raise exceptions.PermissionDenied(
                {"detail": "Not authorized to open recall for this lot.", "code": "NOT_AUTHORIZED"}
            )

        root_lot.state = "RECALLED"
        lot_seq = root_lot.head_seq + 1

        payload = {"reason": reason, "initiated_by_org": str(user_org.org_id)}
        prev_hash = bytes(root_lot.head_hash) if root_lot.head_hash else None
        event_hash = compute_event_hash(prev_hash, "RECALL_OPEN", lot_seq, canonical_json_bytes(payload))

        recall_id = uuid.uuid4()
        recall = Recall.objects.create(
            recall_id=recall_id,
            initiated_by_org=user_org,
            root_lot=root_lot,
            reason=reason,
            status="OPEN",
            opened_at=timezone.now(),
        )

        TraceEvent.objects.create(
            event_id=uuid.uuid4(),
            lot=root_lot,
            lot_seq=lot_seq,
            event_type="RECALL_OPEN",
            event_time=timezone.now().isoformat(),
            org=user_org,
            user=user,
            payload=payload,
            sync_status="ACCEPTED",
            prev_hash=prev_hash,
            event_hash=event_hash,
        )

        root_lot.head_seq = lot_seq
        root_lot.head_hash = event_hash
        root_lot.save(update_fields=["state", "head_seq", "head_hash"])
        refresh_public_view(root_lot)

    return {
        "recall_id": str(recall.recall_id),
        "status": recall.status,
        "root_lot": root_lot.public_code,
    }


def trace_recall(user, recall_id_str: str) -> dict:
    """Executes recursive forward trace CTE to discover all descendants of a recalled lot."""
    try:
        recall_id = uuid.UUID(str(recall_id_str))
    except ValueError:
        raise exceptions.ValidationError({"detail": "Invalid recall_id UUID.", "code": "INVALID_UUID"})

    recall = Recall.objects.select_related("root_lot").filter(recall_id=recall_id).first()
    if not recall:
        raise exceptions.NotFound({"detail": "Recall not found.", "code": "NOT_FOUND"})

    # Forward trace query per docs/05
    query = """
    WITH RECURSIVE descendants AS (
        SELECT lot_id, 0 AS depth FROM lot WHERE lot_id = %s
        UNION ALL
        SELECT e.child_lot, d.depth + 1
        FROM lot_edge e JOIN descendants d ON e.parent_lot = d.lot_id
    )
    SELECT l.public_code, o.name AS custodian, l.state,
           b.qty_in_kg - (b.qty_sold_kg + b.qty_waste_kg + b.qty_rejected_kg
             + b.qty_out_transferred_kg + b.qty_split_out_kg + b.qty_variance_kg) AS on_hand_kg,
           b.qty_sold_kg
    FROM descendants d
    JOIN lot l ON l.lot_id = d.lot_id
    JOIN organisation o ON o.org_id = l.custodian_org
    JOIN lot_balance b ON b.lot_id = l.lot_id
    ORDER BY d.depth ASC, l.created_at ASC;
    """

    items = []
    with connection.cursor() as cursor:
        cursor.execute(query, [to_db_uuid(recall.root_lot.lot_id)])
        rows = cursor.fetchall()
        for row in rows:
            items.append({
                "lot_code": row[0],
                "custodian": row[1],
                "state": row[2],
                "on_hand_kg": float(row[3]) if row[3] is not None else 0.0,
                "sold_kg": float(row[4]) if row[4] is not None else 0.0,
            })

    return {"items": items}
