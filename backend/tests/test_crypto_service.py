"""Unit tests for AES-256-GCM encryption, blind indexing, and masking."""

import pytest
from cryptography.exceptions import InvalidTag
from apps.identity.services.crypto import (
    encrypt_field,
    decrypt_field,
    compute_pan_hmac,
    mask_pan,
    mask_bank_account,
    mask_upi,
    mask_aadhaar_last4,
)


def test_encrypt_decrypt_roundtrip():
    entity_id = "550e8400-e29b-41d4-a716-446655440000"
    plaintext = "ABCDE1234F"

    ciphertext, key_id = encrypt_field(plaintext, entity_id)
    assert len(ciphertext) > len(plaintext)
    assert key_id == "k1-2026"

    decrypted = decrypt_field(ciphertext, entity_id, key_id)
    assert decrypted == plaintext


def test_tampered_ciphertext_fails():
    entity_id = "550e8400-e29b-41d4-a716-446655440000"
    plaintext = "SECRET_ACCOUNT_NUMBER_9999"

    ciphertext, key_id = encrypt_field(plaintext, entity_id)
    tampered = bytearray(ciphertext)
    tampered[-1] ^= 0xFF  # alter last byte of tag

    with pytest.raises(InvalidTag):
        decrypt_field(bytes(tampered), entity_id, key_id)


def test_wrong_entity_id_fails_aad_check():
    entity_id_1 = "11111111-1111-1111-1111-111111111111"
    entity_id_2 = "22222222-2222-2222-2222-222222222222"
    plaintext = "SENSITIVE_DATA"

    ciphertext, key_id = encrypt_field(plaintext, entity_id_1)

    with pytest.raises(InvalidTag):
        decrypt_field(ciphertext, entity_id_2, key_id)


def test_blind_index_pan_deterministic():
    pan1 = "abcde1234f"
    pan2 = "ABCDE1234F "
    pan3 = "WXYZ9876A"

    hmac1 = compute_pan_hmac(pan1)
    hmac2 = compute_pan_hmac(pan2)
    hmac3 = compute_pan_hmac(pan3)

    assert len(hmac1) == 32
    assert hmac1 == hmac2
    assert hmac1 != hmac3


def test_masking_helpers():
    assert mask_pan("ABCDE1234F") == "AB******4F"
    assert mask_bank_account("123456789012") == "XXXXXXXX9012"
    assert mask_bank_account("987654321") == "XXXXX4321"
    assert mask_upi("farmer.ramesh@okaxis") == "fa***@okaxis"
    assert mask_aadhaar_last4("1234") == "XXXXXXXX1234"
