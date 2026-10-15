"""Cryptographic services for AnnaSutra: AES-256-GCM encryption, blind indexing, and masking.

Enforces:
1. Application-level AES-256-GCM encryption with fresh 96-bit random nonce and entity-bound AAD.
2. Key rotation support via enc_key_id tag.
3. HMAC-SHA-256 blind indexing for duplicate identification without plaintext storage.
4. Data masking utilities for restricted role-confined UI display.
"""

import os
import hmac
import hashlib
import re
from typing import Tuple, Optional
from django.conf import settings
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

DEFAULT_KEY_ID = "k1-2026"

# Load root encryption keys from settings/env or derive deterministic 32-byte dev keys
_DEV_KEY = hashlib.sha256(b"annasutra_dev_master_key_2026").digest()
_DEV_BLIND_KEY = hashlib.sha256(b"annasutra_blind_index_dev_key_2026").digest()


def _get_key_registry() -> dict[str, bytes]:
    """Retrieve key registry supporting zero-downtime key rotation."""
    registry = {}
    v1_raw = getattr(settings, "ANNASUTRA_ENCRYPTION_KEY_V1", os.getenv("ANNASUTRA_ENCRYPTION_KEY_V1"))
    if v1_raw:
        if len(v1_raw) == 64:
            registry[DEFAULT_KEY_ID] = bytes.fromhex(v1_raw)
        else:
            registry[DEFAULT_KEY_ID] = hashlib.sha256(v1_raw.encode("utf-8")).digest()
    else:
        registry[DEFAULT_KEY_ID] = _DEV_KEY

    # Optional rotation key V2
    v2_raw = getattr(settings, "ANNASUTRA_ENCRYPTION_KEY_V2", os.getenv("ANNASUTRA_ENCRYPTION_KEY_V2"))
    if v2_raw:
        if len(v2_raw) == 64:
            registry["k2-2026"] = bytes.fromhex(v2_raw)
        else:
            registry["k2-2026"] = hashlib.sha256(v2_raw.encode("utf-8")).digest()

    return registry


def _get_blind_index_key() -> bytes:
    """Retrieve secret key for HMAC blind indexing."""
    raw = getattr(settings, "ANNASUTRA_BLIND_INDEX_KEY", os.getenv("ANNASUTRA_BLIND_INDEX_KEY"))
    if raw:
        if len(raw) == 64:
            return bytes.fromhex(raw)
        return hashlib.sha256(raw.encode("utf-8")).digest()
    return _DEV_BLIND_KEY


def encrypt_field(
    plaintext: str | bytes,
    entity_id: str,
    key_id: Optional[str] = None
) -> Tuple[bytes, str]:
    """Encrypt a sensitive field with AES-256-GCM bound to entity_id AAD.

    Returns:
        (packed_bytes, key_id): packed_bytes = 12-byte nonce + ciphertext + 16-byte tag
    """
    if plaintext is None:
        raise ValueError("Plaintext cannot be None")

    registry = _get_key_registry()
    active_key_id = key_id or DEFAULT_KEY_ID
    key = registry.get(active_key_id)
    if not key:
        raise ValueError(f"Unknown encryption key ID: {active_key_id}")

    data = plaintext.encode("utf-8") if isinstance(plaintext, str) else plaintext
    aad = str(entity_id).encode("utf-8")
    nonce = os.urandom(12)  # 96-bit random nonce

    aesgcm = AESGCM(key)
    ciphertext_and_tag = aesgcm.encrypt(nonce, data, aad)
    packed = nonce + ciphertext_and_tag

    return packed, active_key_id


def decrypt_field(
    packed_bytes: bytes,
    entity_id: str,
    key_id: Optional[str] = None,
    as_bytes: bool = False
) -> str | bytes:
    """Decrypt an AES-256-GCM ciphertext verifying entity_id AAD and integrity tag."""
    if not packed_bytes or len(packed_bytes) < 28:
        raise ValueError("Invalid ciphertext length (minimum 28 bytes required: 12 nonce + 16 tag)")

    active_k_id = key_id or DEFAULT_KEY_ID
    registry = _get_key_registry()
    key = registry.get(active_k_id)
    if not key:
        raise ValueError(f"Unknown encryption key ID: {active_k_id}")

    nonce = packed_bytes[:12]
    ciphertext_and_tag = packed_bytes[12:]
    aad = str(entity_id).encode("utf-8")

    aesgcm = AESGCM(key)
    decrypted = aesgcm.decrypt(nonce, ciphertext_and_tag, aad)

    if as_bytes:
        return decrypted
    return decrypted.decode("utf-8")


def compute_pan_hmac(pan: str) -> bytes:
    """Compute deterministic HMAC-SHA-256 blind index for PAN uniqueness and duplicate checking."""
    normalized = pan.strip().upper()
    key = _get_blind_index_key()
    return hmac.new(key, normalized.encode("utf-8"), hashlib.sha256).digest()


def mask_pan(pan: Optional[str]) -> str:
    """Display format for PAN: AB******5C."""
    if not pan:
        return ""
    clean = pan.strip().upper()
    if len(clean) == 10:
        return f"{clean[:2]}******{clean[-2:]}"
    return "******"


def mask_bank_account(account_no: Optional[str]) -> str:
    """Display format for bank account: XXXXXX1234."""
    if not account_no:
        return ""
    clean = re.sub(r"\D", "", str(account_no))
    if len(clean) > 4:
        return f"{'X' * (len(clean) - 4)}{clean[-4:]}"
    return "XXXX"


def mask_upi(upi_id: Optional[str]) -> str:
    """Display format for UPI: ab***@bank."""
    if not upi_id:
        return ""
    clean = upi_id.strip()
    if "@" in clean:
        user, handle = clean.split("@", 1)
        masked_user = user[:2] + "***" if len(user) > 2 else user + "***"
        return f"{masked_user}@{handle}"
    return "****"


def mask_aadhaar_last4(last4: Optional[str]) -> str:
    """Display format for Aadhaar last 4: XXXXXXXX1234."""
    if not last4:
        return ""
    clean = str(last4).strip()
    return f"XXXXXXXX{clean[-4:]}"


class CryptoService:
    """Convenience class interface for cryptographic operations."""
    ACTIVE_KEY_ID = DEFAULT_KEY_ID

    @staticmethod
    def encrypt(plaintext: str | bytes, entity_id: str, key_id: Optional[str] = None) -> bytes:
        packed, _ = encrypt_field(plaintext, entity_id, key_id)
        return packed

    @staticmethod
    def decrypt(packed_bytes: bytes, entity_id: str, key_id: Optional[str] = None, as_bytes: bool = False) -> str | bytes:
        return decrypt_field(packed_bytes, entity_id, key_id or DEFAULT_KEY_ID, as_bytes=as_bytes)

    @staticmethod
    def blind_index_pan(pan: str) -> bytes:
        return compute_pan_hmac(pan)

    @staticmethod
    def mask_pan(pan: Optional[str]) -> str:
        return mask_pan(pan)

    @staticmethod
    def mask_bank_account(account_no: Optional[str]) -> str:
        return mask_bank_account(account_no)

    @staticmethod
    def mask_upi(upi_id: Optional[str]) -> str:
        return mask_upi(upi_id)

    @staticmethod
    def mask_aadhaar_last4(last4: Optional[str]) -> str:
        return mask_aadhaar_last4(last4)

