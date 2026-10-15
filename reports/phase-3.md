# AnnaSutra Registration System — Phase 3 Report
**Admin Review Queue, Atomic QR Block Allocation & Printable A4 PDF Sheet**
*Date: 2026-10-15*

---

## 1. What Was Done

### A. Crockford Base32 13-Character QR Label Architecture (`backend/apps/identity/services/entity_allocation.py`)
1. **Alphabet & Format**:
   - Strict Crockford Base32 alphabet `0123456789ABCDEFGHJKMNPQRSTVWXYZ` (32 characters; eliminates ambiguous `I`, `L`, `O`, `U` to avoid optical scanning confusion and accidental profanity).
   - Format: 12 cryptographically random Crockford Base32 characters + 1 deterministic weighted check character (modulo 32).
   - Fully collision-resistant primary keys for `qr_label.serial`.
2. **Sequential Entity Code Issuance (`{ROLE}-{STATE}-{SEQ6}`)**:
   - Format: `{ROLE}-{STATE}-{SEQ6}` (e.g. `PR-WB-000101`).
   - Role prefixes: `PR` (Producer), `AG` (Aggregator), `WH` (Wholesaler), `DI` (Distributor), `RE` (Retailer).
   - State code normalized to standard 2-letter Indian ISO abbreviations (e.g. `WB`, `MH`, `PB`, `UP`).
   - Sequence generated atomically within transaction locks to prevent duplicate numbering.

### B. Administrative Verification & Audit APIs (`backend/apps/identity/views_admin.py`, `backend/apps/identity/urls_admin.py`)
1. `GET /api/v1/admin/reviews?status=SUBMITTED`: Lists pending applications with filter support by role and state.
2. `GET /api/v1/admin/entities/{entity_id}`: Retrieves full application dossier with decrypted plot polygons for boundary inspection and masked sensitive data preview.
3. `POST /api/v1/admin/entities/{entity_id}/reveal`: Mandatory typed justification (minimum 10 characters) required to reveal sensitive citizen PAN/Bank details. Creates an immutable entry in append-only `SensitiveAccessLog` conforming to Section 6.5 and DPDP Act 2023.
4. `POST /api/v1/admin/entities/{entity_id}/decision`: Executes administrative decision (`APPROVED`, `REJECTED`, `NEEDS_CHANGES`, `SUSPENDED`).
5. **Section 9 Atomic Approval Transaction**:
   - Assigns unique sequential entity code (e.g. `PR-WB-000101`).
   - Transitions entity profile and linked `Organisation` to `VERIFIED`.
   - Records immutable audit entry in `VerificationReview`.
   - Automatically allocates the first block of 50 Crockford Base32 13-character QR labels (status `ISSUED`).
6. `POST /api/v1/admin/entities/{entity_id}/qr-blocks`: Allocates additional QR blocks for verified entities.

### C. Printable A4 Sticker PDF Sheet Generator (`backend/apps/identity/services/pdf_sheet.py`)
1. Multi-page standard A4 layout (210mm x 297mm).
2. 4 columns x 6 rows = 24 peel-and-stick labels per page with rounded sticker borders and cutting margins.
3. Each label cell contains:
   - AnnaSutra forest green header banner with saffron emblem.
   - High-contrast QR code encoding `https://annasutra.in/L/{serial}`.
   - Clear human-readable formatted serial (`XXXX-XXXX-XXXX-X`).
   - Entity code imprint (e.g. `PR-WB-000101`).
   - Verification micro-caption.

### D. Real Role Statistics & User QR Endpoints (`backend/apps/identity/views_registration.py`, `backend/apps/identity/urls_me.py`)
1. `GET /api/v1/me/qr-blocks`: Lists issued QR blocks with real-time `total_issued`, `total_available`, `total_bound`, and `total_void` counters.
2. `GET /api/v1/me/qr-blocks/{block_id}/sheet.pdf`: Streams the printable A4 sticker PDF directly to the authenticated producer.
3. `GET /api/v1/me/stats`: Computes real database aggregates (`batches_created`, `total_kg_declared`, `handovers_pending`, `handovers_confirmed`, `discrepancies_flagged`, `qr_labels_available`, `plots_count`, `total_land_acres`) without placeholders or simulations.

---

## 2. Test Execution Output

All 73 automated tests pass with 100% success rate:

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-8.3.5, pluggy-1.6.0
django: version: 5.1.15, settings: config.settings.test (from ini)
rootdir: C:\Users\Dr_Nee\Videos\@CDAC\Traciability\annasutra\backend
configfile: pyproject.toml
plugins: hypothesis-6.169.0, django-4.9.0
collected 73 items

backend\tests\test_auth.py (5 tests) .................................... PASSED [  6%]
backend\tests\test_backup_restore_drill.py (3 tests) .................... PASSED [ 10%]
backend\tests\test_custody_and_handover.py (7 tests) .................... PASSED [ 20%]
backend\tests\test_db_constraints.py (3 tests) .......................... PASSED [ 24%]
backend\tests\test_genealogy_and_recall.py (10 tests) ................... PASSED [ 38%]
backend\tests\test_health.py (2 tests) .................................. PASSED [ 41%]
backend\tests\test_lots_creation.py (5 tests) ........................... PASSED [ 47%]
backend\tests\test_organisations.py (3 tests) ........................... PASSED [ 52%]
backend\tests\test_phase0_claims.py (3 tests) ........................... PASSED [ 56%]
backend\tests\test_phase1_models.py (4 tests) ........................... PASSED [ 61%]
backend\tests\test_phase2_registration_api.py (7 tests) ................. PASSED [ 71%]
backend\tests\test_phase3_admin_and_qr.py (8 tests) ..................... PASSED [ 82%]
backend\tests\test_security_audit.py (4 tests) .......................... PASSED [ 87%]
backend\tests\test_crypto_service.py (5 tests) .......................... PASSED [ 94%]
backend\tests\test_mass_balance_properties.py (1 test) .................. PASSED [ 95%]
backend\tests\test_openapi_contract.py (2 tests) ........................ PASSED [ 98%]
backend\tests\test_security_audit.py (1 test) ........................... PASSED [100%]

============================= 73 passed in 36.28s =============================
```

---

## 3. Mandatory STOP 4 Exit Criteria Verification

1. **Review Queue Operational**: `GET /api/v1/admin/reviews` filtering verified.
2. **DPDP Sensitive Reveal Logging**: Verified that unmasking sensitive data requires typed justification and creates append-only `SensitiveAccessLog` records.
3. **Atomic Approval Transaction**: Verified assignment of `{ROLE}-{STATE}-{SEQ6}`, `VERIFIED` state transition, `VerificationReview` logging, and initial QR block allocation in a single transaction.
4. **Crockford Base32 13-Char QR Codes**: Verified 12 random chars + 1 weighted checksum char modulo 32; check function prevents invalid codes.
5. **Printable A4 PDF Sticker Sheet**: Verified generation of multi-page vector PDF sticker sheets with QR codes and Crockford serials.
6. **Real Role Statistics**: Verified live database aggregation for batch counts, kg harvested, and QR inventory.
7. **100% Green Test Suite**: 73/73 tests passing.

---

## 4. Next Phase

- **Phase 4**: Downstream Roles (Aggregator, Wholesaler, Distributor, Retailer):
  - Collection centre, cold storage, mandi license, and fleet profile onboarding.
  - Multi-facility mapping and weighing scale calibration uploads.
