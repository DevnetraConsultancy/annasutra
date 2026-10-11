"""Custody and Handover service for AnnaSutra.

Implements the two-party handover state machine:
DISPATCH -> RECEIVE -> DISPUTE -> RESOLVE.
Enforces Single Write Path rules, cryptographic hash chaining,
idempotency via client UUIDv7, and product discrepancy tolerances.
"""
import uuid
from decimal import Decimal
from datetime import timedelta
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import exceptions

from apps.custody.models import Handover
from apps.lots.models import Lot
from apps.inventory.models import LotBalance
from apps.ledger.models import TraceEvent
from apps.organisations.models import Organisation, PartnerLink
from apps.alerts.models import Alert
from apps.ledger.services.hash_chain import (
    canonical_json_bytes,
    compute_event_hash,
)
from apps.publicview.services import refresh_public_view


# Product tolerance default parameters per docs/05
DEFAULT_SCALE_RESOLUTION = Decimal("0.100")
DEFAULT_SHRINK_TOLERANCE_K = Decimal("0.02")  # 2% shrink tolerance for tomatoes


def dispatch_lot(user, lot_code: str, data: dict) -> Handover:
    """Dispatches a lot to a trusted partner receiver."""
    event_id_str = data.get("event_id")
    if not event_id_str:
        raise exceptions.ValidationError({"detail": "event_id is required.", "code": "VALIDATION_ERROR"})
    try:
        event_id = uuid.UUID(str(event_id_str))
    except ValueError:
        raise exceptions.ValidationError({"detail": "Invalid event_id UUID.", "code": "VALIDATION_ERROR"})

    # Idempotency check: return existing handover if event was already recorded
    existing_event = TraceEvent.objects.filter(event_id=event_id).first()
    if existing_event:
        handover = Handover.objects.filter(lot=existing_event.lot).order_by("-opened_at").first()
        if handover:
            return handover

    user_org = user.org
    if not user_org or user_org.verification != "VERIFIED":
        raise exceptions.PermissionDenied(
            {"detail": "Organisation is not verified to dispatch lots.", "code": "ORG_UNVERIFIED"}
        )

    to_org_id_str = data.get("to_org_id")
    if not to_org_id_str:
        raise exceptions.ValidationError({"detail": "to_org_id is required.", "code": "VALIDATION_ERROR"})
    try:
        to_org = Organisation.objects.get(org_id=uuid.UUID(str(to_org_id_str)))
    except (Organisation.DoesNotExist, ValueError):
        raise exceptions.NotFound({"detail": "Destination organisation not found.", "code": "NOT_FOUND"})

    if to_org.org_id == user_org.org_id:
        raise exceptions.ValidationError({"detail": "Cannot dispatch lot to own organisation.", "code": "VALIDATION_ERROR"})

    # Verify bilateral partner link is ACCEPTED
    has_partner_link = PartnerLink.objects.filter(
        (Q(org_a=user_org, org_b=to_org) | Q(org_a=to_org, org_b=user_org)),
        status="ACCEPTED",
    ).exists()
    if not has_partner_link:
        raise exceptions.PermissionDenied(
            {"detail": "Receiver is not an accepted trusted partner.", "code": "PARTNER_NOT_ACCEPTED"}
        )

    try:
        qty_kg = Decimal(str(data.get("qty_kg", "0")))
    except Exception:
        raise exceptions.ValidationError({"detail": "Invalid qty_kg.", "code": "VALIDATION_ERROR"})

    if qty_kg <= 0:
        raise exceptions.ValidationError({"detail": "Quantity to dispatch must be positive.", "code": "VALIDATION_ERROR"})

    event_time_str = data.get("event_time", timezone.now().isoformat())
    device_sig = data.get("device_signature")
    sig_bytes = str(device_sig).encode("utf-8") if device_sig else None

    with transaction.atomic():
        lot = Lot.objects.select_for_update().filter(public_code=lot_code).first()
        if not lot:
            raise exceptions.NotFound({"detail": "Lot not found.", "code": "NOT_FOUND"})

        if lot.custodian_org_id != user_org.org_id:
            raise exceptions.PermissionDenied(
                {"detail": "Only the current custodian can dispatch the lot.", "code": "NOT_CUSTODIAN"}
            )

        if lot.state not in ["CREATED", "IN_CUSTODY"]:
            raise exceptions.ValidationError(
                {"detail": f"Cannot dispatch lot in state {lot.state}.", "code": "INVALID_STATE"}
            )

        # Enforce partial unique index: at most one open handover
        if Handover.objects.filter(lot=lot, state="PENDING").exists():
            raise exceptions.ValidationError(
                {"detail": "An open handover is already pending for this lot.", "code": "HANDOVER_ALREADY_PENDING"}
            )

        balance = LotBalance.objects.select_for_update().filter(lot=lot).first()
        if not balance:
            raise exceptions.ValidationError({"detail": "Lot balance not found.", "code": "BALANCE_NOT_FOUND"})

        if balance.qty_on_hand_kg < qty_kg:
            raise exceptions.ValidationError(
                {
                    "detail": f"Insufficient quantity on hand: {balance.qty_on_hand_kg} kg available, tried to dispatch {qty_kg} kg.",
                    "code": "INSUFFICIENT_STOCK",
                }
            )

        handover_id = uuid.uuid4()
        expires_at = timezone.now() + timedelta(hours=24)

        handover = Handover.objects.create(
            handover_id=handover_id,
            lot=lot,
            from_org=user_org,
            to_org=to_org,
            declared_qty_kg=qty_kg,
            state="PENDING",
            opened_at=timezone.now(),
            expires_at=expires_at,
        )

        lot.state = "IN_TRANSIT"
        lot.pending_receiver_org = to_org
        lot_seq = lot.head_seq + 1

        payload = {
            "handover_id": str(handover_id),
            "to_org_id": str(to_org.org_id),
            "declared_qty_kg": str(qty_kg),
            "vehicle_no": data.get("vehicle_no"),
            "destination": data.get("destination"),
            "crates": data.get("crates"),
        }

        prev_hash = bytes(lot.head_hash) if lot.head_hash else None
        event_hash = compute_event_hash(
            prev_hash,
            "DISPATCH",
            lot_seq,
            canonical_json_bytes(payload),
        )

        TraceEvent.objects.create(
            event_id=event_id,
            lot=lot,
            lot_seq=lot_seq,
            event_type="DISPATCH",
            event_time=event_time_str,
            recorded_at=timezone.now(),
            org=user_org,
            user=user,
            counterparty_org=to_org,
            qty_kg=qty_kg,
            qty_basis="DECLARED",
            payload=payload,
            event_hash=event_hash,
            prev_hash=prev_hash,
            device_signature=sig_bytes,
        )

        lot.head_seq = lot_seq
        lot.head_hash = event_hash
        lot.save(update_fields=["state", "pending_receiver_org", "head_seq", "head_hash"])

        balance.qty_out_transferred_kg += qty_kg
        balance.save(update_fields=["qty_out_transferred_kg"])

        refresh_public_view(lot)

    return handover


def receive_handover(user, handover_id_val, data: dict) -> Handover:
    """Receives and accepts a pending handover, evaluating product tolerances."""
    event_id_str = data.get("event_id")
    if not event_id_str:
        raise exceptions.ValidationError({"detail": "event_id is required.", "code": "VALIDATION_ERROR"})
    try:
        event_id = uuid.UUID(str(event_id_str))
    except ValueError:
        raise exceptions.ValidationError({"detail": "Invalid event_id UUID.", "code": "VALIDATION_ERROR"})

    # Idempotency check
    existing_event = TraceEvent.objects.filter(event_id=event_id).first()
    if existing_event:
        handover = Handover.objects.filter(lot=existing_event.lot).order_by("-opened_at").first()
        if handover:
            return handover

    user_org = user.org
    if not user_org or user_org.verification != "VERIFIED":
        raise exceptions.PermissionDenied(
            {"detail": "Organisation is not verified.", "code": "ORG_UNVERIFIED"}
        )

    try:
        handover_id = uuid.UUID(str(handover_id_val))
    except ValueError:
        raise exceptions.ValidationError({"detail": "Invalid handover_id.", "code": "VALIDATION_ERROR"})

    event_time_str = data.get("event_time", timezone.now().isoformat())
    matches = bool(data.get("matches", False))
    device_sig = data.get("device_signature")
    sig_bytes = str(device_sig).encode("utf-8") if device_sig else None

    with transaction.atomic():
        handover = Handover.objects.select_for_update().filter(handover_id=handover_id).first()
        if not handover:
            raise exceptions.NotFound({"detail": "Handover not found.", "code": "NOT_FOUND"})

        if handover.state != "PENDING":
            # Race condition handling: if another receiver already claimed it, return conflict
            raise exceptions.ValidationError(
                {"detail": f"Handover is in state {handover.state}, not PENDING.", "code": "HANDOVER_NOT_PENDING"}
            )

        if handover.to_org_id != user_org.org_id:
            raise exceptions.PermissionDenied(
                {"detail": "Only the named receiver organisation can receive this handover.", "code": "NOT_RECEIVER"}
            )

        if handover.expires_at < timezone.now():
            handover.state = "EXPIRED"
            handover.save(update_fields=["state"])
            raise exceptions.ValidationError({"detail": "Handover has expired.", "code": "HANDOVER_EXPIRED"})

        lot = Lot.objects.select_for_update().filter(lot_id=handover.lot_id).first()
        balance = LotBalance.objects.select_for_update().filter(lot=lot).first()

        declared_qty = handover.declared_qty_kg
        if matches:
            received_qty = declared_qty
            rejected_qty = Decimal("0")
        else:
            received_qty = Decimal(str(data.get("received_qty_kg", declared_qty)))
            rejected_qty = Decimal(str(data.get("rejected_qty_kg", 0)))

        accounted = received_qty + rejected_qty
        diff = abs(declared_qty - accounted)
        allowed_tolerance = max(Decimal("2") * DEFAULT_SCALE_RESOLUTION, DEFAULT_SHRINK_TOLERANCE_K * declared_qty)

        variance = max(Decimal("0"), declared_qty - accounted)

        if diff <= allowed_tolerance:
            new_handover_state = "ACCEPTED"
        else:
            new_handover_state = "ACCEPTED_WITH_DISCREPANCY"
            # Flag audit alert
            Alert.objects.create(
                rule="TOLERANCE_EXCEEDED",
                lot=lot,
                severity="MEDIUM",
                detail={
                    "handover_id": str(handover.handover_id),
                    "declared_qty_kg": str(declared_qty),
                    "received_qty_kg": str(received_qty),
                    "rejected_qty_kg": str(rejected_qty),
                    "diff_kg": str(diff),
                    "allowed_tolerance_kg": str(allowed_tolerance),
                },
                status="OPEN",
            )

        # Move custody to receiver
        lot.custodian_org = user_org
        lot.pending_receiver_org = None
        lot.state = "IN_CUSTODY"
        lot_seq = lot.head_seq + 1

        payload = {
            "handover_id": str(handover.handover_id),
            "matches": matches,
            "received_qty_kg": str(received_qty),
            "rejected_qty_kg": str(rejected_qty),
            "variance_kg": str(variance),
            "condition": data.get("condition"),
            "crates_counted": data.get("crates_counted"),
        }

        prev_hash = bytes(lot.head_hash) if lot.head_hash else None
        event_hash = compute_event_hash(
            prev_hash,
            "RECEIVE",
            lot_seq,
            canonical_json_bytes(payload),
        )

        TraceEvent.objects.create(
            event_id=event_id,
            lot=lot,
            lot_seq=lot_seq,
            event_type="RECEIVE",
            event_time=event_time_str,
            recorded_at=timezone.now(),
            org=user_org,
            user=user,
            counterparty_org=handover.from_org,
            qty_kg=received_qty,
            qty_basis="MEASURED" if not matches else "DECLARED",
            payload=payload,
            event_hash=event_hash,
            prev_hash=prev_hash,
            device_signature=sig_bytes,
        )

        lot.head_seq = lot_seq
        lot.head_hash = event_hash
        lot.save(update_fields=["custodian_org", "pending_receiver_org", "state", "head_seq", "head_hash"])

        handover.state = new_handover_state
        handover.received_qty_kg = received_qty
        handover.closed_at = timezone.now()
        handover.save(update_fields=["state", "received_qty_kg", "closed_at"])

        # Update balance: transfer out completed, document any rejected & variance
        balance.qty_out_transferred_kg = max(Decimal("0"), balance.qty_out_transferred_kg - declared_qty)
        balance.qty_rejected_kg += rejected_qty
        balance.qty_variance_kg += variance
        balance.save(update_fields=["qty_out_transferred_kg", "qty_rejected_kg", "qty_variance_kg"])

        refresh_public_view(lot)

    return handover


def dispute_handover(user, handover_id_val, data: dict) -> Handover:
    """Disputes quantities on a received handover with discrepancy."""
    event_id_str = data.get("event_id")
    if not event_id_str:
        raise exceptions.ValidationError({"detail": "event_id is required.", "code": "VALIDATION_ERROR"})
    try:
        event_id = uuid.UUID(str(event_id_str))
    except ValueError:
        raise exceptions.ValidationError({"detail": "Invalid event_id UUID.", "code": "VALIDATION_ERROR"})

    existing_event = TraceEvent.objects.filter(event_id=event_id).first()
    if existing_event:
        handover = Handover.objects.filter(lot=existing_event.lot).order_by("-opened_at").first()
        if handover:
            return handover

    user_org = user.org
    try:
        handover_id = uuid.UUID(str(handover_id_val))
    except ValueError:
        raise exceptions.ValidationError({"detail": "Invalid handover_id.", "code": "VALIDATION_ERROR"})

    event_time_str = data.get("event_time", timezone.now().isoformat())
    reason = data.get("reason", "Discrepancy disputed")
    claimed_qty_str = data.get("claimed_qty_kg")
    claimed_qty = Decimal(str(claimed_qty_str)) if claimed_qty_str is not None else None
    device_sig = data.get("device_signature")
    sig_bytes = str(device_sig).encode("utf-8") if device_sig else None

    with transaction.atomic():
        handover = Handover.objects.select_for_update().filter(handover_id=handover_id).first()
        if not handover:
            raise exceptions.NotFound({"detail": "Handover not found.", "code": "NOT_FOUND"})

        if handover.from_org_id != user_org.org_id and handover.to_org_id != user_org.org_id:
            raise exceptions.PermissionDenied(
                {"detail": "Only counterparties of the handover can dispute.", "code": "NOT_COUNTERPARTY"}
            )

        if handover.state != "ACCEPTED_WITH_DISCREPANCY":
            raise exceptions.ValidationError(
                {"detail": f"Cannot dispute handover in state {handover.state}.", "code": "INVALID_STATE"}
            )

        lot = Lot.objects.select_for_update().filter(lot_id=handover.lot_id).first()
        lot.state = "DISPUTED"
        handover.state = "DISPUTED"
        handover.save(update_fields=["state"])

        lot_seq = lot.head_seq + 1
        payload = {
            "handover_id": str(handover.handover_id),
            "reason": reason,
            "claimed_qty_kg": str(claimed_qty) if claimed_qty else None,
        }

        prev_hash = bytes(lot.head_hash) if lot.head_hash else None
        event_hash = compute_event_hash(
            prev_hash,
            "DISPUTE",
            lot_seq,
            canonical_json_bytes(payload),
        )

        counterparty = handover.to_org if user_org.org_id == handover.from_org_id else handover.from_org
        TraceEvent.objects.create(
            event_id=event_id,
            lot=lot,
            lot_seq=lot_seq,
            event_type="DISPUTE",
            event_time=event_time_str,
            recorded_at=timezone.now(),
            org=user_org,
            user=user,
            counterparty_org=counterparty,
            payload=payload,
            event_hash=event_hash,
            prev_hash=prev_hash,
            device_signature=sig_bytes,
        )

        lot.head_seq = lot_seq
        lot.head_hash = event_hash
        lot.save(update_fields=["state", "head_seq", "head_hash"])

        Alert.objects.create(
            rule="HANDOVER_DISPUTED",
            lot=lot,
            severity="HIGH",
            detail={"reason": reason, "handover_id": str(handover.handover_id)},
            status="OPEN",
        )

        refresh_public_view(lot)

    return handover


def resolve_handover(user, handover_id_val, data: dict) -> Handover:
    """Resolves a disputed handover with counterparty agreed quantity."""
    event_id_str = data.get("event_id")
    if not event_id_str:
        raise exceptions.ValidationError({"detail": "event_id is required.", "code": "VALIDATION_ERROR"})
    try:
        event_id = uuid.UUID(str(event_id_str))
    except ValueError:
        raise exceptions.ValidationError({"detail": "Invalid event_id UUID.", "code": "VALIDATION_ERROR"})

    existing_event = TraceEvent.objects.filter(event_id=event_id).first()
    if existing_event:
        handover = Handover.objects.filter(lot=existing_event.lot).order_by("-opened_at").first()
        if handover:
            return handover

    user_org = user.org
    try:
        handover_id = uuid.UUID(str(handover_id_val))
    except ValueError:
        raise exceptions.ValidationError({"detail": "Invalid handover_id.", "code": "VALIDATION_ERROR"})

    try:
        agreed_qty = Decimal(str(data.get("agreed_qty_kg", "0")))
    except Exception:
        raise exceptions.ValidationError({"detail": "Invalid agreed_qty_kg.", "code": "VALIDATION_ERROR"})

    if agreed_qty <= 0:
        raise exceptions.ValidationError({"detail": "Agreed quantity must be positive.", "code": "VALIDATION_ERROR"})

    event_time_str = data.get("event_time", timezone.now().isoformat())
    note = data.get("note", "Handover resolved")
    device_sig = data.get("device_signature")
    sig_bytes = str(device_sig).encode("utf-8") if device_sig else None

    with transaction.atomic():
        handover = Handover.objects.select_for_update().filter(handover_id=handover_id).first()
        if not handover:
            raise exceptions.NotFound({"detail": "Handover not found.", "code": "NOT_FOUND"})

        if handover.from_org_id != user_org.org_id and handover.to_org_id != user_org.org_id:
            raise exceptions.PermissionDenied(
                {"detail": "Only counterparties of the handover can resolve.", "code": "NOT_COUNTERPARTY"}
            )

        if handover.state != "DISPUTED":
            raise exceptions.ValidationError(
                {"detail": f"Cannot resolve handover in state {handover.state}.", "code": "INVALID_STATE"}
            )

        lot = Lot.objects.select_for_update().filter(lot_id=handover.lot_id).first()
        lot.state = "IN_CUSTODY"
        handover.state = "ACCEPTED"
        handover.received_qty_kg = agreed_qty
        handover.save(update_fields=["state", "received_qty_kg"])

        lot_seq = lot.head_seq + 1
        payload = {
            "handover_id": str(handover.handover_id),
            "agreed_qty_kg": str(agreed_qty),
            "note": note,
        }

        prev_hash = bytes(lot.head_hash) if lot.head_hash else None
        event_hash = compute_event_hash(
            prev_hash,
            "RESOLVE",
            lot_seq,
            canonical_json_bytes(payload),
        )

        counterparty = handover.to_org if user_org.org_id == handover.from_org_id else handover.from_org
        TraceEvent.objects.create(
            event_id=event_id,
            lot=lot,
            lot_seq=lot_seq,
            event_type="RESOLVE",
            event_time=event_time_str,
            recorded_at=timezone.now(),
            org=user_org,
            user=user,
            counterparty_org=counterparty,
            qty_kg=agreed_qty,
            qty_basis="MEASURED",
            payload=payload,
            event_hash=event_hash,
            prev_hash=prev_hash,
            device_signature=sig_bytes,
        )

        lot.head_seq = lot_seq
        lot.head_hash = event_hash
        lot.save(update_fields=["state", "head_seq", "head_hash"])

        refresh_public_view(lot)

    return handover
