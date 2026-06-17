# RFM & Cohort Analysis of an Online Retail Dataset
### B.Tech Computer Science & Engineering — Data Science Project Report
**SASTRA Deemed to be University**

---

## 1. Introduction

Customer analytics is a cornerstone of modern retail strategy. Two of the most operationally valuable techniques are **RFM (Recency-Frequency-Monetary) analysis** and **Cohort Analysis**. This project applies both to a real-world UK-based online retail dataset spanning December 2010 to December 2011.

**RFM Analysis** quantifies each customer's value along three behavioural axes:
- **Recency** — how recently did the customer last buy?
- **Frequency** — how often did they buy?
- **Monetary** — how much total revenue did they contribute?

**Cohort Analysis** groups customers by their first purchase month and tracks how many return in subsequent months, yielding month-by-month **retention rates**.

Together these tools allow a business to identify its most valuable customers, flag churn risk early, and prioritise marketing spend.

---

## 2. Dataset Description

| Attribute | Value |
|---|---|
| Source | UCI ML Repository — Online Retail Dataset |
| Raw rows | 541,909 transactions |
| Columns | InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country |
| Date range | 01 Dec 2010 – 09 Dec 2011 |
| Geography | 37 countries; United Kingdom dominant (~91% revenue) |

---

## 3. Methodology

### 3.1 Data Cleaning

The raw dataset required systematic cleaning before analysis:

| Issue | Count | Treatment |
|---|---|---|
| Missing CustomerID | 135,080 rows | Dropped (guest transactions not trackable) |
| Duplicate rows | 5,268 | Removed |
| Cancellations (InvoiceNo starts with 'C') | 9,288 | Excluded |
| Negative Quantity (returns/adjustments) | 10,624 | Excluded |
| Zero or negative UnitPrice | 2,517 | Excluded |

**Post-cleaning shape:** 392,692 rows | 4,338 unique customers  
**Derived feature:** `TotalPrice = Quantity × UnitPrice`

### 3.2 Exploratory Data Analysis

Key patterns discovered:
- **Revenue peaks** sharply in October–November 2011, consistent with pre-Christmas gifting
- **Thursday** is the highest-revenue weekday; Sunday has negligible activity
- **10 AM – 3 PM** is the peak purchasing window
- **United Kingdom** accounts for ~91% of revenue; Germany, France, and EIRE are the next largest markets
- Top product by volume: "WORLD WAR 2 GLIDERS ASSTD DESIGNS"

### 3.3 RFM Calculation

A **snapshot date** of 2011-12-10 (one day after the final transaction) was defined.

For each customer:

```
Recency   = (snapshot_date − max(InvoiceDate)).days
Frequency = count of unique InvoiceNo values
Monetary  = sum of TotalPrice
```

| Metric | Median | Mean | Max |
|---|---|---|---|
| Recency (days) | 51 | 92.5 | 374 |
| Frequency (invoices) | 2 | 4.3 | 209 |
| Monetary (£) | £668 | £2,049 | £280,206 |

The wide standard deviations indicate a **highly skewed distribution** — a small cohort of very high-value customers pulls the mean significantly above the median.

### 3.4 RFM Scoring

Each metric was divided into 5 equal-frequency (quintile) bins:

- **R Score 5** = purchased most recently; **R Score 1** = longest ago
- **F Score 5** = bought most often; **F Score 1** = least often
- **M Score 5** = highest spender; **M Score 1** = lowest spender

Note: for Recency, lower raw values are better, so bin labels are reversed (the customer with recency = 1 day receives R Score = 5).

### 3.5 Customer Segmentation

Segments were assigned using a rule-based mapping on R and F scores:

| Segment | Rule | Customers | Revenue | Rev % |
|---|---|---|---|---|
| **Champions** | R≥4, F≥4 | 1,139 | £5,913,422 | 66.5% |
| **Loyal Customers** | R≥3, F≥3 | 821 | £1,351,084 | 15.2% |
| **At Risk** | R≤2, F≥3 | 417 | £603,024 | 6.8% |
| **Need Attention** | 2≤R≤3, 2≤F≤3 | 428 | £305,145 | 3.4% |
| **Potential Loyalists** | R≥3, F≤2 | 670 | £306,328 | 3.4% |
| **Can't Lose Them** | R≤2, M≥3 | 168 | £251,198 | 2.8% |
| **Lost Customers** | R≤2, F≤2 | 553 | £124,458 | 1.4% |
| **About to Sleep** | R=2, F≤2 | 142 | £32,550 | 0.4% |

### 3.6 Cohort Analysis

Each customer was assigned a **cohort** equal to the month of their first purchase. A **cohort index** of 0 represents the acquisition month; index 1 represents one month later, and so on.

```
Retention(cohort, month_n) = 
    unique customers in cohort active at month_n  
    ─────────────────────────────────────────────  × 100
    unique customers in cohort at month_0
```

Retention tables were computed for both customer counts and revenue.

---

## 4. Results

### 4.1 RFM Segment Distribution

Champions (1,139 customers, 26.3% of the customer base) generate **66.5% of total revenue**. This extreme concentration aligns with the Pareto principle and signals that retaining these customers is the single highest-leverage business action available.

Loyal Customers add another 15.2%, meaning the top two segments collectively account for **~82% of revenue from only ~45% of customers**.

### 4.2 At-Risk & Lost Customers

- **At Risk (417):** These customers used to buy frequently but haven't purchased recently. Avg recency is 172 days versus 13 days for Champions — they are on a clear disengagement trajectory.
- **Lost Customers (553):** Avg recency of 280 days. Winback probability is low but their historic value warrants a targeted reactivation campaign.
- **Can't Lose Them (168):** Low recency but high monetary value. These are high-LTV customers who have gone quiet — a priority reactivation segment.

### 4.3 Cohort Retention

The cohort heatmap (Figure 6) reveals a **classic steep drop-off** in retention:

| Month | Avg Retention |
|---|---|
| 0 (acquisition) | 100% |
| 1 | ~20.6% |
| 2 | ~22.3% |
| 3 | ~23.2% |
| 6 | ~24–28% (stabilising) |
| 12 | ~30–40% for early cohorts |

The December 2010 cohort (the largest and oldest) demonstrates the strongest long-term retention, with rates stabilising above 30% by month 6 onward. Later cohorts show progressively higher initial month-1 retention, suggesting improving onboarding or a natural selection of more loyal early adopters.

The counterintuitive **slight uptick** from month 1 to month 3 is common in retail: some customers make an initial purchase, lapse for one month, and then return on a seasonal or promotional trigger.

---

## 5. Business Insights

### 5.1 Revenue Concentration & VIP Risk
66.5% of revenue depends on 1,139 customers. Any significant churn in the Champions segment would have an outsized financial impact. **Recommendation:** Introduce a VIP loyalty programme — early access, personalised offers, dedicated account management.

### 5.2 Retention Cliff at Month 1
Fewer than 1 in 5 new customers returns after their first purchase. **Recommendation:** Implement a post-purchase nurture sequence — a Day-3 "how was your order?" email, a Day-7 personalised product recommendation, and a Day-14 incentive for the second purchase.

### 5.3 At-Risk Segment Rescue
417 customers contributed £603K in the past and are at risk of churning. **Recommendation:** Trigger a win-back campaign with a time-limited 10–15% discount for customers with R≤2 and F≥3.

### 5.4 Potential Loyalists Conversion
670 customers have bought recently but only once or twice. They are engaged but not habitual. **Recommendation:** Cross-sell complementary product categories to increase frequency before they disengage.

### 5.5 Seasonal Revenue Optimisation
Revenue spikes sharply in Q4 (Oct–Nov). Early cohorts in this period have higher long-term retention. **Recommendation:** Invest disproportionately in acquisition in September–October to capture consumers who will prove most loyal.

### 5.6 Geographic Expansion
Non-UK markets (Germany, France, EIRE, Netherlands) collectively represent material revenue. **Recommendation:** Localise email marketing (language, currency) for the top 5 non-UK markets to reduce friction and test organic growth.

---

## 6. Conclusion

This project demonstrated a complete end-to-end customer analytics pipeline on a real e-commerce dataset:

1. **Data cleaning** removed ~27% of raw records (missing IDs, cancellations, returns, duplicates), leaving 392,692 clean transactions across 4,338 identifiable customers.
2. **EDA** surfaced strong seasonal, weekday, and hourly purchasing patterns that directly inform campaign timing.
3. **RFM analysis** quantified each customer's value and assigned them to actionable segments. The top two segments (Champions + Loyal) represent the business's revenue backbone.
4. **Cohort analysis** confirmed a steep early-retention drop that is the clearest lever for revenue growth: moving month-1 retention from ~21% to even 30% would compound significantly over the customer lifetime.

The combination of RFM scoring and cohort tracking gives the business a continuously updatable customer health dashboard, enabling data-driven decisions across acquisition, retention, and reactivation strategy.

---

## 7. Output Files

| File | Description |
|---|---|
| `01_eda_overview.png` | 6-panel EDA dashboard |
| `02_rfm_segments.png` | Donut, revenue bar, R-F bubble chart |
| `03_rfm_heatmaps.png` | R×F and F×M customer-count heatmaps |
| `04_rfm_distributions.png` | Histograms of Recency, Frequency, Monetary |
| `05_segment_profiles.png` | Avg R/F/M per segment |
| `06_cohort_retention_heatmap.png` | Month-by-month retention % |
| `07_cohort_retention_curves.png` | All cohorts + average curve |
| `08_cohort_revenue.png` | Revenue cohort heatmap (£K) |
| `rfm_scores.csv` | Full RFM table with segment labels |
| `segment_summary.csv` | Aggregated stats per segment |
| `cohort_retention.csv` | Full retention matrix |

---

*Analysis performed using Python 3 · Pandas · NumPy · Matplotlib · Seaborn*
