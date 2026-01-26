-- Latest available closing price per symbol
-- Purpose: snapshot view of most recent market data

SELECT
    p.symbol,
    p.date,
    p.close
FROM prices p
JOIN (
    SELECT
        symbol,
        MAX(date) AS max_date
    FROM prices
    GROUP BY symbol
) latest
ON p.symbol = latest.symbol
AND p.date = latest.max_date
ORDER BY p.symbol;