# Project A — Profitability and Loss Diagnostics (Tableau)

## Portfolio Project — Project A

This is **Project A** in my data analytics / BI portfolio.  
The project is designed to demonstrate structured analytical thinking, business interpretation, and dashboard-driven storytelling rather than surface-level reporting.

This analysis examines profitability, margin efficiency, discount behavior, and loss concentration using the Superstore dataset. The objective is to move beyond total profit reporting and identify **structural drivers of performance and risk**.

Data was lightly preprocessed to ensure correct data types and consistency.  
All aggregations, KPIs, and business logic are defined in the BI layer (Tableau) to preserve flexibility and analytical transparency.

---

## Tableau Dashboard Analysis

The analysis is structured into three dashboards that progress from executive summary to operational diagnosis.

---

### Dashboard 1 — Executive Overview: Profit Is Concentrated in Few Products and Markets

**Purpose**  
Provide a high-level summary of where profit is generated across categories, customer segments, regions, and sub-categories.

**Key Insights**
- All major categories and regions are profitable, but profitability is **unevenly distributed**.
- Technology and Consumer segments drive a disproportionate share of total profit.
- A small number of sub-categories account for the majority of positive profit.
- Several sub-categories contribute minimal or negative value, increasing concentration risk.

**Why It Matters**  
Overall profitability masks dependency risk. This view highlights where the business relies too heavily on a narrow set of products and markets.

---

### Dashboard 2 — Operational Drivers: Discounts and Volume Efficiency

**Purpose**  
Analyze *why* some products perform well while others underperform by examining discounting behavior, sales volume, and profit margins.

**Key Insights**
- Higher average discounts are strongly associated with **margin decline**, particularly in Furniture and select Technology sub-categories.
- High sales volume does **not** guarantee efficiency or profitability.
- Technology combines scale with strong margins, while Furniture generates volume with weaker profitability.
- Several high-volume sub-categories operate below average margins, indicating pricing or cost structure inefficiencies.

**Why It Matters**  
The results suggest that pricing strategy and discount discipline — not demand — are primary drivers of margin erosion.

---

### Dashboard 3 — Loss Diagnostics: Identifying Structural Loss Drivers

**Purpose**  
Isolate and diagnose sources of negative profit to understand where losses originate and how they relate to discounting and margin structure.

**Key Insights**
- Losses are highly concentrated in a **small number of sub-categories** (notably Tables, Bookcases, and Supplies).
- Loss-driving products often combine deep discounts with weak or negative margins.
- Some profitable products operate below average margin efficiency, increasing downside risk.
- Interactive highlight actions enable tracing loss behavior across discount and margin views.

**Why It Matters**  
Losses are not random anomalies but reflect **systemic pricing and cost inefficiencies** that require targeted, product-level intervention.

---

## Tools Used
- Tableau Public
- Python (light preprocessing)
- Pandas

---

## Key Takeaway
Profitability is driven less by volume and more by **pricing discipline, margin efficiency, and product mix**.  
Without addressing structural discounting and cost issues, growth alone increases risk rather than resilience.