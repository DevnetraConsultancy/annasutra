# 11. Backend specification

## Stack

Python, Django, Django REST Framework, PostgreSQL, a Postgres-backed job queue to begin with (add Redis only if needed). If the human prefers Java or Kotlin, Spring Boot is an equal choice. Choose by team skill, not fashion. Use `drf-spectacular` or equivalent only to check the code against `api/openapi.yaml`, not to replace it.

## Project layout

```
backend/
  manage.py
  config/            settings (base, dev, prod), urls, wsgi
  apps/
    identity/        otp, passkeys, devices, sessions, recovery
    organisations/   businesses, facilities, partner links, verification
    labels/          serial blocks, binding, void, reissue
    lots/            lots, genealogy, containers
    custody/         dispatch, receive, dispute, handover state machine
    quality/         inspections, evidence, certificates
    inventory/       balances, tolerance, discrepancy flags
    ledger/          events, hash chain, anchoring, verification
    publicview/      builds public_view rows; separate read-only public site
    alerts/          rules, review queue, notifications
    reporting/       exports, recall reports
  tests/
```

Each app exposes a small service layer. Views call services. Apps do not reach into each other's tables except through those services.

## The single write path

Every command goes through one function pattern:

1. Authenticate and resolve the organisation. Set the database session variable `app.org_id` (row-level security).
2. Check idempotency: if the event ID exists, return the stored result.
3. Open one transaction. Lock the lot row (`select_for_update`).
4. Validate state, custody, quantities, signature, tolerance.
5. Append the event with the next `lot_seq`, compute `event_hash = H(prev_hash || canonical_event)`.
6. Update lot state, balance, handover.
7. Queue jobs: alerts, public view refresh, notifications.
8. Commit. Return the result.

Any failure rolls back everything. No partial writes.

## Hash chain and anchoring

- Canonical serialisation of the event (sorted keys, fixed number formatting) is hashed with SHA-256, chained per lot.
- Nightly job re-verifies chains and recomputes a daily Merkle root of all lot head hashes. It writes the root to the external write-once bucket in a **separate cloud account** and records it in `hash_anchor`. A mismatch raises a HIGH alert.

## Background jobs

Public view refresh, alert rules, handover expiry (mark EXPIRED and flag gap), hash verification, daily anchor, notification sending (SMS and in-app), backups checks, log shipping.

## Public page

A separate small Django (or minimal) service using a database role that can `SELECT` only from `public_view`. Server-rendered template, no JavaScript framework, English plus Bengali and Hindi. Cached at the edge. Generic not-found page. No search or list routes. Includes the disclaimer on every page.

## Admin

Hardened Django admin reachable only through Cloudflare Access with SSO and a hardware key. Screens: verify or reject business, issue QR blocks, alert queue, recall management, audit export. Event and ledger tables are read-only. A correction goes through the same correction rule with two approvers. Every admin action is logged and visible to the Auditor role.

## Settings and secrets

12-factor settings from environment variables. `.env.example` with fake values only. Secrets from the cloud secrets manager. Debug off in production. Secure cookies for the admin. Strict allowed hosts. Rate limiting at Cloudflare and again in the app.

## Notifications

In-app and push for dispatch, receive, dispute, recall. SMS fallback for key events. SMS in India needs sender registration [verify current requirements]. Cap messages per number per day.

## Observability

Structured JSON logs without personal data. Request IDs. Error tracking. Metrics for sync rejects, handover times, alert counts, job lag. Logs retained at least 180 days in an Indian region store.
