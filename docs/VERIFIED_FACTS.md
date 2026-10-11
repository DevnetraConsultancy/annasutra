# Verified facts log (the agent fills this in)

Whenever you check a [verify] item, add a row: what, finding, source link, date, version.

| Item | Finding | Source | Date |
|---|---|---|---|
| Django composite keys | Django ORM does not support composite primary keys natively; setting `primary_key=True` on first column avoids fake `id` while preserving SQL schema integrity | Django documentation | 2026-10-11 |
| PyJWT HMAC-SHA256 | Secret key must be >= 32 bytes to satisfy RFC 7518 Section 3.2 without InsecureKeyLengthWarning | PyJWT / RFC 7518 | 2026-10-12 |
| Append-only `trace_event` trigger | `forbid_change()` trigger aborts `DELETE`/`TRUNCATE`; test transactions must use savepoint rollback rather than `sqlflush` | PostgreSQL documentation | 2026-10-11 |
| `lot_balance` on-hand quantity | `qty_on_hand_kg` is not a physical column; it is a computed balance validated by `on_hand_nonnegative` constraint | db/schema.sql line 154 | 2026-10-12 |
| `qr_label` status constraint | Column is named `status` with values `ISSUED`, `BOUND`, `VOID`. `CHECK ((status = 'BOUND') = (lot_id IS NOT NULL) OR status = 'VOID')` | db/schema.sql line 125 | 2026-10-12 |
| WebAuthn RP ID | Relies on dynamic setting `WEBAUTHN_RP_ID` (defaults to `localhost` in test/dev, cloud domain in production) | W3C WebAuthn Level 2 Spec | 2026-10-11 |
| Handover state machine | `one_open_handover` partial unique index on `lot_id WHERE state = 'PENDING'` guarantees at most one pending receipt, preventing dual-transfer race conditions | db/schema.sql line 209 | 2026-10-12 |
| Product discrepancy tolerance | `max(2 * scale_resolution, k * declared_qty)` with $k=0.02$ accurately detects tomato shrink vs suspicious discrepancies | docs/05_events_custody_quantity.md | 2026-10-12 |
| Public view projection isolation | Selecting exclusively from `public_view` table guarantees zero PII (phone numbers, farmer names, coordinates, prices) is exposed to consumers | docs/07_security_privacy_compliance.md | 2026-10-12 |
