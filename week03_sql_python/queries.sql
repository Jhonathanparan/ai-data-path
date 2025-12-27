-- ============================================================
-- Chinook SQL Analysis
-- Purpose: Demonstrate JOINs and aggregation
-- ============================================================

-- Revenue by country
-- Business question: Which countries generate the most revenue?
SELECT
  c.Country AS country,
  ROUND(SUM(i.Total), 2) AS total_revenue
FROM Customer c
INNER JOIN Invoice i
  ON c.CustomerId = i.CustomerId
GROUP BY c.Country
ORDER BY total_revenue DESC;
-- Findings:
-- - Revenue is concentrated in North America, with the USA and Canada generating the highest totals.
-- - European countries form a secondary revenue tier, followed by a long tail of smaller markets.

-- ============================================================
-- Top customers by lifetime spend
-- Business question: Who are the highest-value customers?
-- ============================================================
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
-- Findings:
-- - The top customers have relatively similar lifetime spend levels, with no single customer dominating total revenue.
-- - High-value customers are distributed across multiple countries, indicating that revenue concentration is driven by broad customer participation rather than a small number of extreme outliers.

-- ============================================================
-- Customers with no purchases
-- Business question: Which customers have never made a purchase?
-- ============================================================
SELECT
  c.CustomerId,
  c.FirstName || ' ' || c.LastName AS customer_name,
  c.Country
FROM Customer c
LEFT JOIN Invoice i
  ON c.CustomerId = i.CustomerId
WHERE i.InvoiceId IS NULL
ORDER BY c.Country, customer_name;
-- Findings:
-- - All customers in the Chinook dataset have at least one associated invoice.
-- - No dormant customers were identified, indicating complete customer-to-invoice coverage in this dataset.