"""Daily hash chain verification and Merkle root anchoring service."""
import hashlib
from typing import List, Tuple
from django.utils import timezone
from apps.lots.models import Lot
from apps.ledger.models import HashAnchor
from apps.alerts.models import Alert
from apps.ledger.services.hash_chain import verify_lot_hash_chain


def compute_merkle_root(leaf_hashes: List[bytes]) -> bytes:
    """Computes binary Merkle tree root hash from a list of leaf hashes."""
    if not leaf_hashes:
        return hashlib.sha256(b"EMPTY_TREE").digest()

    current_level = sorted(leaf_hashes)

    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            if i + 1 < len(current_level):
                right = current_level[i + 1]
            else:
                right = left  # duplicate odd leaf
            hasher = hashlib.sha256()
            hasher.update(left)
            hasher.update(right)
            next_level.append(hasher.digest())
        current_level = next_level

    return current_level[0]


def run_daily_anchoring(anchor_date=None, location: str = "s3://annasutra-anchors/daily/") -> Tuple[bytes, int, int]:
    """Re-verifies all lot hash chains, detects mutations, and records daily Merkle anchor.
    
    Returns (root_hash, verified_count, corrupted_count).
    """
    if anchor_date is None:
        anchor_date = timezone.now().date()

    lots = Lot.objects.exclude(head_hash__isnull=True)
    verified_count = 0
    corrupted_count = 0
    valid_leaf_hashes = []

    for lot in lots:
        is_valid, error_msg = verify_lot_hash_chain(lot)
        if not is_valid:
            corrupted_count += 1
            Alert.objects.create(
                rule="HASH_CHAIN_MUTATION",
                lot=lot,
                severity="HIGH",
                detail={
                    "lot_code": lot.public_code,
                    "error": error_msg,
                    "date": str(anchor_date),
                },
                status="OPEN",
            )
        else:
            verified_count += 1
            if lot.head_hash:
                valid_leaf_hashes.append(bytes(lot.head_hash))

    root_hash = compute_merkle_root(valid_leaf_hashes)
    full_location = f"{location.rstrip('/')}/{anchor_date.isoformat()}/root.bin"

    HashAnchor.objects.update_or_create(
        anchor_date=anchor_date,
        defaults={
            "root_hash": root_hash,
            "location": full_location,
            "created_at": timezone.now(),
        },
    )

    return root_hash, verified_count, corrupted_count
