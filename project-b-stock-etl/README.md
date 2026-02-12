# Project B — Stock + FX Daily ETL with Automated Reporting

A production-style daily ETL pipeline that ingests U.S. equity prices (Alpha Vantage) **and** FX rates (Frankfurter), persists results to an idempotent SQLite “ledger”, generates **Markdown + PDF** reports, and delivers outputs via **SendGrid email**. The job is safe to rerun and easy to schedule locally (macOS launchd).

---

## What This Demonstrates (Portfolio Value)

- **Multi-source ingestion**: equities (Alpha Vantage) + **FX rates** (Frankfurter)
- **Idempotent persistence**: reruns do not duplicate rows (DB-level constraints)
- **Automated reporting**: date-stamped **.md** and **.pdf** outputs
- **Automated delivery**: SendGrid email with attachments (CSVs + reports)
- **Scheduling**: hands-free daily execution via launchd (macOS)

---

## Architecture

### Daily Job (Orchestrator)

Entry point:

```bash
python -m src.jobs.run_daily
```

What it does:
1) Run stock ETL for configured symbols (Extract → Transform → Load)
2) Fetch + store FX rate (USD/THB)
3) Build summary + generate reports
4) Email attachments via SendGrid

### Stock ETL

- Extract: `src/extract.py` (Alpha Vantage `TIME_SERIES_DAILY` → DataFrame)
- Transform: `src/transform.py` (types, ordering, data contract)
- Load: `src/load.py` (CSV snapshots + SQLite ledger)
- Orchestration: `src/pipeline.py` (`run_pipeline(symbols)`)

### FX Integration (Second API Source)

- `src/fx.py`
  - Fetches latest FX from Frankfurter (no API key)
  - Upserts into SQLite table `fx_rates` (idempotent)

### Reporting

- Markdown report: `src/reporting/daily_report.py`
  - Writes `data/reports/daily_report_YYYY-MM-DD.md`
  - Includes latest close + 1D return per symbol
  - Includes latest stored USD/THB FX rate

- PDF report: `src/reporting/pdf_report.py`
  - Writes `data/reports/daily_report_YYYY-MM-DD.pdf`
  - Includes a summary table + close-price chart
  - Includes latest stored USD/THB FX rate

### Notification

- SendGrid emailer: `src/notify/sendgrid_emailer.py`
  - Sends a daily email with attachments

---

## Data Model

Database file: `data/market_data.db`

**prices**
- One row per `(symbol, date)`
- Database-level uniqueness ensures idempotency

**fx_rates**
- One row per `(rate_date, base, quote)`
- Stores FX context for reporting

---

## Outputs

After a successful run:

- CSV snapshots (overwritten each run):
  - `data/processed/prices_AAPL.csv`
  - `data/processed/prices_MSFT.csv`
  - `data/processed/prices_NVDA.csv`

- SQLite ledger (append-safe):
  - `data/market_data.db`

- Date-stamped reports:
  - `data/reports/daily_report_YYYY-MM-DD.md`
  - `data/reports/daily_report_YYYY-MM-DD.pdf`

---

## Setup

### Requirements
- Python 3.10+

Install dependencies:

```bash
pip install -r requirements.txt
```

### Environment variables
Create a `.env` file in the project root:

```bash
ALPHAVANTAGE_API_KEY=YOUR_ALPHA_VANTAGE_KEY
SENDGRID_API_KEY=YOUR_SENDGRID_KEY
SENDGRID_FROM_EMAIL=you@yourdomain.com
SENDGRID_TO_EMAIL=destination@example.com
```

Notes:
- Alpha Vantage requires an API key.
- SendGrid may queue emails without a verified domain, but **deliverability can be limited** until sender/domain authentication is complete.

---

## Run Locally

Run the full daily job (ETL + FX + reports + email):

```bash
python -m src.jobs.run_daily
```

Run only the stock ETL pipeline:

```bash
python -m src.pipeline
```

Generate reports only:

```bash
python -m src.reporting.daily_report
python -m src.reporting.pdf_report
```

---

## SQL Analytics

Analytical queries are stored under `sql/`:

```text
sql/
  01_row_counts.sql
  02_latest_prices.sql
  03_daily_returns.sql
```

Run with readable output:

```bash
sqlite3 -header -column data/market_data.db < sql/03_daily_returns.sql
```

---

## Scheduling (macOS launchd)

This project is scheduling-ready via launchd.

Typical setup uses:
- a shell wrapper script (e.g. `scripts/run_daily.sh`) that runs the job and writes to `logs/`
- a launchd plist (e.g. `com.yonatan.stocketl.daily.plist`) that calls the wrapper at a chosen time

Confirm the job is loaded:

```bash
launchctl list | grep com.yonatan.stocketl.daily
```

---

## Idempotency Guarantees

- SQLite enforces uniqueness at the DB layer
- Re-running the job produces a stable database state
- FX rates use a primary key on `(rate_date, base, quote)` and upsert semantics

This makes the system safe to:
- retry
- schedule
- rerun after partial failures

---

## Known Limitations

- Alpha Vantage free tier is rate-limited
- This is a daily batch pipeline, not real-time streaming
- SQLite is used intentionally for simplicity and portability

---

## Project Status

✅ Stock ETL (CSV + SQLite)
✅ Daily job runner (ETL + FX + reports + email)
✅ Markdown + PDF reporting
✅ Multi-source ingestion (stocks + FX)
✅ Scheduling-ready (launchd)

---

## Next Extensions (Optional)

- Incremental fetching (only new trading days)
- Dockerize the job for portability
- CI checks (tests/lint/type-check)
- Run on a remote scheduler (GitHub Actions / Cloud Run)

---

## Final Note

This project emphasizes correctness, clarity, and operational realism: a small system that runs daily, stores data safely, produces reports, and delivers results automatically.