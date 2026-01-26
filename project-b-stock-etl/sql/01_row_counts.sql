-- Row counts per symbol
-- Purpose: verify data completeness and ingestion consistency

SELECT
    symbol,
    COUNT(*) AS row_count
FROM prices
GROUP BY symbol
ORDER BY symbol;