# Runbook 03: Hash Chain Mismatch / Tampering Alert

## Severity: CRITICAL
## Trigger
- Nightly cryptographic verification job (`python manage.py verify_hash_chain`) fails.
- Recomputing `compute_event_hash(prev_hash, event_type, seq, payload)` produces a hash that does not match `event_hash` or `head_hash` on a lot.
- PostgreSQL database error: attempt to modify or delete a row in `trace_event` caught by trigger.

## Immediate Containment Actions (< 15 Minutes)
1. **Freeze Ledger Operations:**
   - Put affected lot in `DISPUTED` state:
     ```sql
     UPDATE lot SET state = 'DISPUTED' WHERE lot_id = '<AFFECTED_LOT_UUID>';
     ```
2. **Export Forensic Audit Snapshot:**
   - Dump all `trace_event` rows for the affected lot along with PostgreSQL transaction commit logs.
   - Compare with the latest daily external anchor stored in the write-once cloud bucket (`hash_anchor`).
   - Identify the exact block or sequence number where divergence occurred.
3. **Database Access Audit:**
   - Review PostgreSQL connection logs for unauthorized superuser queries bypassing Django application role.
   - Rotate database master credentials immediately if unauthorized DB access is suspected.

## Post-Incident
1. If tampering was an external cyber attack: Trigger Runbook 04 (CERT-In Data Breach Escalation) within the 6-hour window.
2. Restore database from known good immutable backup and re-anchor head hashes.
