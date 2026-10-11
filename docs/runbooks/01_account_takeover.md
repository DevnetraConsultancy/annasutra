# Runbook 01: Account Takeover & Device Revocation

## Severity: HIGH
## Trigger
- User reports stolen phone or unauthorized handover confirmation.
- Automated alert: Sudden login from unfamiliar IP with multiple failed passkey attempts followed by SMS fallback.

## Immediate Containment Actions (< 15 Minutes)
1. **Revoke Active Device & Sessions:**
   - Run management command or database query to immediately deactivate the compromised device:
     ```sql
     UPDATE device SET is_active = FALSE WHERE device_id = '<COMPROMISED_DEVICE_UUID>';
     ```
2. **Invalidate Refresh Tokens & Cache:**
   - Blacklist all active JWT access and refresh tokens for the `user_id`.
   - Flush cached OTP attempts and passkey credentials for the phone number.
3. **Audit In-Flight Handovers:**
   - Check if any handovers were accepted or lots dispatched by the compromised device in the last 24 hours:
     ```sql
     SELECT * FROM trace_event WHERE device_id = '<COMPROMISED_DEVICE_UUID>' AND recorded_at > NOW() - INTERVAL '24 HOURS';
     ```
   - If unauthorized handover found, flag lot with `DISPUTED` state and open an administrative audit alert.

## Recovery Procedure
1. Require the verified organisation owner or field cooperative manager to confirm the farmer/staff identity in person.
2. Issue a new enrollment OTP with an enforced 24-hour cooling delay.
3. Re-enroll new hardware passkey / device key on the replacement device.
