"""Quality and evidence inspection services for AnnaSutra."""

import uuid
from decimal import Decimal
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from rest_framework import exceptions

from apps.ledger.models import TraceEvent
from apps.ledger.services.hash_chain import (
    canonical_json_bytes,
    compute_event_hash,
)
from apps.lots.models import Lot
from apps.quality.models import Evidence, Inspection


def record_inspection(user, lot_code: str, data: dict) -> dict:
    """Records an inspection with grade, defect %, temperature, and optional evidence."""
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
        insp = Inspection.objects.filter(event=existing_event).first()
        return {
            "event_id": str(existing_event.event_id),
            "event_time": existing_event.event_time.isoformat(),
            "grade": insp.grade if insp else None,
            "defect_pct": float(insp.defect_pct) if insp and insp.defect_pct is not None else None,
            "temperature_c": float(insp.temperature_c) if insp and insp.temperature_c is not None else None,
            "notes": insp.notes if insp else None,
            "evidence_ids": [str(e.evidence_id) for e in existing_event.evidences.all()],
        }

    grade = data.get("grade")
    defect_pct = data.get("defect_pct")
    temperature_c = data.get("temperature_c")
    notes = data.get("notes")
    evidence_ids = data.get("evidence_ids", [])
    event_time_str = data.get("event_time", timezone.now().isoformat())

    with transaction.atomic():
        lot = Lot.objects.select_for_update().filter(public_code=lot_code).first()
        if not lot:
            raise exceptions.NotFound({"detail": "Lot not found.", "code": "NOT_FOUND"})

        # Author must be current custodian or pending receiver
        is_custodian = (lot.custodian_org_id == user_org.org_id)
        is_pending_receiver = (lot.pending_receiver_org_id == user_org.org_id)
        if not (is_custodian or is_pending_receiver):
            raise exceptions.PermissionDenied(
                {"detail": "Only custodian or pending receiver can inspect.", "code": "NOT_AUTHORIZED"}
            )

        lot_seq = lot.head_seq + 1
        payload = {
            "grade": grade,
            "defect_pct": str(defect_pct) if defect_pct is not None else None,
            "temperature_c": str(temperature_c) if temperature_c is not None else None,
            "notes": notes,
            "evidence_ids": [str(eid) for eid in evidence_ids],
        }
        prev_hash = bytes(lot.head_hash) if lot.head_hash else None
        event_hash = compute_event_hash(prev_hash, "INSPECT", lot_seq, canonical_json_bytes(payload))

        trace_event = TraceEvent.objects.create(
            event_id=event_id,
            lot=lot,
            lot_seq=lot_seq,
            event_type="INSPECT",
            event_time=event_time_str,
            org=user_org,
            user=user,
            payload=payload,
            sync_status="ACCEPTED",
            prev_hash=prev_hash,
            event_hash=event_hash,
        )

        insp_obj = Inspection.objects.create(
            inspection_id=uuid.uuid4(),
            event=trace_event,
            grade=grade,
            defect_pct=Decimal(str(defect_pct)) if defect_pct is not None else None,
            temperature_c=Decimal(str(temperature_c)) if temperature_c is not None else None,
            notes=notes,
        )

        # Link evidence records if already uploaded
        if evidence_ids:
            for eid in evidence_ids:
                try:
                    ev_uuid = uuid.UUID(str(eid))
                    Evidence.objects.filter(evidence_id=ev_uuid).update(event=trace_event)
                except ValueError:
                    pass

        lot.head_seq = lot_seq
        lot.head_hash = event_hash
        lot.save(update_fields=["head_seq", "head_hash"])

    return {
        "event_id": str(trace_event.event_id),
        "event_time": event_time_str,
        "grade": insp_obj.grade,
        "defect_pct": float(insp_obj.defect_pct) if insp_obj.defect_pct is not None else None,
        "temperature_c": float(insp_obj.temperature_c) if insp_obj.temperature_c is not None else None,
        "notes": insp_obj.notes,
        "evidence_ids": [str(eid) for eid in evidence_ids],
    }


def request_evidence_upload(user, data: dict) -> dict:
    """Pre-allocates an evidence descriptor and returns an upload URL."""
    kind = data.get("kind")
    if kind not in ["PHOTO", "SCALE_PHOTO", "LAB_CERT", "DOC"]:
        raise exceptions.ValidationError(
            {"detail": "Invalid evidence kind. Must be PHOTO, SCALE_PHOTO, LAB_CERT, or DOC.", "code": "INVALID_KIND"}
        )

    sha256_hex = data.get("sha256")
    if not sha256_hex:
        raise exceptions.ValidationError({"detail": "sha256 is required.", "code": "FIELD_REQUIRED"})

    try:
        if isinstance(sha256_hex, str):
            sha256_bytes = bytes.fromhex(sha256_hex) if len(sha256_hex) == 64 else sha256_hex.encode("utf-8")
        else:
            sha256_bytes = bytes(sha256_hex)
    except Exception:
        sha256_bytes = str(sha256_hex).encode("utf-8")

    evidence_id = uuid.uuid4()
    expires_at = timezone.now() + timedelta(hours=2)
    object_key = f"evidence/{evidence_id}_{kind.lower()}"

    # Return upload instructions conforming to EvidenceUpload schema
    upload_url = f"/api/v1/evidence/upload/{evidence_id}"

    return {
        "evidence_id": str(evidence_id),
        "upload_url": upload_url,
        "expires_at": expires_at.isoformat(),
    }
