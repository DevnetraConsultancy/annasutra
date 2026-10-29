# AnnaSutra: Farm-to-Consumer Agri-Traceability Platform

A complete design and implementation package for AnnaSutra, a farm-to-consumer traceability platform featuring a Django backend, unified web console, and Flutter mobile client.

---

## Quickstart: Run Locally in 1 Minute

Anyone who clones this repository from GitHub can run it immediately on localhost with zero external services required (uses local SQLite out of the box).

### Option A: One-Click Runner (Recommended)

* **Windows:** Double-click `run_local.bat` or run in terminal:
  ```cmd
  run_local.bat
  ```
* **macOS / Linux:** Run in terminal:
  ```bash
  chmod +x run_local.sh
  ./run_local.sh
  ```

This automatically configures the Python virtual environment, installs dependencies, applies database migrations, seeds verified demo data, opens your browser, and starts the local server.

---

### Option B: Manual CLI Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply migrations & seed initial demo data
python manage.py migrate
python manage.py seed_demo_data

# 4. Start the development server
python manage.py runserver 127.0.0.1:8000
```

---

### Local Access Points & Credentials

| Service / Interface | Local URL | Default Credentials / Context |
|---|---|---|
| **Web Portal & Entity Console** | [http://localhost:8000/](http://localhost:8000/) | Live 5-tier operational simulator & role registration |
| **Traceable Lot Provenance Story** | [http://localhost:8000/q/DEMO-LOT-001](http://localhost:8000/q/DEMO-LOT-001) | Verified consumer timeline, GI tag, quality certificates |
| **System Health Check** | [http://localhost:8000/health](http://localhost:8000/health) | Probe returning `{"status": "healthy", "database": "connected"}` |
| **Django Admin Portal** | [http://localhost:8000/admin/](http://localhost:8000/admin/) | `admin` / `admin123` |
| **Admin Console Identity** | [http://localhost:8000/](http://localhost:8000/) | `devnetraconsultancy@gmail.com` |
| **Android APK Download** | [http://localhost:8000/download/apk](http://localhost:8000/download/apk) | Direct APK download route |

> **Database Configuration**: By default, local execution uses SQLite (`backend/annasutra.sqlite3`). To connect to an external Aiven Cloud MySQL 8.0+ or Docker instance, create a `.env` file or export `DATABASE_URL="mysql://user:password@host:port/dbname"` as detailed in `.env.example`.

---

## Contents

```
README.md                  this file
manage.py                  root CLI wrapper for Django commands
run_local.bat              one-click runner for Windows
run_local.sh               one-click runner for macOS/Linux
HANDOVER_GUIDE.md          how to give this to Antigravity, settings, prompts, review loop
AGENTS.md                  rules the agent must follow (copy in .agent/rules/)
.agent/rules/              workspace rules
.agent/workflows/          /plan-phase, /implement-phase, /write-tests, /security-review, /release-checklist
docs/Core/annasutra_entity_console_architecture.md   the ONLY spec under docs/ (Gold Standard, locked)
db/schema_mysql.sql        Aiven Cloud MySQL 8.0+ schema (InnoDB, utf8mb4, append-only triggers & constraints)
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

Checked while preparing this package: the MySQL 8.0+ SQL schema (`db/schema_mysql.sql`) loads and its key constraints behave as designed on Aiven Cloud MySQL 8.0+; the OpenAPI file validates; the diagrams render. Researched on 11 October 2026: DPDP timeline, CERT-In directions, OWASP ASVS version, ISO 22005 edition, Flutter passkey platform minimums, Antigravity settings. **Not checked:** GS1, FSSAI, APEDA and e-NAM details, store requirements, any code (none exists yet). Items marked [verify] must be confirmed against official sources.

No software is flawless. This design reduces risk and makes failures visible. It cannot prove what is physically inside a package.
