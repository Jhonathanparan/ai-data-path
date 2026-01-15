/*
profit anaylisis by discount

SELECT
  discount * 100 AS discount_pct,
  COUNT(*) AS total_orders,
  SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS loss_orders,
  SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) AS profit_orders,
  SUM(CASE WHEN PROFIT = 0 THEN 1 ELSE 0 END) AS break_even_orders,
  ROUND(SUM(profit), 2) AS total_profit,
  ROUND(
    100.0 * SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(*),
    2
  ) AS loss_order_pct
FROM superstore_clean
GROUP BY discount
ORDER BY discount;

Profit by sub-categories with discount over 30 percent

SELECT
    category,
    sub_category,
    COUNT(*) AS total_orders,

    SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS loss_orders,
    SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) AS profit_orders,

    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(
        100.0 * SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(*),2)
        AS loss_order_pct
    FROM superstore_clean
    WHERE discount >= 0.30
    GROUP BY category, sub_category
    HAVING total_orders >= 10
    ORDER BY total_profit ASC;


-- =========================================================
-- Phones only: Discount band analysis at high discounts (30%+)
-- =========================================================
SELECT
    CASE
        WHEN discount >= 0.50 THEN '50%+'
        WHEN discount >= 0.40 THEN '40–49%'
        WHEN discount >= 0.30 THEN '30–39%'
    END AS discount_band,

    COUNT(*) AS total_orders,

    SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS loss_orders,
    SUM(CASE WHEN profit = 0 THEN 1 ELSE 0 END) AS break_even_orders,
    SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) AS profit_orders,

    ROUND(SUM(profit), 2) AS total_profit,

    ROUND(
        100.0 * SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS loss_order_pct
FROM superstore_clean
WHERE sub_category = 'Phones'
  AND discount >= 0.30
GROUP BY discount_band
ORDER BY discount_band;


-- =========================================================
-- Phones only: Quantity bucket analysis at high discounts (40–49%)
-- Hypothesis: profitable phone orders at high discounts are larger orders
-- =========================================================


SELECT
    CASE
        WHEN quantity >= 5 THEN '5+ units'
        WHEN quantity >= 3 THEN '3–4 units'
        WHEN quantity = 2 THEN '2 units'
        ELSE '1 unit'
    END AS quantity_bucket,

    COUNT(*) AS total_orders,

    SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS loss_orders,
    SUM(CASE WHEN profit = 0 THEN 1 ELSE 0 END) AS break_even_orders,
    SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) AS profit_orders,

    ROUND(SUM(profit), 2) AS total_profit,

    ROUND(
        100.0 * SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS loss_order_pct
FROM superstore_clean
WHERE sub_category = 'Phones'
  AND discount >= 0.40
  AND discount < 0.50
GROUP BY quantity_bucket
ORDER BY
    CASE quantity_bucket
        WHEN '1 unit' THEN 1
        WHEN '2 units' THEN 2
        WHEN '3–4 units' THEN 3
        WHEN '5+ units' THEN 4
    END;
 
-- =========================================================
-- Order quality by region (classification view)
-- =========================================================

SELECT
    region
    COUNT(*) AS total_orders,

    SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS bad_orders,
    SUM(CASE WHEN profit = 0 THEN 1 ELSE 0 END) AS break_even_orders,
    SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) AS good_orders,

    ROUND(SUM(profit), 2) AS total_profit,

    ROUND(
        100.0 * SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS bad_order_pct
FROM superstore_clean
GROUP BY region
ORDER BY bad_order_pct DESC;

 

 -- =========================================================
-- Order quality by region  and category (classification view)
-- =========================================================
 
 SELECT
    region, 
    category,
    COUNT(*) AS total_orders,

    SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS bad_orders,
    SUM(CASE WHEN profit = 0 THEN 1 ELSE 0 END) AS break_even_orders,
    SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) AS good_orders,

    ROUND(SUM(profit), 2) AS total_profit,

    ROUND(
        100.0 * SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS bad_order_pct
FROM superstore_clean
GROUP BY region, category
HAVING COUNT (*) > 20
ORDER BY region, bad_order_pct DESC;


-- Furniture sub-categories by region 

SELECT
  region,
  sub_category,
  COUNT(*) AS total_orders,
  SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS bad_orders,
  ROUND(SUM(profit), 2) AS total_profit,
  ROUND(100.0 * SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS bad_order_pct
FROM superstore_clean
WHERE category = 'Furniture'
GROUP BY region, sub_category
HAVING COUNT(*) >= 30
ORDER BY region, bad_order_pct DESC, total_profit ASC;


-- TOTAL PROFITS AND TOTAL PROFIT PCT

SELECT
  sub_category,
  ROUND(SUM(profit), 2) AS total_profit
FROM superstore_clean
WHERE category = 'Furniture'
GROUP BY sub_category
ORDER BY total_profit ASC;

SELECT
  sub_category,
  ROUND(SUM(profit), 2) AS total_profit,

  ROUND(
    100.0 * SUM(profit) / SUM(SUM(profit)) OVER (),
    2
  ) AS pct_of_total_profit
FROM superstore_clean
WHERE category = 'Furniture'
GROUP BY sub_category
ORDER BY total_profit ASC;

 

--Within Furniture, which sub-categories contribute the most to total losses?


SELECT
  sub_category,
  ROUND(SUM(profit), 2) AS total_profit,

  ROUND(
    100.0 * SUM(profit)
    / SUM(SUM(profit)) OVER (),
    2
  ) AS pct_of_total_profit
FROM superstore_clean
WHERE category = 'Furniture'
  AND profit < 0
GROUP BY sub_category
ORDER BY total_profit ASC;


-- total loss and percent of total loss ny region

WITH furniture_losses_by_region AS (
    SELECT
        region,
        SUM(profit) AS total_profit
    FROM superstore_clean
    WHERE category = 'Furniture'
      AND profit < 0
    GROUP BY region
)

SELECT
    region,
    ROUND(total_profit, 2) AS total_profit,
    ROUND(
        100.0 * total_profit
        / SUM(total_profit) OVER (),
        2
    ) AS pct_of_total_profit
FROM furniture_losses_by_region
ORDER BY total_profit ASC;


-- losses per order

WITH furniture_loss_totals AS (
    SELECT
        region,
        SUM(profit) AS total_loss
    FROM superstore_clean
    WHERE category = 'Furniture'
      AND profit < 0
    GROUP BY region
),
furniture_loss_counts AS (
    SELECT
        region,
        COUNT(*) AS loss_orders
    FROM superstore_clean
    WHERE category = 'Furniture'
      AND profit < 0
    GROUP BY region
)

SELECT
    t.region,
    ROUND(t.total_loss, 2) AS total_loss,
    c.loss_orders,
    ROUND(t.total_loss / c.loss_orders, 2) AS loss_per_order
FROM furniture_loss_totals t
JOIN furniture_loss_counts c
  ON t.region = c.region
ORDER BY loss_per_order ASC;
*/
WITH
orders(order_id, region) AS (
  VALUES ('O1','West'),('O2','Central'),('O3','East')
),
order_lines(order_id, sub_category, profit) AS (
  VALUES ('O1','Tables',-50),('O1','Chairs',20),('O2','Tables',-30),('O4','Bookcases',-10)
)
SELECT
  o.order_id, o.region,
  l.sub_category, l.profit
FROM orders o
INNER JOIN order_lines l
  ON o.order_id = l.order_id
ORDER BY o.order_id;
