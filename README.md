# AnnaSutra: handover package

A complete design package for building AnnaSutra, a farm-to-consumer traceability app (one Flutter codebase for Android and Web, iOS later) with a Django backend, ready to hand to Google Antigravity.

**Start here:** `HANDOVER_GUIDE.md` (for you, the human), then `docs/Core/annasutra_entity_console_architecture.md` (the locked Gold Standard blueprint, for every agent).

## Contents

```
README.md                  this file
HANDOVER_GUIDE.md          how to give this to Antigravity, settings, prompts, review loop
AGENTS.md                  rules the agent must follow (copy in .agent/rules/)
.agent/rules/              workspace rules
.agent/workflows/          /plan-phase, /implement-phase, /write-tests, /security-review, /release-checklist
docs/Core/annasutra_entity_console_architecture.md   the ONLY spec under docs/ (Gold Standard, locked)
db/schema.sql              PostgreSQL schema (loaded and constraint-tested on PostgreSQL 16)
api/openapi.yaml           API contract, 35 paths (validated as OpenAPI 3.0.3)
assets/diagrams/           12 diagrams as SVG and PNG
tools/gen_diagrams.py      regenerates the diagrams
tools/gen_openapi.py       regenerates api/openapi.yaml
```

## Diagram index

| File | Shows |
|---|---|
| 01_supply_chain_overview | Six stages and the approval chain |
| 02_system_architecture | Components, edge, database, safety nets |
| 03_mobile_app_layers | Flutter app layers |
| 04_flow_master | Login, verification, scan, permission check |
| 05_flow_farmer | Create batch and hand over |
| 06_flow_middleman | Receive, difference check, confirm, next step |
| 07_flow_consumer_admin | Public page and admin tasks |
| 08_lot_state_machine | Batch states |
| 09_qr_lifecycle | Serial issue, bind, reissue, new QR on split |
| 10_offline_sync | Outbox and sync |
| 11_security_layers | Eight layers |
| 12_delivery_phases | Phases 0 to 4 |

## What was and was not checked

Checked while preparing this package: the SQL schema loads and its key constraints behave as designed on PostgreSQL 16; the OpenAPI file validates; the diagrams render. Researched on 11 October 2026: DPDP timeline, CERT-In directions, OWASP ASVS version, ISO 22005 edition, Flutter passkey platform minimums, Antigravity settings. **Not checked:** GS1, FSSAI, APEDA and e-NAM details, store requirements, any code (none exists yet). Items marked [verify] must be confirmed against official sources.

No software is flawless. This design reduces risk and makes failures visible. It cannot prove what is physically inside a package.
