-- Daily returns per symbol
-- Formula: (close - previous_close) / previous_close

SELECT
    symbol,
    date,
    close,
    LAG(close) OVER (
        PARTITION BY symbol
        ORDER BY date
    ) AS prev_close,
    ROUND(
        (close - LAG(close) OVER (
            PARTITION BY symbol
            ORDER BY date
        )) / LAG(close) OVER (
            PARTITION BY symbol
            ORDER BY date
        ),
        6
    ) AS daily_return
FROM prices
ORDER BY symbol, date;