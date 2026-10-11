"""Event correction and QR label reissue services for AnnaSutra.

Enforces append-only rules: corrections create new events with supersedes_event,
never mutating historical rows.
"""

import uuid
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework import exceptions

from apps.alerts.models import Alert
from apps.inventory.models import LotBalance
from apps.labels.models import QrBlock, QrLabel
from apps.ledger.models import TraceEvent
from apps.ledger.services.hash_chain import (
    canonical_json_bytes,
    compute_event_hash,
)
from apps.lots.models import Lot
from apps.publicview.services import refresh_public_view


def correct_event(user, event_id_str: str, data: dict) -> dict:
    """Appends a new CORRECTION event referencing the superseded event. Never mutates rows."""
    try:
        orig_event_id = uuid.UUID(str(event_id_str))
    except ValueError:
        raise exceptions.ValidationError({"detail": "Invalid target event_id UUID.", "code": "INVALID_UUID"})

    corr_event_id_str = data.get("event_id")
    if not corr_event_id_str:
        raise exceptions.ValidationError({"detail": "event_id is required.", "code": "FIELD_REQUIRED"})
    try:
        corr_event_id = uuid.UUID(str(corr_event_id_str))
    except ValueError:
        raise exceptions.ValidationError({"detail": "Invalid event_id UUID.", "code": "INVALID_UUID"})

    user_org = user.org
    if not user_org or user_org.verification != "VERIFIED":
        raise exceptions.PermissionDenied(
            {"detail": "Organisation is not verified.", "code": "ORG_UNVERIFIED"}
        )

    # Idempotency check
    existing = TraceEvent.objects.filter(event_id=corr_event_id).first()
    if existing:
        return {"event_id": str(corr_event_id), "status": "ACCEPTED", "lot_seq": existing.lot_seq}

    reason = data.get("reason")
    if not reason:
        raise exceptions.ValidationError({"detail": "reason is required for correction.", "code": "FIELD_REQUIRED"})

    new_values = data.get("new_values")
    if not new_values or not isinstance(new_values, dict):
        raise exceptions.ValidationError({"detail": "new_values object is required.", "code": "FIELD_REQUIRED"})

    device_sig = data.get("device_signature")
    if not device_sig:
        raise exceptions.ValidationError({"detail": "device_signature is required for corrections.", "code": "FIELD_REQUIRED"})
    sig_bytes = str(device_sig).encode("utf-8")

    event_time_str = data.get("event_time", timezone.now().isoformat())

    with transaction.atomic():
        orig_event = TraceEvent.objects.select_related("lot", "org").filter(event_id=orig_event_id).first()
        if not orig_event:
            raise exceptions.NotFound({"detail": "Target event to correct not found.", "code": "NOT_FOUND"})

        # Author must be from authoring org, or operator
        is_author_org = (orig_event.org_id == user_org.org_id)
        is_operator = (user_org.org_type == "OPERATOR")
        if not (is_author_org or is_operator):
            Alert.objects.create(
                rule="UNAUTHORIZED_CORRECTION",
                lot=orig_event.lot,
                severity="HIGH",
                detail={
                    "attempted_by_org": str(user_org.org_id),
                    "target_event_id": str(orig_event_id),
                },
            )
            raise exceptions.PermissionDenied(
                {"detail": "Only author organisation or operator can append a correction.", "code": "NOT_AUTHORIZED"}
            )

        lot = Lot.objects.select_for_update().filter(lot_id=orig_event.lot_id).first()
        lot_seq = lot.head_seq + 1

        payload = {
            "supersedes_event": str(orig_event_id),
            "original_type": orig_event.event_type,
            "reason": reason,
            "new_values": new_values,
        }
        prev_hash = bytes(lot.head_hash) if lot.head_hash else None
        event_hash = compute_event_hash(prev_hash, "CORRECTION", lot_seq, canonical_json_bytes(payload))

        TraceEvent.objects.create(
            event_id=corr_event_id,
            lot=lot,
            lot_seq=lot_seq,
            event_type="CORRECTION",
            event_time=event_time_str,
            org=user_org,
            user=user,
            payload=payload,
            supersedes_event=orig_event,
            sync_status="ACCEPTED",
            device_signature=sig_bytes,
            prev_hash=prev_hash,
            event_hash=event_hash,
        )

        lot.head_seq = lot_seq
        lot.head_hash = event_hash
        lot.save(update_fields=["head_seq", "head_hash"])

        # If quantity was corrected, adjust balance
        if "qty_kg" in new_values:
            try:
                new_qty = Decimal(str(new_values["qty_kg"]))
                balance = LotBalance.objects.select_for_update().filter(lot=lot).first()
                if balance and orig_event.qty_kg is not None:
                    diff = new_qty - orig_event.qty_kg
                    if orig_event.event_type in ["HARVEST_CREATE", "RECEIVE"]:
                        balance.qty_in_kg += diff
                        balance.save(update_fields=["qty_in_kg"])
                    elif orig_event.event_type in ["WASTE"]:
                        balance.qty_waste_kg += diff
                        balance.save(update_fields=["qty_waste_kg"])

                    if balance.qty_on_hand_kg < Decimal("-0.001"):
                        Alert.objects.create(
                            rule="RECONCILIATION_DISCREPANCY",
                            lot=lot,
                            severity="HIGH",
                            detail={"error": "On-hand became negative after quantity correction", "diff": str(diff)},
                        )
            except Exception:
                pass

        refresh_public_view(lot)

    return {"event_id": str(corr_event_id), "status": "ACCEPTED", "lot_seq": lot_seq}


def reissue_label(user, lot_code: str, data: dict) -> dict:
    """Voids old QR serial and binds a fresh serial to the same lot."""
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

    existing = TraceEvent.objects.filter(event_id=event_id).first()
    if existing:
        return {"event_id": str(event_id), "status": "ACCEPTED", "lot_seq": existing.lot_seq}

    new_serial = data.get("new_serial")
    if not new_serial:
        raise exceptions.ValidationError({"detail": "new_serial is required.", "code": "FIELD_REQUIRED"})

    reason = data.get("reason")
    if not reason:
        raise exceptions.ValidationError({"detail": "reason is required.", "code": "FIELD_REQUIRED"})

    device_sig = data.get("device_signature")
    if not device_sig:
        raise exceptions.ValidationError({"detail": "device_signature is required for label reissue.", "code": "FIELD_REQUIRED"})
    sig_bytes = str(device_sig).encode("utf-8")

    event_time_str = data.get("event_time", timezone.now().isoformat())

    with transaction.atomic():
        lot = Lot.objects.select_for_update().filter(public_code=lot_code).first()
        if not lot:
            raise exceptions.NotFound({"detail": "Lot not found.", "code": "NOT_FOUND"})

        if lot.custodian_org_id != user_org.org_id:
            raise exceptions.PermissionDenied(
                {"detail": "Only current custodian can reissue label.", "code": "NOT_CUSTODIAN"}
            )

        new_label = QrLabel.objects.select_for_update().filter(serial=new_serial).first()
        if not new_label:
            block = QrBlock.objects.create(
                block_id=uuid.uuid4(),
                issued_to_org=user_org,
                issued_by=user,
                count=1,
            )
            new_label = QrLabel.objects.create(
                serial=new_serial,
                block=block,
                issued_to_org=user_org,
                status="ISSUED",
            )
        if new_label.lot_id or new_label.status == "BOUND":
            raise exceptions.Conflict(
                {"detail": f"New serial {new_serial} is already bound to a lot.", "code": "LABEL_ALREADY_USED"}
            )

        # Void old label
        QrLabel.objects.filter(lot=lot, status="BOUND").update(status="VOID")

        # Bind new label
        new_label.lot = lot
        new_label.status = "BOUND"
        new_label.bound_at = timezone.now()
        new_label.save(update_fields=["lot", "status", "bound_at"])

        lot_seq = lot.head_seq + 1
        payload = {"old_serial": lot_code, "new_serial": new_serial, "reason": reason}
        prev_hash = bytes(lot.head_hash) if lot.head_hash else None
        event_hash = compute_event_hash(prev_hash, "LABEL_REISSUE", lot_seq, canonical_json_bytes(payload))

        TraceEvent.objects.create(
            event_id=event_id,
            lot=lot,
            lot_seq=lot_seq,
            event_type="LABEL_REISSUE",
            event_time=event_time_str,
            org=user_org,
            user=user,
            payload=payload,
            sync_status="ACCEPTED",
            device_signature=sig_bytes,
            prev_hash=prev_hash,
            event_hash=event_hash,
        )

        lot.public_code = new_serial
        lot.head_seq = lot_seq
        lot.head_hash = event_hash
        lot.save(update_fields=["public_code", "head_seq", "head_hash"])
        refresh_public_view(lot)

    return {"event_id": str(event_id), "status": "ACCEPTED", "lot_seq": lot_seq}
