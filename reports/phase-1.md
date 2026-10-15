# AnnaSutra Registration System — Phase 1 Report
**Database Schema & Cryptographic Foundations**
*Date: 2026-10-15*

---

## 1. What Was Done
1. **Cryptographic Foundation (`backend/apps/identity/services/crypto.py`)**:
   - Implemented AES-256-GCM symmetric authenticated encryption.
   - Generates a fresh 96-bit (12-byte) random nonce for every encryption operation.
   - Binds Additional Authenticated Data (AAD) to the `entity_id` so ciphertext cannot be swapped between entities.
   - Formats ciphertext as `key_id$iv_b64$ciphertext_tag_b64` (e.g. `k1-2026$...`).
   - Supports key rotation through active key ID configuration (`ANNASUTRA_ACTIVE_KEY_ID`).
   - Implemented HMAC-SHA256 blind indexing with a pepper secret for exact-match querying of normalized PAN without storing or exposing plaintext.
   - Built strict masking helpers: `mask_pan` (`AB******5C`), `mask_bank_account` (`******4321`), `mask_aadhaar_last4` (`•••• •••• 1234`).

2. **Database Models (`backend/apps/identity/models.py`)**:
   - **`EntityProfile`**: Master profile holding non-sensitive public business information, workflow state (`DRAFT`, `SUBMITTED`, `UNDER_REVIEW`, `APPROVED`, `REJECTED`, `SUSPENDED`), assigned sequential identifier (`PR-WB-000142`), QR token (`Crockford Base32`), and timestamps.
   - **`EntitySensitive`**: Isolated table for encrypted sensitive data (PAN ciphertext + blind index, bank account/IFSC, encrypted address, last 4 digits of Aadhaar). No plaintext fields exist.
   - **`EntityPlot`**: Multi-plot support for producers with centroid coordinates and AES-256-GCM encrypted GeoJSON polygon boundaries.
   - **`EntityFacility`**: Operational facilities (collection centres, cold stores, warehouses, retail counters) for downstream tiers with geofences and licenses.
   - **`EntityRoleDetails`**: Extensible JSON configuration for tier-specific operational parameters (farm type, certifications, storage type, fleet, GSTIN, FSSAI).
   - **`EntityDocument`**: Document metadata with file path, SHA-256 content checksum, MIME type, file size, and verification status.
   - **`VerificationReview`**: Strictly append-only record of admin review decisions.
   - **`ProfileChangeLog`**: Strictly append-only audit trail capturing field-level before/after diffs.
   - **`SensitiveAccessLog`**: Strictly append-only access log recording who accessed sensitive data, when, and for what purpose.
   - **`EntityConsentRecord`**: Statutory DPDP/Aadhaar/data processing consent records with IP address, user-agent, and consent version.

3. **Database Migration (`backend/apps/identity/migrations/0002_registration_schema.py`)**:
   - Created migration 0002 targeting MySQL 8 on Aiven with fallback parsing for SQLite test environments.
   - Integrated MySQL triggers for append-only tables (`verification_review`, `profile_change_log`, `sensitive_access_log`) preventing `UPDATE` and `DELETE` via `SIGNAL SQLSTATE '45000'`.
   - Dual-enforced at the Django ORM level via `PermissionError` on save/delete.

4. **Automated Verification**:
   - Implemented unit tests in `backend/tests/test_crypto_service.py` (5 tests).
   - Implemented model integration tests in `backend/tests/test_phase1_models.py` (4 tests).

---

## 2. Test Execution Output

```
backend/venv/Scripts/python -m pytest backend/tests/test_crypto_service.py backend/tests/test_phase1_models.py backend/tests/test_phase0_claims.py -v

============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-8.3.5, pluggy-1.6.0
django: version: 5.1.15, settings: config.settings.test (from ini)
rootdir: C:\Users\Dr_Nee\Videos\@CDAC\Traciability\annasutra\backend
configfile: pyproject.toml
plugins: hypothesis-6.169.0, django-4.9.0
collected 12 items

backend/tests/test_phase1_models.py::test_entity_profile_draft_and_sensitive_encryption PASSED [  8%]
backend/tests/test_phase1_models.py::test_entity_plot_encrypted_polygon PASSED         [ 16%]
backend/tests/test_phase1_models.py::test_append_only_audit_log_enforcement PASSED    [ 25%]
backend/tests/test_phase1_models.py::test_consent_record_lifecycle PASSED             [ 33%]
backend/tests/test_phase0_claims.py::test_favicon_endpoint PASSED                      [ 41%]
backend/tests/test_phase0_claims.py::test_landing_page_claims_scrubbed PASSED         [ 50%]
backend/tests/test_phase0_claims.py::test_public_lot_view_claims_scrubbed PASSED       [ 58%]
backend/tests/test_crypto_service.py::test_encrypt_decrypt_roundtrip PASSED            [ 66%]
backend/tests/test_crypto_service.py::test_tampered_ciphertext_fails PASSED            [ 75%]
backend/tests/test_crypto_service.py::test_wrong_entity_id_fails_aad_check PASSED      [ 83%]
backend/tests/test_crypto_service.py::test_blind_index_pan_deterministic PASSED       [ 91%]
backend/tests/test_crypto_service.py::test_masking_helpers PASSED                      [100%]

============================= 12 passed in 3.56s ==============================
```

---

## 3. Cryptographic Verification Evidence
- **Nonce Freshness**: Verified that two encryptions of the same plaintext yield distinct ciphertexts.
- **Tamper Evidence**: Tampering with a single byte in ciphertext or auth tag raises `InvalidTag` from `cryptography.hazmat.primitives.ciphers.aead.AESGCM`.
- **Context Binding (AAD)**: Encrypting under `entity_id="E1"` and attempting decryption under `entity_id="E2"` raises `InvalidTag`.
- **Blind Index Determinism**: PAN normalization ensures case-insensitivity while producing 64-char hex HMAC-SHA256 digests matching only identical PANs with zero plaintext leakage.

---

## 4. Rollback Plan
- To roll back schema:
  `python manage.py migrate identity 0001`
- Any encrypted fields in `EntitySensitive` remain decryptable only with the matched key version.

---

## 5. Sign-off Block
- **Phase 1 Status**: COMPLETED
- **Sign-off**: System verified and tests passed.
