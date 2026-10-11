"""Cryptographic hash chain computation and verification for lot ledger."""
import hashlib
import json
from decimal import Decimal
from typing import Any, Tuple, Optional


def decimal_default(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def canonical_json_bytes(payload: dict) -> bytes:
    """Produces canonical JSON serialization with sorted keys and compact separators."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=decimal_default).encode("utf-8")


def compute_event_hash(
    prev_hash: Optional[bytes],
    event_type: str,
    lot_seq: int,
    payload_bytes: bytes,
) -> bytes:
    """Computes SHA-256 hash: SHA256(prev_hash || event_type || lot_seq || payload_bytes)."""
    hasher = hashlib.sha256()
    if prev_hash:
        hasher.update(bytes(prev_hash))
    hasher.update(event_type.encode("utf-8"))
    hasher.update(str(lot_seq).encode("utf-8"))
    hasher.update(payload_bytes)
    return hasher.digest()


def verify_lot_hash_chain(lot) -> Tuple[bool, Optional[str]]:
    """Traverses all trace events for a given lot and verifies sequential hash chaining.
    
    Returns (True, None) if valid, or (False, reason) if corrupted.
    """
    from apps.ledger.models import TraceEvent

    events = TraceEvent.objects.filter(lot=lot).order_by("lot_seq")
    if not events.exists():
        return True, None

    expected_prev_hash: Optional[bytes] = None
    expected_seq = 1

    for event in events:
        if event.lot_seq != expected_seq:
            return False, f"Sequence gap detected: expected {expected_seq}, found {event.lot_seq}"

        stored_prev = bytes(event.prev_hash) if event.prev_hash else None
        if stored_prev != expected_prev_hash:
            return False, f"Previous hash mismatch at lot_seq {event.lot_seq}"

        payload_bytes = canonical_json_bytes(event.payload)
        recomputed = compute_event_hash(
            stored_prev,
            event.event_type,
            event.lot_seq,
            payload_bytes,
        )

        stored_hash = bytes(event.event_hash)
        if recomputed != stored_hash:
            return False, f"Event hash mismatch at lot_seq {event.lot_seq}: tamper detected"

        expected_prev_hash = stored_hash
        expected_seq += 1

    return True, None
