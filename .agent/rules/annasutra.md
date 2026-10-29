# AnnaSutra: agent rules

Read `docs/Core/annasutra_entity_console_architecture.md` (the locked Gold Standard blueprint, the only doc under `docs/`) before any task. Keep it updated whenever the Web UI/UX changes.

**Locked Core (`Core of AnnaSutra`, C1–C16 at the top of the blueprint):** never remove, reorder, merge, bypass or reword any step of the 16-step core chain, and always use its exact string when asked for the end-to-end flow:
"Sign in with Gmail > the login portal shows every registration this Gmail already has, with its status > the entity registers with their details > Admin approves (only now is the Unique ID created) > the entity gets its console > the entity can update more details, except KYC (KYC changes need an Admin change request) > the farmer creates a batch with all required details > mints the batch QR / barcode > prints it on Web or APK and sticks it on the delivery lot > sends a dispatch request to the next party > the next party accepts by scanning the lot QR (live photo, weight, GPS), and the farmer's record is locked > the next party adds more data to the lot > the relevant entity makes small packet batches, each with a child QR > the packets reach the retailer shop > a customer scans with the AnnaSutra APK (optional location, recorded for Admin) > the customer sees the product's origin, a short summary and its journey."

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
