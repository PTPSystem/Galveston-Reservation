# Galveston Reservation

Unified tooling to manage a short‑term rental property in Galveston by: (1) displaying Google Calendar availability, (2) orchestrating the end‑to‑end operational workflow (booking → prep → guest stay → turnover), and (3) automatically cross‑checking an external/online calendar source to ensure no bookings are missed on Google Calendar.

> Status: Initial README scaffold (no committed implementation code yet). This document defines the intended architecture & workflows so code can be added consistently.

## ✨ Core Functions

1. Show calendar from Google Account
   - Read reservations / events from a designated Google Calendar (e.g. `Primary` or a dedicated rental calendar) and present them in a human‑friendly view (CLI, web, or dashboard).
2. Short‑term rental workflow automation
   - Standardize tasks triggered by each booking lifecycle stage (booking confirmation, pre‑arrival messaging, check‑in, mid‑stay, checkout, cleaning/turnover, maintenance follow‑ups).
3. External calendar consistency check
   - Poll or fetch an online calendar (e.g. listing platform iCal feed / partner portal / scraped availability page) and reconcile it against Google Calendar to detect missing or divergent events.

## 🧭 Intended Architecture (Proposed)

| Layer | Responsibility |
|-------|----------------|
| Data Sources | Google Calendar API, External iCal / HTML feed, Local cache (SQLite / JSON) |
| Ingestion | Scheduled fetchers (cron / GitHub Actions / local script) |
| Core Logic | Booking normalization, diff engine, workflow state machine |
| Notifications | Email (SMTP), SMS (Twilio), or Chat (Slack / Teams) adapters |
| Presentation | CLI reports, optional lightweight web dashboard |

> Adjust once actual language / frameworks are chosen.

## 🔐 Prerequisites

Because implementation details are not yet committed, below are assumed prerequisites:

- A Google Cloud project with Calendar API enabled.
- OAuth 2.0 credentials (Service Account or OAuth Client) granting read/write access to the rental calendar.
- Access to the external calendar feed (public iCal URL, API key, or page URL for scraping).
- Runtime environment (pick one when coding begins):
   - Python 3.11+ (suggested) OR
   - Node.js 20+ OR
   - Another stack (document here once decided).

## 🗂 Data Model (Conceptual)

Minimal normalized booking/event structure:

```json
{
  "id": "ext-1234" ,           // Stable unique identifier
  "source": "google|external",
  "start": "2025-08-14T15:00:00Z",
  "end": "2025-08-18T17:00:00Z",
  "guestName": "Jane Doe",
  "status": "confirmed|tentative|canceled",
  "notes": "Any freeform text",
  "raw": { /* Original provider payload */ }
}
```

## 🔄 Workflow Lifecycle (Draft)

| Stage | Trigger | Actions |
|-------|---------|---------|
| Booking Created | New event detected | Normalize + store; send confirmation template; schedule pre‑arrival tasks |
| Pre‑Arrival (T-3 days) | Time threshold | Send reminder, lock code provisioning, cleaning confirmation |
| Check‑In Day | Start date morning | Send welcome message & instructions |
| Mid‑Stay (optional) | Midpoint | Courtesy message, upsell opportunities |
| Checkout Day | End date morning | Send checkout procedures & review request scheduling |
| Post‑Checkout | After end | Create cleaning task; maintenance flagging; send review request |
| Discrepancy Detected | Diff engine finds missing event | Alert via configured channel |

## ✅ External Calendar Reconciliation

1. Fetch Google events for target window (e.g. next 180 days).
2. Fetch external calendar feed.
3. Normalize both → unified structure.
4. Compare on (date range overlap + guest name + length). Heuristics for fuzzy matching (e.g. ±1 hour tolerance).
5. Produce a diff report:
   - Missing in Google
   - Missing in External
   - Attribute mismatches (dates shifted, status different)
6. Persist last diff snapshot (for change tracking) and emit notifications only on new discrepancies (avoid spam).

## 🛠 Setup (Proposed Steps – adapt once stack chosen)

### 1. Clone

```bash
git clone <repo-url>
cd Galveston-Reservation
```

### 2. Environment Variables (example `.env`)

```bash
GOOGLE_PROJECT_ID=your-project
GOOGLE_CREDENTIALS_PATH=./secrets/service-account.json
GOOGLE_CALENDAR_ID=your-calendar-id@group.calendar.google.com
EXTERNAL_CALENDAR_URL=https://example.com/calendar.ics
NOTIFY_EMAIL=alerts@example.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
```
(Only include what you implement; rotate secrets appropriately.)

### 3. Credentials
 
- Create a Service Account (if server-side) with Calendar API scope (`https://www.googleapis.com/auth/calendar` or read-only variant).
- Download JSON key → place in `./secrets/` (never commit) → reference with `GOOGLE_CREDENTIALS_PATH`.
- If using OAuth user consent for write operations, implement token storage (e.g. `token.json`).

### 4. (If Python Stack Example)
 
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # (to be created)
```

### 5. First Run (Hypothetical CLI)
 
 
```bash
python scripts/fetch_google_calendar.py --days 60
python scripts/check_discrepancies.py --window 180 --format table
python scripts/run_workflow_tick.py  # processes due workflow actions
```

## 🧪 Testing Strategy (Planned)

| Test Type | Focus |
|----------|-------|
| Unit | Normalization logic, date range comparisons, workflow transitions |
| Integration | Google API fetch, external feed parse, notification send |
| Regression | Diff engine stability across edge cases (overlapping bookings, daylight savings) |

## 🚨 Edge Cases To Handle

- Overlapping bookings (platform double-book vs. split stays)
- Daylight Saving Time transitions
- Canceled or modified events (ID reuse vs new event ID)
- Partial stays (guest leaves early)
- External feed latency (stale data windows)

## 📤 Notifications (Options)

- Email (SMTP / SendGrid)
- Slack incoming webhook
- SMS (Twilio)
- Console / log only (dev mode)

## 📈 Future Enhancements

- Web UI dashboard (availability grid + discrepancy badges)
- Auto-repair (create missing Google events automatically after confirmation)
- Metrics export (Prometheus / simple CSV)
- Guest communication templates with localization
- Multi-property support (property_id dimension)

## 🧾 Project Conventions (To Decide)

| Area | Suggested Choice |
|------|------------------|
| Language | Python 3.11 (timezone handling: `pytz` / `zoneinfo`) |
| Packaging | `pyproject.toml` + `poetry` or `pip-tools` |
| Scheduler | Cron (system) or lightweight APScheduler task loop |
| Persistence | SQLite via SQLAlchemy OR plain JSON for MVP |
| Logging | Structured (JSON) using `structlog` |
| Lint/Format | `ruff`, `black`, `mypy` |

(Revise when implementation starts.)

## 🔒 Security Notes

- Never commit raw credential files.
- Principle of least privilege for Service Account.
- Rate limit external polling to respect provider terms.
- Store secrets in environment or a secret manager (GCP Secret Manager) for production.

## 🤝 Contributions

Until core code is present, contributions should focus on:

- Defining concrete data schema
- Selecting baseline tech stack
- Drafting minimal ingestion scripts

Open an issue describing the proposal before large changes.

## 📣 Getting Help

Create a GitHub Issue with:

- Description of problem
- Steps to reproduce (if runtime issue)
- Logs (with secrets redacted)

## 🗓 Changelog

- 2025-08-08: Initial README scaffold created.

---
Feel free to refine this document once implementation decisions are finalized.
