print(">>> run_queries.py started")
"""
Run SQL queries against the Chinook SQLite database and export results to CSV.

Purpose:
- Demonstrate Python ↔ SQL integration
- Execute pre-written SQL queries (no business logic in Python)
- Export query results for downstream use (BI, reporting, etc.)
"""

import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "chinook.db"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

query_revenue_by_country = """
SELECT
  c.Country AS country,
  ROUND(SUM(i.Total), 2) AS total_revenue
FROM Customer c
JOIN Invoice i
  ON c.CustomerId = i.CustomerId
GROUP BY c.Country
ORDER BY total_revenue DESC;
"""

df_revenue = pd.read_sql_query(query_revenue_by_country, conn)
df_revenue.to_csv(OUTPUT_DIR / "revenue_by_country.csv", index=False)

query_top_customers = """
SELECT
  c.CustomerId,
  c.FirstName || ' ' || c.LastName AS customer_name,
  c.Country,
  ROUND(SUM(i.Total), 2) AS lifetime_spend
FROM Customer c
JOIN Invoice i
  ON c.CustomerId = i.CustomerId
GROUP BY
  c.CustomerId,
  c.FirstName,
  c.LastName,
  c.Country
ORDER BY lifetime_spend DESC
LIMIT 10;
"""

df_customers = pd.read_sql_query(query_top_customers, conn)
df_customers.to_csv(OUTPUT_DIR / "top_customers.csv", index=False)


query_customers_no_purchases = """
SELECT
  c.CustomerId,
  c.FirstName || ' ' || c.LastName AS customer_name,
  c.Country
FROM Customer c
LEFT JOIN Invoice i
  ON c.CustomerId = i.CustomerId
WHERE i.InvoiceId IS NULL
ORDER BY c.Country, customer_name;
"""

df_no_purchases = pd.read_sql_query(query_customers_no_purchases, conn)
df_no_purchases.to_csv(OUTPUT_DIR / "customers_no_purchases.csv", index=False)


conn.close()
