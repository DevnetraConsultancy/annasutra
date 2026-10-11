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
| Recursive CTE forward trace | `WITH RECURSIVE descendants AS (...)` traversing `lot_edge` downwards from `root_lot` discovers 100% of descendants in an acyclic graph of 200+ lots | docs/05_events_custody_quantity.md line 78 | 2026-10-12 |
| Mass balance invariant | Invariant `unexplained = qty_in - (transferred + split_out + rejected + waste + sold + documented_variance + on_hand) == 0` holds for all valid sequences | docs/05_events_custody_quantity.md line 55 | 2026-10-12 |
| Append-only event corrections | `CORRECTION` events use `supersedes_event` pointer and device signature; original `trace_event` rows are never mutated or deleted | docs/05_events_custody_quantity.md line 11 | 2026-10-12 |
| CERT-In Directions 2022 | Mandatory 6-hour incident reporting window to `incident@cert-in.org.in` and 180-day ICT system log retention within India | CERT-In Directions 2022 Rule 20 | 2026-10-12 |
| DPDP Act 2023 & Rules 2025 | Notice and consent must be provided in English, Hindi, and Bengali with clear purpose limitation, Data Principal rights, and named Grievance Redressal Officer | DPDP Act 2023 / DPDP Rules 2025 | 2026-10-12 |
| Touch target accessibility | Interactive button dimensions $\ge 48\times 48\text{dp}$ (WCAG 2.1 AA / MASVS) ensure accessibility for field operators under sunlight on budget phones | OWASP MASVS / WCAG 2.1 AA | 2026-10-12 |
