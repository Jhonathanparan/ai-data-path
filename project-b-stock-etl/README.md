

# Project B — Stock Market ETL Pipeline

## Overview

This project implements a production-style ETL (Extract, Transform, Load) pipeline that ingests daily U.S. equity price data from the Alpha Vantage API, normalizes and validates the data, and persists it in both CSV snapshots and an idempotent SQLite database for analysis.

This project was built as part of a structured learning path focused on developing practical data engineering skills and understanding how small, real-world data systems are designed and maintained.

The system is designed to be:
- safe to re-run
- resilient to API failures
- explicit in its data contracts
- suitable for local execution and portfolio review

---

## Architecture

The pipeline follows a strict separation of concerns:

Extract → Transform → Load → Analyze

### Extract (`src/extract.py`)
- Calls the Alpha Vantage `TIME_SERIES_DAILY` endpoint
- Validates response structure
- Converts raw JSON into a pandas DataFrame
- Fails loudly on unexpected API responses (e.g. rate limits)

### Transform (`src/transform.py`)
- Parses dates into proper datetime objects
- Enforces numeric types for price and volume columns
- Sorts data chronologically
- Returns a clean, analysis-ready DataFrame
- Does **not** persist data

### Load (`src/load.py`)

Persists transformed data in two formats:

**CSV (Snapshot)**
- One file per symbol
- Overwritten on each run
- Human-readable and easy to inspect

Example:
```
data/processed/prices_AAPL.csv
```

**SQLite (Ledger)**
- Stores all historical data in `data/market_data.db`
- Enforces idempotency using a UNIQUE index on `(symbol, date)`
- Safe to re-run indefinitely without duplicating data
- Automatically de-duplicates legacy data if required

### Pipeline Orchestration (`src/pipeline.py`)
- Coordinates extract → transform → load
- Processes symbols independently (one failure does not halt the run)
- Includes rate limiting to respect API constraints
- Logs progress and errors in a production-style format

---

## Data Persistence Design

This project intentionally uses two persistence layers, each with a distinct purpose:

| Storage | Purpose | Behavior |
|-------|--------|----------|
| CSV | Snapshot | Overwritten on each run |
| SQLite | Ledger | Idempotent, append-safe |

This mirrors real-world systems where:
- files are used for inspection and export
- databases serve as the canonical source of truth

---

## Idempotency Guarantee

The SQLite database enforces data integrity at the database level, not just in application logic.

- Dates are normalized to `YYYY-MM-DD`
- A UNIQUE index on `(symbol, date)` prevents duplicate rows
- Inserts use `INSERT OR IGNORE`
- Re-running the pipeline produces a stable database state

This makes the pipeline safe to:
- retry
- schedule
- re-run after failures

---

## Running the Pipeline

### Requirements
- Python 3.10+
- Dependencies installed via `pip install -r requirements.txt`
- Alpha Vantage API key

Create a `.env` file in the project root:

```
ALPHAVANTAGE_API_KEY=YOUR_API_KEY_HERE
```

Run the pipeline from the project root:

```
python -m src.pipeline
```

---

## SQL Analytics

Analytical queries are stored as versioned `.sql` files under the `sql/` directory.

Example structure:
```
sql/
  01_row_counts.sql
  02_latest_prices.sql
  03_daily_returns.sql
```

### Running SQL analytics

From the project root:

```
sqlite3 data/market_data.db < sql/03_daily_returns.sql
```

For readable output:

```
sqlite3 -header -column data/market_data.db < sql/03_daily_returns.sql
```

This approach ensures analytics are:
- reproducible
- reviewable
- independent of the ingestion pipeline

---

## Known Limitations

- Alpha Vantage free tier is limited to 25 requests per day
- Pipeline is designed for daily batch ingestion, not real-time streaming
- SQLite is used intentionally for simplicity and portability

---

## Why SQLite?

SQLite was chosen deliberately because:
- the dataset is modest in size
- the pipeline runs locally
- it requires no external infrastructure
- it allows real SQL analytics without operational overhead

This choice prioritizes appropriateness over complexity.

---

## Project Status

- ETL pipeline implemented
- Idempotent persistence enforced
- SQL analytics included
- Ready for extension (incremental loads, reporting, dashboards)

---

## Possible Extensions

- Incremental API fetching (only new trading days)
- Scheduled execution (cron / task scheduler)
- Python-based reporting using SQL outputs
- Migration to a cloud database if scale requires it

---

## Final Note

This project emphasizes correctness, clarity, and restraint over unnecessary complexity.
It is intentionally designed to reflect how small-to-medium data systems are built in practice.
# Project B — Stock + FX Daily ETL with Automated Reporting

A production-style daily ETL pipeline that ingests U.S. equity prices (Alpha Vantage) **and** FX rates (Frankfurter), persists results to an idempotent SQLite “ledger”, generates **Markdown + PDF** reports, and delivers outputs via **SendGrid email**. The job is designed to be safe to rerun and easy to schedule locally (macOS launchd).

---

## What This Project Demonstrates (Portfolio Value)

- **Multi-source ingestion**: equities (Alpha Vantage) + **FX rates** (Frankfurter)
- **Idempotent persistence**: reruns do not duplicate rows (DB-level constraints)
- **Automated reporting**: date-stamped **.md** and **.pdf** outputs
- **Automated delivery**: SendGrid email with attachments (CSVs + reports)
- **Scheduling**: hands-free daily execution via launchd (macOS)

---

## Architecture

**Daily Job (Orchestrator)**

`src/jobs/run_daily.py`

1) Run stock ETL for configured symbols (Extract → Transform → Load)
2) Fetch + store FX rate (USD/THB)
3) Build summary + generate reports
4) Email attachments via SendGrid

**Stock ETL**

- Extract: `src/extract.py` (Alpha Vantage API → raw JSON → DataFrame)
- Transform: `src/transform.py` (types, ordering, data contract)
- Load: `src/load.py` (CSV snapshots + SQLite ledger)
- Orchestration: `src/pipeline.py`

**FX Integration (Second API Source)**

- `src/fx.py`
  - Fetches latest FX from Frankfurter (no API key)
  - Upserts into SQLite table `fx_rates` (idempotent)

**Reporting**

- Markdown report: `src/reporting/daily_report.py`
  - Writes `data/reports/daily_report_YYYY-MM-DD.md`
  - Includes latest close + 1D return per symbol
  - Includes latest stored USD/THB FX rate

- PDF report: `src/reporting/pdf_report.py`
  - Writes `data/reports/daily_report_YYYY-MM-DD.pdf`
  - Includes a summary table + a close-price chart
  - Includes latest stored USD/THB FX rate

**Notification**

- SendGrid emailer: `src/notify/sendgrid_emailer.py`
  - Sends a daily email with attachments

---

## Data Model

### SQLite (Canonical “Ledger”)

Database file: `data/market_data.db`

**prices**
- One row per `(symbol, date)`
- Database-level uniqueness ensures idempotency

**fx_rates**
- One row per `(rate_date, base, quote)`
- Stores latest FX for reporting context

---

## Outputs

After a successful run you should have:

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
- Install dependencies:

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
- SendGrid can queue emails without a verified domain, but **deliverability may be limited** until sender/domain authentication is complete.

---

## Run Locally

### Run the full daily job
This is the primary entrypoint (ETL + FX + reports + email):

```bash
python -m src.jobs.run_daily
```

### Run only the stock ETL pipeline

```bash
python -m src.pipeline
```

### Generate reports only

```bash
python -m src.reporting.daily_report
python -m src.reporting.pdf_report
```

---

## SQL Analytics

SQL queries live in `sql/`:

```text
sql/
  01_row_counts.sql
  02_latest_prices.sql
  03_daily_returns.sql
```

Run (with readable output):

```bash
sqlite3 -header -column data/market_data.db < sql/03_daily_returns.sql
```

---

## Scheduling (macOS launchd)

This project is designed to be scheduled locally using launchd.

Typical setup uses:
- a shell wrapper script (e.g. `scripts/run_daily.sh`) that runs the job and writes to `logs/`
- a launchd plist (e.g. `com.yonatan.stocketl.daily.plist`) that calls the wrapper at a chosen time

Once installed and loaded, you can confirm it is active with:

```bash
launchctl list | grep com.yonatan.stocketl.daily
```

---

## Idempotency Guarantees

- The SQLite database enforces uniqueness at the DB layer
- Re-running the job produces a stable database state
- FX rates use a primary key on `(rate_date, base, quote)` and upsert semantics

This makes the pipeline safe to:
- retry
- schedule
- rerun after partial failures

---

## Known Limitations

- Alpha Vantage free tier is rate-limited
- This is a daily batch pipeline, not real-time streaming
- SQLite is used intentionally for portability and local reproducibility

---

## Project Status

✅ Stock ETL (CSV + SQLite)
✅ Daily job runner (ETL + FX + reports + email)
✅ Markdown + PDF reporting
✅ Multi-source ingestion (stocks + FX)
✅ Scheduling-ready (launchd)

---

## Next Extensions (If You Want to Push Further)

- Incremental fetching (only new trading days)
- Dockerize the job for portability
- CI checks + linting + type checking
- Deploy to a simple cloud scheduler (GitHub Actions / Cloud Run / etc.)

---

## Final Note

This project emphasizes correctness, clarity, and operational realism: a small system that runs daily, stores data safely, produces reports, and delivers results automatically.