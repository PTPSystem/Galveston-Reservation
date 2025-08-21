# Galveston Reservation System

A complete Flask-based booking management system for short-term rental properties in Galveston. Features real-time availability checking, automated email workflows, Google Calendar integration, and a multi-step approval process.

## 🚀 Status: Production Ready

The system is fully implemented and running at `https://str.ptpsystem.com` with complete booking workflow, email notifications, and calendar synchronization.

## ✨ Core Features

1. **Real-time Calendar Display**
   - Integration with Google Calendar API for live availability checking
   - Visual calendar interface showing booked and available dates
   - Automatic conflict detection for booking requests

2. **Multi-step Booking Workflow**
   - Guest submits booking request through web form
   - Admin receives email with approve/reject links
   - Automatic calendar event creation upon approval
   - Email notifications to all stakeholders

3. **Email Automation**
   - Booking approval/rejection notifications
   - Guest confirmation emails
   - Team notifications for new bookings
   - Secure token-based approval links

## 📁 Project Structure

```
Galveston-Reservation/
├── app/                    # Main Flask application
│   ├── models/            # Database models
│   ├── routes/            # API endpoints and routes
│   ├── services/          # Business logic (email, calendar)
│   ├── static/            # CSS, JS, images
│   └── templates/         # HTML templates
├── docs/                  # Documentation files
│   ├── DEPLOYMENT.md      # Deployment instructions
│   ├── GOOGLE_CALENDAR_SETUP.md
│   └── CLOUDFLARE_SETUP.md
├── scripts/               # Utility scripts
│   ├── init_db.py         # Database initialization
│   ├── smart_calendar_sync.py
│   └── deployment scripts
├── tests/                 # Test files and test data
└── secrets/               # Credentials (git-ignored)
```

## 🛠 Technology Stack

- **Backend**: Flask 3.0.0 with SQLAlchemy
- **Database**: SQLite (with PostgreSQL support)
- **Email**: Flask-Mail with Gmail SMTP
- **Calendar**: Google Calendar API v3
- **Frontend**: Bootstrap 5, vanilla JavaScript
- **Deployment**: Waitress WSGI server
- **Security**: Token-based authentication, SSL via Cloudflare

## 🚀 Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd Galveston-Reservation
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Initialize Database**
   ```bash
   python scripts/init_db.py
   ```

4. **Run Development Server**
   ```bash
   python run.py
   ```

5. **Production Deployment**
   ```bash
   python server.py  # Runs on port 80
   ```

## 🔐 Configuration Requirements

1. **Google Calendar API**
   - Service account credentials in `secrets/credentials.json`
   - Calendar shared with service account email
   - See `docs/GOOGLE_CALENDAR_SETUP.md` for details

2. **Email Configuration**
   - Gmail SMTP with app password
   - Configure in `.env` file

3. **Environment Variables**
   ```env
   FLASK_ENV=production
   SECRET_KEY=your-secret-key
   GMAIL_USERNAME=your-email@gmail.com
   GMAIL_PASSWORD=your-app-password
   GOOGLE_CALENDAR_ID=your-calendar-id
   ```

## � Booking Workflow

1. **Guest Request**
   - Guest fills out booking form at `str.ptpsystem.com`
   - System checks calendar availability
   - Creates BookingRequest in database

2. **Admin Approval**
   - Admin receives email with booking details
   - Click approve/reject links in email
   - Links expire after 48 hours

3. **Confirmation**
   - Upon approval: Creates Google Calendar event
   - Sends confirmation to guest
   - Notifies team members (without guest names for privacy)

4. **Email Recipients**
   - Primary admin: `livingbayfront@gmail.com`
   - Team notifications: `info@galvestonislandresortrentals.com`, 
     `michelle.kleensweep@gmail.com`, `alicia.kleensweep@gmail.com`

## 📖 Documentation

Detailed setup and deployment guides are available in the `docs/` directory:

- [Deployment Guide](docs/DEPLOYMENT.md)
- [Google Calendar Setup](docs/GOOGLE_CALENDAR_SETUP.md)
- [Cloudflare Configuration](docs/CLOUDFLARE_SETUP.md)

## 🧪 Testing

Test files are organized in the `tests/` directory:

```bash
# Run tests
python -m pytest tests/

# Run specific test
python tests/test_calendar.py
```
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
