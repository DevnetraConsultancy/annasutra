# 13. Test strategy and acceptance criteria

| Area | Test | Pass condition |
|---|---|---|
| Normal flow | Farmer to retailer happy path (the tomato simulation) | States and balances match `05_events_custody_quantity.md` |
| Split and merge | Children sum, merge custodians | Violations rejected |
| Duplicate and replay | Send the same event 100 times | One event stored |
| Out-of-order sync | Receive arrives before dispatch | Conflict or queued, no corruption |
| Conflicting handovers | Two receivers at once | Exactly one wins |
| Quantity imbalance | Outputs exceed input | Rejected |
| Invalid genealogy | Cycle or self-parent | Rejected |
| Unauthorised access | Cross-business read and write on every endpoint | 403 or 404 |
| QR cloning | Scan by non-custodian, distant scans | Alert fires |
| Data corruption | Change a stored row in a test database | Nightly hash check fails and alerts |
| Backup restore | Full restore and chain verify | Meets recovery targets |
| Partial outage | Kill API or database during sync | No loss, replay safe |
| Recall completeness | Seeded graph of 200 lots | Query finds 100% of descendants |
| Public page | Automated check of response fields | Zero forbidden fields |
| Offline | Airplane mode for a full receive and dispatch, then sync | Items reach the server and the UI matches |
| Low-end device | Core flows on a 2 to 3 GB phone | Handover recorded in under 60 seconds |
| Accessibility and language | Bengali, Hindi, English; large text | No truncation, screen reader labels |

## Kinds of tests

- **Property tests** for mass balance: no sequence of valid actions makes on-hand negative or lets outputs exceed inputs.
- **Race tests** with parallel requests on the same lot.
- **Database tests** against a real PostgreSQL: the constraints in `db/schema.sql` must fail as designed. (They were checked once on PostgreSQL 16 while preparing this package. Rerun them in CI.)
- **Contract tests** that compare the running API to `api/openapi.yaml`.
- **Mobile tests**: unit tests for rules, widget tests for key screens, integration tests for the offline outbox.
- **Load tests** for mandi peak hours.
- **Usability tests** in Bengali with real farmers and traders.
- **External penetration test** of backend and app before the pilot, retest after fixes.

## Acceptance criteria for the MVP

1. A batch can travel from farmer to retailer on real phones, with each handover confirmed by the receiver.
2. Offline for an hour, then sync, loses nothing.
3. No account can read or write another business's data.
4. The public page shows only the allowed fields.
5. Editing a stored event is impossible through the app or the admin, and a forced database change is detected within a day.
6. A recall trace from any lot returns all descendants and where unsold stock sits.
7. A restore from backup succeeds and passes hash verification.

## Critical failure modes the tests must cover (at least 15)

Double dispatch race; negative stock; duplicate event on retry; out-of-order offline sync; backdated events; sender-receiver collusion (detect patterns only); fake label on unrelated produce; orphan lots; genealogy cycle; misleading consumer claims; unauthorised correction; database administrator tampering; stolen phone; lost unsynced data; ransomware or region outage; scale tampering; public scraping; blind "matches" tapping; public view leaking commercial data; reconciliation false alarms.
