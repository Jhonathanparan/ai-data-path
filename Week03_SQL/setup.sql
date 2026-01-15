-- 1. Remove clean table if it exists
DROP TABLE IF EXISTS superstore_clean;

-- 2. Create clean analysis table
CREATE TABLE superstore_clean (
    ship_mode TEXT,
    segment TEXT,
    country TEXT,
    city TEXT,
    state TEXT,
    postal_code INTEGER,
    region TEXT,
    category TEXT,
    sub_category TEXT,
    sales REAL,
    quantity INTEGER,
    discount REAL,
    profit REAL
);

-- 3. Copy + FIX data from raw table
INSERT INTO superstore_clean
SELECT
    ship_mode,
    segment,
    country,
    city,
    state,
    postal_code,
    region,
    category,
    sub_category,
    CAST(sales AS REAL),
    CAST(quantity AS INTEGER),
    CAST(discount AS REAL),
    CAST(profit AS REAL)
FROM superstore;