-- Superstore Profitability Analysis (SQLite)
-- Dataset: superstore_clean (flat extract; no order_id/customer_id)
-- Unit of analysis: each row is a line record

SELECT COUNT(*) AS row_count
FROM superstore_clean;

-- ============================================================
-- Profitability by discount rate
-- Question: At what discount levels does profit consistently break down?
-- ============================================================
SELECT
  ROUND(discount * 100.0, 0) AS discount_pct,
  COUNT(*) AS total_rows,
  SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS loss_rows,
  ROUND(SUM(profit), 2) AS total_profit,
  ROUND(
    100.0 * SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(*),
    2
  ) AS loss_row_pct
FROM superstore_clean
GROUP BY ROUND(discount * 100.0, 0)
ORDER BY discount_pct ASC;

-- Findings:
-- - Profitability remains positive through ~20% discounts, despite some loss occurrences.
-- - A clear profitability break occurs at ~30% discount, where loss frequency exceeds 90% and net profit turns negative.
-- - Discounts above 30% are structurally unprofitable, with near-100% loss rates and increasing loss magnitude.

-- ============================================================
-- Regional risk profile
-- Question: Which regions combine high loss frequency with material profit impact?
-- ============================================================
SELECT
  region,
  COUNT(*) AS total_rows,
  SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS loss_rows,
  SUM(CASE WHEN profit = 0 THEN 1 ELSE 0 END) AS break_even_rows,
  SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) AS profit_rows,
  ROUND(SUM(profit), 2) AS total_profit,
  ROUND(
    100.0 * SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(*),
    2
  ) AS loss_row_pct
FROM superstore_clean
GROUP BY region
ORDER BY loss_row_pct DESC, total_profit ASC;
-- Findings:
-- - Central exhibits the highest loss frequency (~32%), indicating elevated operational or pricing risk despite remaining profitable overall.
-- - West shows the strongest performance profile, combining the lowest loss rate (~10%) with the highest total profit.
-- - East and South fall between these extremes, with moderate loss rates and solid profitability.
-- - Overall, risk and profitability vary meaningfully by region, suggesting that loss drivers are not evenly distributed geographically.

-- ============================================================
-- Category risk within each region
-- Question: Which product categories are driving losses inside each region?
-- Note: HAVING filters out very small sample sizes to avoid misleading signals.
-- ============================================================
SELECT
  region,
  category,
  COUNT(*) AS total_rows,
  SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS loss_rows,
  ROUND(SUM(profit), 2) AS total_profit,
  ROUND(
    100.0 * SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(*),
    2
  ) AS loss_row_pct
FROM superstore_clean
GROUP BY region, category
HAVING COUNT(*) >= 20
ORDER BY region, loss_row_pct DESC, total_profit ASC;

-- Findings:
-- - Furniture is the dominant loss driver in every region, exhibiting the highest loss frequency and, in Central, negative total profit.
-- - Central–Furniture is the most problematic combination, with ~66% of rows unprofitable and net losses.
-- - Technology is consistently the healthiest category across all regions, combining low loss rates with strong positive profit.
-- - Office Supplies shows moderate loss frequency but remains profitable in all regions, suggesting manageable risk.

-- ============================================================
-- Step 5: Furniture loss contribution by sub-category
-- Question: Which Furniture sub-categories contribute most to total losses?
-- ============================================================
SELECT
  sub_category,
  ROUND(SUM(profit), 2) AS total_loss,
  ROUND(
    100.0 * SUM(profit) / SUM(SUM(profit)) OVER (),
    2
  ) AS pct_of_total_loss
FROM superstore_clean
WHERE category = 'Furniture'
  AND profit < 0
GROUP BY sub_category
ORDER BY total_loss ASC;
-- Findings:
-- - Furniture losses are highly concentrated, with Tables alone accounting for ~53% of total Furniture losses.
-- - Tables and Bookcases together contribute approximately 73% of all Furniture losses, indicating a clear Pareto-style concentration.
-- - Chairs and Furnishings contribute materially less to total losses, suggesting that not all Furniture sub-categories are structurally problematic.

-- ============================================================
-- Regional contribution to Furniture losses
-- Question: Which regions contribute most to total Furniture losses?
-- ============================================================
SELECT
  region,
  ROUND(SUM(profit), 2) AS total_loss,
  ROUND(
    100.0 * SUM(profit) / SUM(SUM(profit)) OVER (),
    2
  ) AS pct_of_total_loss
FROM superstore_clean
WHERE category = 'Furniture'
  AND profit < 0
GROUP BY region
ORDER BY total_loss ASC;

-- Findings:
-- - Furniture losses are geographically concentrated, with Central (~32%) and East (~31%) together accounting for roughly 63% of total Furniture losses.
-- - West and South contribute substantially less to Furniture losses, indicating lower priority for immediate intervention.
-- - These results suggest that remediation efforts for Furniture should focus first on Central and East regions to achieve the largest impact.

-- ============================================================
-- Step 7: Loss severity analysis using a CTE
-- Question: Where are Furniture losses most expensive per loss row?
-- ============================================================
WITH furniture_losses_by_region AS (
  SELECT
    region,
    SUM(profit) AS total_loss,
    COUNT(*) AS loss_rows
  FROM superstore_clean
  WHERE category = 'Furniture'
    AND profit < 0
  GROUP BY region
)
SELECT
  region,
  ROUND(total_loss, 2) AS total_loss,
  loss_rows,
  ROUND(total_loss / loss_rows, 2) AS avg_loss_per_loss_row
FROM furniture_losses_by_region
ORDER BY avg_loss_per_loss_row ASC;
-- Findings:
-- - While Central and East account for the largest share of total Furniture losses, their average loss per unprofitable row is comparatively lower.
-- - South exhibits the highest loss severity per loss row (~$171 per loss), despite contributing a smaller share of total Furniture losses.
-- - This distinction suggests different remediation strategies: frequency-driven issues in Central/East versus severity-driven issues in South.

-- ============================================================
-- Loss analysis by order size (quantity)
-- Question: Are losses driven by small orders or large (bulk) orders?
-- ============================================================
SELECT
  CASE
    WHEN quantity = 1 THEN '1 unit'
    WHEN quantity = 2 THEN '2 units'
    WHEN quantity BETWEEN 3 AND 4 THEN '3–4 units'
    ELSE '5+ units'
  END AS quantity_bucket,
  COUNT(*) AS total_rows,
  SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS loss_rows,
  ROUND(SUM(profit), 2) AS total_profit,
  ROUND(
    100.0 * SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(*),
    2
  ) AS loss_row_pct
FROM superstore_clean
GROUP BY quantity_bucket
ORDER BY
  CASE
    WHEN quantity_bucket = '1 unit' THEN 1
    WHEN quantity_bucket = '2 units' THEN 2
    WHEN quantity_bucket = '3–4 units' THEN 3
    ELSE 4
  END;

-- Findings:
-- - Loss frequency remains consistent across all order sizes (~18–19%), indicating that losses are not driven by order size.
-- - Larger orders (3+ units) generate substantially higher total profit, despite similar loss rates to smaller orders.
-- - This suggests that profitability issues are primarily driven by pricing and discount structure rather than order size or exposure to large quantities.

-- ============================================================
-- Superstore Profitability Analysis — Executive Summary
-- ============================================================
--
-- Objective:
-- Identify the primary drivers of profitability and loss in the Superstore dataset,
-- determine where losses originate, and prioritize corrective action areas with the
-- highest potential impact.
--
-- Dataset & Constraints:
-- - Source table: superstore_clean (flat analytical extract)
-- - Unit of analysis: each row represents a line record
-- - No order_id or customer_id available; analysis is performed at row level
-- - Joins were intentionally not used to avoid misrepresenting the data structure
--
-- Analytical Approach:
-- The analysis followed a structured, hypothesis-driven workflow:
-- 1. Identify structural profitability breakpoints by discount level
-- 2. Assess regional loss frequency and profit impact
-- 3. Isolate category-level loss drivers within regions
-- 4. Drill down into Furniture sub-categories to identify root causes
-- 5. Quantify loss concentration using window functions
-- 6. Separate loss frequency from loss severity using a CTE
-- 7. Test whether order size (quantity) is a meaningful driver of losses
--
-- Key Findings:
-- - Discounting is the primary structural driver of losses:
--   Profitability breaks sharply at ~30% discount, where loss frequency exceeds 90%
--   and net profit becomes consistently negative.
--
-- - Loss risk varies meaningfully by region:
--   Central exhibits the highest loss frequency, while West combines the lowest loss
--   rate with the highest overall profitability.
--
-- - Furniture is the dominant loss-driving category across all regions:
--   Other categories, particularly Technology, remain structurally profitable.
--
-- - Furniture losses are highly concentrated:
--   Tables alone account for ~53% of Furniture losses, and Tables + Bookcases together
--   contribute approximately 73%, indicating a clear Pareto-style concentration.
--
-- - Furniture losses are geographically concentrated:
--   Central and East together account for roughly 63% of total Furniture losses.
--
-- - Loss frequency and loss severity are distinct phenomena:
--   Central and East experience frequent losses, while South exhibits the highest
--   average loss per unprofitable row, suggesting different remediation strategies.
--
-- - Order size is not a meaningful loss driver:
--   Loss frequency remains consistent across quantity buckets (~18–19%), while larger
--   orders generate higher total profit, ruling out bulk orders as the root cause.
--
-- Recommendations:
-- - Reevaluate and constrain discounting at or above 30%, where losses become structural.
-- - Prioritize corrective action for Furniture, specifically Tables and Bookcases.
-- - Focus remediation efforts first in Central and East regions to address loss frequency.
-- - Investigate cost, pricing, or logistics drivers in the South region, where loss
--   severity per row is highest.
-- - Preserve and potentially scale strategies used in the West region, which exhibits
--   strong profitability with low loss rates.
--
-- Conclusion:
-- Losses in the Superstore dataset are driven primarily by pricing and discount structure,
-- not order size. They are concentrated in specific product categories and regions,
-- enabling targeted, high-impact remediation rather than broad operational changes.
--
-- ============================================================