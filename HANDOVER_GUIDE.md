# Handover guide: giving AnnaSutra to Google Antigravity

**Target:** one Flutter codebase that builds an **Android app** and a **web app** (installable in the browser), plus the Django backend and a tiny public consumer page. iOS can come later from the same code.

Antigravity is an AI coding tool that can plan and write code. It can build most of AnnaSutra, but a person must review every phase, test on real phones, and own the security and legal decisions. Do not ask for "the whole app" in one prompt.

Antigravity announced version 2.0 and a command-line tool at Google I/O 2026, so menu names may differ from this guide. Check https://antigravity.google/docs when a setting is not where described.

## Step 1. Accounts and things you need

| Need | Why |
|---|---|
| Google account with Antigravity access | The tool itself |
| GitHub (or similar) account, private repository | Code storage, CI |
| A domain name you control | Public QR links, API, and passkey domain association files |
| Cloudflare account | Edge protection |
| Cloud account in an Indian region (plus a **second, separate** account for backups and the daily hash copy) | Hosting, tamper evidence |
| SMS provider (India sender registration may be needed) [verify] | Login codes |
| Google Play developer account | Android release [verify cost and rules] |
| Apple developer account and a Mac (or a macOS CI service) | **Only if you add iOS later** [verify]. Not needed for Android and Web |
| A lawyer for DPDP, CERT-In and consent text | Compliance |
| A real low-cost Android phone (and an iPhone if you ship iOS) | Real testing |

## Step 2. Prepare the project folder

1. Unzip `annasutra-handover.zip`. Keep the folder structure.
2. Create a private Git repository and commit the contents (`git init`, add, commit, push).
3. Keep `AGENTS.md`, `.agent/`, `docs/`, `db/`, `api/`, `assets/` and `tools/` at the repo root. The agent will add `backend/` and `mobile/`.

## Step 3. Configure Antigravity (safe settings)

Open the unzipped folder as the workspace. Open settings (Ctrl+, on Windows or Linux, Cmd+, on Mac).

| Setting | Choose | Why |
|---|---|---|
| Overall mode | **Review-driven development** (the agent asks for review often) | You see plans before code |
| Terminal execution policy | **Request review**, or an allow list | Agent only runs approved commands |
| Allow list (if used) | `git status`, `git diff`, `flutter analyze`, `flutter test`, `dart format`, `python manage.py test`, `pytest`, `ruff`, `pip install -r requirements.txt` | Safe, routine commands |
| Deny list | `rm -rf`, `curl ... \| sh`, `git push --force`, anything touching keys, keystores or `.env` | Prevents damage |
| Review policy | Request review for plans and for files about auth, keys, permissions, sync, hashing | These are security-critical |
| JavaScript or browser execution | Disabled, or request review | You do not need it for this work |
| **Avoid** | "Always proceed", agent-driven or any auto-run mode | Too risky for a security-sensitive product |

Rules and workflows: this package already includes `AGENTS.md` and `.agent/rules/annasutra.md` (the rules) and `.agent/workflows/` (saved prompts you run with a slash command: `/plan-phase`, `/implement-phase`, `/write-tests`, `/security-review`, `/release-checklist`). Antigravity guides say workspace rules live in `.agent/rules/` and workflows in `.agent/workflows/`. If your version looks elsewhere (for example it reads only `AGENTS.md`), keep both copies. **[verify in the current docs]**

Android and Flutter help: Google announced an Android command-line tool and open-source Android skills at I/O 2026. Install them if your version offers them, and keep Android Studio (and Xcode on a Mac) for emulators and device builds. Use the strongest model your account offers for planning.

## Step 4. Give it the idea (first prompt)

**4A. Safe default: one phase at a time.** Start a **new conversation for each phase** so the context stays clean. First conversation:

```
You are building AnnaSutra, a traceability app for Android and Web (one Flutter codebase) with a Django backend. Read AGENTS.md and every file
in docs/ (start with docs/00_MASTER_BRIEF.md), plus api/openapi.yaml and db/schema.sql.
Do not write code yet.
Run /plan-phase for Phase 0 (see docs/14_phases_and_prompts.md). List every dependency
with reason, size, licence and risk. List questions and anything you must verify.
Stop and wait for my approval.
```

Then approve or correct the plan, and run `/implement-phase` for Phase 0. Repeat for Phases 1 to 4 using the prompts in `docs/14_phases_and_prompts.md`.

**4B. "In one go" mode (continuous run with four mandatory stops).** If you want Antigravity to build everything in one continuous run, paste this once. Do not remove the stops. Security-critical code cannot be verified without a human and real phones.

```
Build AnnaSutra end to end in one continuous run, following the docs exactly.
Targets: Flutter for Android and Web from ONE codebase, Django backend, tiny public page.
Read AGENTS.md, docs/00_MASTER_BRIEF.md and every file in docs/, plus api/openapi.yaml
and db/schema.sql. Never invent endpoints, fields, standards or legal duties.

Work phase by phase (docs/14). Each phase on its own branch, all tests green before the
next phase starts. After each phase write reports/phase-N.md (what changed, what was
tested with results, what is uncertain, questions). Treat these reports as your memory if
your context gets long.

STOP 1: before any code, give me ONE master plan for Phases 0 to 4 (dependencies with
reason, size, licence, risk; [verify] items; risks; questions). Wait for my approval.
STOP 2: before writing signing and login code (Android Keystore device key, WebAuthn on web),
show me the design and wait for approval.
STOP 3: at the end of Phase 2 (first farmer to retailer handover) give me a demo script
and wait for my review on real phones and a browser.
STOP 4: after the Phase 4 security review (/security-review), before any release steps.

Between stops you may continue without asking, unless the docs are missing or conflicting:
then stop and ask. Never weaken a security rule to make a test or a platform work.
```

**Honest note on "one go":** Antigravity can run long tasks, but long runs lose context and can drift. That is why each phase is its own branch with a written report, and why the four stops stay. If you remove them, you risk a large codebase with security mistakes that are expensive to find later. The review-driven setting in Step 3 will also pause for your approval at times. That is expected.

## Step 5. The loop for every phase

1. **Plan** (`/plan-phase`). You read it, answer questions, correct mistakes.
2. **Implement** (`/implement-phase`). The agent works on a branch and reports.
3. **Review.** You (or a developer you trust) read the diff. Pay extra attention to anything about login, keys, permissions, sync, hashing, and the public page.
4. **Test.** Run it on a real low-cost phone. Try airplane mode. Try a second phone as the receiver.
5. **Security check** (`/security-review`) at the end of Phases 2, 3 and 4.
6. **Merge** only when the phase gate checklist in `docs/14` is ticked.

## Step 6. What you must do yourself (do not delegate)

- Create and hold signing keys and production secrets. Never paste them into Antigravity or the repo.
- Use fake data in development. Never real farmer data.
- Legal review of consent text, DPDP and CERT-In duties.
- External penetration test before the pilot.
- Store submissions, privacy forms and developer accounts.
- Field testing and training with real farmers, in Bengali.
- Decisions listed in `docs/15_risks_open_questions.md`.

## Step 7. When the agent goes wrong

| Symptom | What to do |
|---|---|
| It invents an endpoint or field | Point it to `api/openapi.yaml`. If the contract is truly missing something, change the contract yourself (edit `tools/gen_openapi.py`, rerun, validate), then tell the agent |
| It wants to add many dependencies | Ask it to justify each and pick the smallest set |
| It weakens a rule to pass a test | Reject. Tell it to fix the cause (see AGENTS.md) |
| Context gets long and sloppy | Start a new conversation. Paste only the phase prompt. It re-reads the docs |
| Passkeys or hardware signing fail on a phone | Prototype on the exact phone model early. Use the device-key fallback for older phones |
| It claims something works without running it | Ask for the test output. Run it yourself |

## Step 8. Suggested order of the human work

Week 0: accounts, domain, lawyer, device phones. Phase 0 and 1: backend and app foundations. Phase 2: first end-to-end handover on real phones. Phase 3: split, merge, recall. Phase 4: security, pen test, pilot readiness. Then the pilot described in `docs/01_product_and_scope.md`.

## Honest limits

An AI agent can write a lot of correct code, but it can also write plausible wrong code. The security design in this package reduces risk, it does not remove it. Never describe AnnaSutra as "flawless" or as proving what is physically inside a package.
