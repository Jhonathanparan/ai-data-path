

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