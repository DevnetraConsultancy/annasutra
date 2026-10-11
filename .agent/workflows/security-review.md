# /security-review
Review the repository against docs/07_security_privacy_compliance.md, OWASP ASVS 5.0 and OWASP MASVS.
Check especially: authorisation on every endpoint (cross-business access), row-level security, the single write path, append-only events, idempotency, hash chain and anchor, secrets in code or git history, logging of personal data, local database encryption, key handling, backups disabled on the phone, public page access limits, rate limits, dependency risks.
Report findings by severity (critical, high, medium, low) with file and line, a proposed fix, and how to test it. Do NOT change code until I approve.
