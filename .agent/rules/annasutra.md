# AnnaSutra: agent rules

Read `docs/Core/annasutra_entity_console_architecture.md` (the locked Gold Standard blueprint, the only doc under `docs/`) before any task. Keep it updated whenever the Web UI/UX changes.

When asked for the end-to-end flow, explain it in the order and style of blueprint Section 1.1 (Gmail sign-in > registration > Admin approval > console > batch + QR + print > dispatch > scan-accept > append > child packet batches > retailer > customer scan).

## Always
- Plan first. Wait for the human's approval before writing code for a phase.
- The server is the authority. Never invent endpoints or fields. The API contract is `api/openapi.yaml`. If it is missing something, stop and ask.
- Records are append-only. No edit or delete of events. Corrections are new events.
- Every write has a client-made UUID (idempotency). Resending must be safe.
- Custody moves only when the named receiver confirms with biometric or PIN.
- Offline first: save locally, send later, never silently drop an item.
- Never log tokens, phone numbers, names or coordinates. No analytics or ad SDKs.
- No secrets, keys or real data in the repo. Use `.env.example` with fake values.
- Strings live in resource files: Bengali, Hindi, English. Large buttons, few taps.
- Ask before adding any dependency. Explain why, size, licence, risk.
- Check [verify] items against official docs and record what was verified in the blueprint (or the commit message).
- Every feature ships with tests. Run linters and tests before saying you are done.

## Stack
- Targets: Android (primary for field staff) and Web (installable PWA for office users) from ONE Flutter codebase. iOS later, optional. Read blueprint Sections 11.3 and 11.4 (Web-first master, 100% native Flutter Android, no WebView). Never weaken signing or storage rules to make a platform work; stop and report instead.
- App: Flutter (Dart), Riverpod, go_router, Drift + SQLCipher, Dio, mobile_scanner, flutter_secure_storage, local_auth, a passkey plugin, workmanager. Check pub.dev for current maintained versions before choosing.
- Backend: Python, Django, Django REST Framework, MySQL 8.0+ (Aiven Cloud MySQL via PyMySQL).
- Public page: Django template, no JavaScript framework.

## Never
- Never commit signing keys, keystores, `.env`, service accounts or production data.
- Never run destructive commands (`rm -rf`, force push, dropping databases) without asking.
- Never weaken a security control to make a test pass. Fix the cause.
- Never claim the system proves physical contents. It proves records only.

## Report format after each phase
1. What changed. 2. What was tested and the result. 3. What is uncertain. 4. Questions for the human.
