# Runbook 02: Fake or Cloned QR Code Wave

## Severity: HIGH
## Trigger
- Automated alert: `ScanLog` records identical QR serial scanned at impossible geographic distances within minutes.
- Public scans spike on a lot that has already reached `CLOSED` state.
- Mandi staff reports duplicate printed QR labels circulating in the physical market.

## Immediate Containment Actions (< 30 Minutes)
1. **Identify the Target Serial(s):**
   - Query `ScanLog` to identify duplicate scans and IP clusters:
     ```sql
     SELECT serial, COUNT(*), array_agg(scanned_at) 
     FROM scan_log 
     WHERE scanned_at > NOW() - INTERVAL '1 HOUR' 
     GROUP BY serial 
     HAVING COUNT(*) > 10;
     ```
2. **Quarantine the Lot:**
   - Mark the lot state as `DISPUTED` to block further downstream handovers, splits, or retail sales:
     ```sql
     UPDATE lot SET state = 'DISPUTED' WHERE public_code = '<SUSPICIOUS_SERIAL>';
     ```
3. **Notify Current Custodian:**
   - Dispatch immediate SMS and app alert to the registered custodian organisation.
   - Halt physical truck dispatch until physical seals and weight measurements are cross-verified.

## Resolution
1. Physically inspect packaging, security seals, and printed QR sticker books.
2. If label was cloned: Void the compromised label (`UPDATE qr_label SET status = 'VOID' WHERE serial = '...'`).
3. Issue a new replacement QR label via `POST /v1/lots/{code}/label-reissue` to restore verified chain of custody.
