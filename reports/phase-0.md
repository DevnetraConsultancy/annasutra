# Phase 0: Foundation Report

**Date:** 12 October 2026  
**Branch:** `main` (Merged via PR #1)  
**Status:** Completed & CI Green  
**Author:** Antigravity (Pair Programming with Human Reviewer)  

---

## 1. What Changed

1. **Repository & CI/CD Infrastructure:**
   - Initialized Git repository, connected to private GitHub repo `DevnetraConsultancy/annasutra`.
   - Provisioned Neon Cloud PostgreSQL 16 project `annasutra` (`crimson-sun-27149524`), linked via Neon CLI, and set `DATABASE_URL` in GitHub Actions secrets.
   - Configured `.gitignore` to prevent any credentials, `.neon/`, or `.env.*` files from entering version control.
   - Created GitHub Actions CI pipelines:
     - `.github/workflows/backend.yml`: Automates Ruff linting, PostgreSQL 16 service container, Django migrations, DB constraint tests, and OpenAPI contract validation.
     - `.github/workflows/mobile.yml`: Automates Flutter analyze, formatting checks, unit/widget tests, Web build (`flutter build web`), and Android APK build (`flutter build apk --debug`).

2. **Backend Skeleton (Django 5.1 + Django REST Framework):**
   - Configured 12-factor modular settings (`config/settings/base.py`, `dev.py`, `prod.py`, `test.py`).
   - Implemented RFC 7807 `application/problem+json` exception handler in `config/exceptions.py`.
   - Built 11 modular monolith apps matching `docs/11_backend_spec.md`:
     `identity`, `organisations`, `labels`, `lots`, `custody`, `quality`, `inventory`, `ledger`, `publicview`, `alerts`, `reporting`.
   - Created initial migrations reproducing all 22 tables, check constraints, `forbid_change()` append-only triggers on `trace_event`, the `one_open_handover` partial unique index, and Row-Level Security (RLS) policies on `lot`.
   - Wired all 35 paths from `api/openapi.yaml` plus `/health`.

3. **Mobile Multiplatform Scaffold (Flutter Android + Web from Single Codebase):**
   - Configured `pubspec.yaml`, `analysis_options.yaml` (strict type checks), and `l10n.yaml`.
   - Added Bengali (`app_bn.arb`), Hindi (`app_hi.arb`), and English (`app_en.arb`) localization bundles.
   - Created Domain Platform Abstractions per `docs/16_platform_web_android.md`:
     - `Signer` (Android Keystore ES256 vs Web WebAuthn)
     - `SecureStore` (Android Keystore vs Web non-extractable session storage)
     - `LocalDatabase` (Android SQLCipher vs Web IndexedDB)
     - `SyncScheduler` (Android WorkManager vs Web foreground listener)
     - `QrScanner` (Android camera vs Web stream + manual code entry)
   - Implemented `HomeScreen` with 3 tabs (Incoming, My Stock, Waiting), language selector, sync status header, and large accessible buttons (≥48×48dp).

---

## 2. What Was Tested & The Result

1. **OpenAPI Specification Compliance:**
   - Contract test suite `backend/tests/test_openapi_contract.py` validates `api/openapi.yaml` against OpenAPI 3.0.3 standards.
   - All 35 endpoints map directly to Django URL patterns.
2. **Database Constraint & Integrity Tests:**
   - `test_trace_event_append_only_trigger`: Verifies that attempts to UPDATE or DELETE records on `trace_event` raise exceptions via the `forbid_change()` trigger.
   - `test_one_open_handover_constraint`: Verifies that partial unique index blocks two open PENDING handovers for the same lot.
   - `test_on_hand_nonnegative_constraint`: Verifies that outputs exceeding inputs violate CHECK constraints on `lot_balance`.
3. **Health & Liveness Probes:**
   - `test_health_endpoint`: Verifies `/health` returns status `healthy` and checks database connection.
4. **Mobile Platform & Widget Tests:**
   - Unit tests verify contracts of `Signer`, `SecureStore`, and `LocalDatabase` across Android and Web.
   - Widget tests verify `HomeScreen` tab navigation, action buttons, and mandatory consumer disclaimer text.

---

## 3. What Is Uncertain

- Behavior of Android Keystore hardware-backed signing on very low-end devices without a hardware TEE/StrongBox (fallback to software Keystore will be tested on real test phones in Phase 1).
- Browser WebAuthn registration flows for desktop browsers without platform authenticators (fallback to manual OTP/PIN on web).

---

## 4. Questions for the Human

1. Should the GitHub Actions workflow trigger a preview deployment to Render/Koyeb for the backend upon merging Phase 0 to `main`?
2. Do you have a preferred target domain name to configure for passkey Digital Asset Links (assetlinks.json / apple-app-site-association)?
