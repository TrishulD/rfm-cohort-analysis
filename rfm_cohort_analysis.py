"""
=============================================================
  RFM & Cohort Analysis — Online Retail Dataset
  Author : Jai (SASTRA Deemed University, B.Tech CSE)
  Dataset: OnlineRetail.csv  (~541 K transactions, 2010-2011)
=============================================================
"""

# ── 0. Imports ────────────────────────────────────────────
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from datetime import datetime
import os

OUT = "/mnt/user-data/outputs"
os.makedirs(OUT, exist_ok=True)

# Consistent style
plt.rcParams.update({
    "figure.facecolor": "#0f1117",
    "axes.facecolor":   "#1a1d27",
    "axes.edgecolor":   "#3a3d4d",
    "axes.labelcolor":  "#e0e0e0",
    "xtick.color":      "#b0b0b0",
    "ytick.color":      "#b0b0b0",
    "text.color":       "#e0e0e0",
    "grid.color":       "#2a2d3d",
    "grid.linestyle":   "--",
    "grid.alpha":       0.5,
    "font.family":      "DejaVu Sans",
    "axes.titlesize":   13,
    "axes.labelsize":   11,
    "legend.framealpha":0.2,
    "legend.edgecolor": "#555",
})

PALETTE   = ["#7B61FF","#00D4AA","#FF6B6B","#FFB347","#4FC3F7","#F06292","#AED581","#FF8A65"]
ACCENT    = "#7B61FF"
SEG_COLORS = {
    "Champions":        "#00D4AA",
    "Loyal Customers":  "#7B61FF",
    "Potential Loyalists": "#4FC3F7",
    "Promising":        "#AED581",
    "Need Attention":   "#FFB347",
    "At Risk":          "#FF8A65",
    "About to Sleep":   "#F06292",
    "Hibernating":      "#B0BEC5",
    "Lost Customers":   "#FF6B6B",
    "Can't Lose Them":  "#FFD700",
}

print("=" * 60)
print("  RFM & Cohort Analysis — Online Retail Dataset")
print("=" * 60)

# ═══════════════════════════════════════════════════════════
# 1. LOAD & DATA CLEANING
# ═══════════════════════════════════════════════════════════
print("\n[1/7] Loading & cleaning data …")

df_raw = pd.read_csv(
    "/mnt/user-data/uploads/OnlineRetail.csv", encoding="latin1"
)
print(f"  Raw shape          : {df_raw.shape}")
print(f"  Missing CustomerID : {df_raw['CustomerID'].isna().sum():,}")
print(f"  Duplicates         : {df_raw.duplicated().sum():,}")
print(f"  Cancellations (C)  : {df_raw['InvoiceNo'].astype(str).str.startswith('C').sum():,}")
print(f"  Negative Quantity  : {(df_raw['Quantity']<0).sum():,}")
print(f"  Zero/neg UnitPrice : {(df_raw['UnitPrice']<=0).sum():,}")

df = df_raw.copy()

# Date conversion
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# Drop rows with missing CustomerID (guest / untracked)
df.dropna(subset=["CustomerID"], inplace=True)

# Remove cancellations (InvoiceNo starts with 'C')
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]

# Remove invalid Quantity / UnitPrice
df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]

# Remove duplicates
df.drop_duplicates(inplace=True)

# Derived columns
df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
df["CustomerID"] = df["CustomerID"].astype(int)

print(f"\n  Clean shape        : {df.shape}")
print(f"  Date range         : {df['InvoiceDate'].min().date()} → {df['InvoiceDate'].max().date()}")
print(f"  Unique customers   : {df['CustomerID'].nunique():,}")
print(f"  Unique countries   : {df['Country'].nunique():,}")


# ═══════════════════════════════════════════════════════════
# 2. EDA
# ═══════════════════════════════════════════════════════════
print("\n[2/7] Exploratory Data Analysis …")

df["Month"]    = df["InvoiceDate"].dt.to_period("M")
df["YearMonth"]= df["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
df["DayOfWeek"]= df["InvoiceDate"].dt.day_name()
df["Hour"]     = df["InvoiceDate"].dt.hour

monthly_rev  = df.groupby("YearMonth")["TotalPrice"].sum()
monthly_cust = df.groupby("YearMonth")["CustomerID"].nunique()
top_countries= df.groupby("Country")["TotalPrice"].sum().nlargest(10)
top_products = df.groupby("Description")["Quantity"].sum().nlargest(10)
dow_order    = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
dow_rev      = df.groupby("DayOfWeek")["TotalPrice"].sum().reindex(dow_order)
hourly_rev   = df.groupby("Hour")["TotalPrice"].sum()

# ── EDA Figure ────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Exploratory Data Analysis — Online Retail", fontsize=16, fontweight="bold", color="#e0e0e0", y=1.01)

# 2-a: Monthly Revenue
ax = axes[0, 0]
ax.fill_between(monthly_rev.index, monthly_rev.values, alpha=0.3, color=ACCENT)
ax.plot(monthly_rev.index, monthly_rev.values, color=ACCENT, lw=2)
ax.set_title("Monthly Revenue")
ax.set_xlabel("Month"); ax.set_ylabel("Revenue (£)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}K"))
ax.tick_params(axis="x", rotation=45)

# 2-b: Monthly Unique Customers
ax = axes[0, 1]
ax.bar(monthly_cust.index, monthly_cust.values,
       color=[PALETTE[i % len(PALETTE)] for i in range(len(monthly_cust))],
       width=20, alpha=0.85)
ax.set_title("Monthly Active Customers")
ax.set_xlabel("Month"); ax.set_ylabel("Unique Customers")
ax.tick_params(axis="x", rotation=45)

# 2-c: Top 10 Countries by Revenue
ax = axes[0, 2]
bars = ax.barh(top_countries.index[::-1], top_countries.values[::-1],
               color=PALETTE[:10], alpha=0.85)
ax.set_title("Top 10 Countries by Revenue")
ax.set_xlabel("Revenue (£)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}K"))

# 2-d: Top 10 Products
ax = axes[1, 0]
ax.barh(top_products.index[::-1], top_products.values[::-1],
        color=PALETTE[:10], alpha=0.85)
ax.set_title("Top 10 Products by Quantity Sold")
ax.set_xlabel("Units Sold")
for label in ax.get_yticklabels():
    label.set_fontsize(7.5)

# 2-e: Revenue by Day of Week
ax = axes[1, 1]
ax.bar(dow_rev.index, dow_rev.values,
       color=[PALETTE[i] for i in range(7)], alpha=0.85)
ax.set_title("Revenue by Day of Week")
ax.set_xlabel(""); ax.set_ylabel("Revenue (£)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}K"))
ax.tick_params(axis="x", rotation=30)

# 2-f: Revenue by Hour
ax = axes[1, 2]
ax.plot(hourly_rev.index, hourly_rev.values, color="#00D4AA", lw=2.5, marker="o", ms=4)
ax.fill_between(hourly_rev.index, hourly_rev.values, alpha=0.2, color="#00D4AA")
ax.set_title("Revenue by Hour of Day")
ax.set_xlabel("Hour"); ax.set_ylabel("Revenue (£)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}K"))

plt.tight_layout()
plt.savefig(f"{OUT}/01_eda_overview.png", dpi=150, bbox_inches="tight", facecolor="#0f1117")
plt.close()
print("  → Saved 01_eda_overview.png")


# ═══════════════════════════════════════════════════════════
# 3. RFM CALCULATION
# ═══════════════════════════════════════════════════════════
print("\n[3/7] Computing RFM values …")

snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

rfm = df.groupby("CustomerID").agg(
    Recency   = ("InvoiceDate",  lambda x: (snapshot_date - x.max()).days),
    Frequency = ("InvoiceNo",    "nunique"),
    Monetary  = ("TotalPrice",   "sum")
).reset_index()

print(f"  Snapshot date  : {snapshot_date.date()}")
print(f"  Customers in RFM: {len(rfm):,}")
print(rfm.describe().round(2).to_string())


# ═══════════════════════════════════════════════════════════
# 4. RFM SCORING & SEGMENTATION
# ═══════════════════════════════════════════════════════════
print("\n[4/7] Scoring & segmenting …")

# Quintile scoring (1–5)
rfm["R_Score"] = pd.qcut(rfm["Recency"],   5, labels=[5,4,3,2,1]).astype(int)
rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
rfm["M_Score"] = pd.qcut(rfm["Monetary"],  5, labels=[1,2,3,4,5]).astype(int)

rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)
rfm["RFM_Total"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]

def segment(row):
    r, f = row["R_Score"], row["F_Score"]
    if r >= 4 and f >= 4:                          return "Champions"
    if r >= 3 and f >= 3:                          return "Loyal Customers"
    if r >= 3 and f <= 2:                          return "Potential Loyalists"
    if r == 5 and f == 1:                          return "Promising"
    if 2 <= r <= 3 and 2 <= f <= 3:               return "Need Attention"
    if r <= 2 and f >= 3:                          return "At Risk"
    if r <= 2 and f <= 2 and row["M_Score"] >= 3: return "Can't Lose Them"
    if r == 2 and f <= 2:                          return "About to Sleep"
    if r <= 2 and f >= 4:                          return "Hibernating"
    return "Lost Customers"

rfm["Segment"] = rfm.apply(segment, axis=1)

seg_summary = rfm.groupby("Segment").agg(
    Customers  = ("CustomerID","count"),
    Avg_Recency= ("Recency",   "mean"),
    Avg_Freq   = ("Frequency", "mean"),
    Avg_Monetary=("Monetary",  "mean"),
    Total_Revenue=("Monetary", "sum"),
).round(2)
seg_summary["Rev_Pct"] = (seg_summary["Total_Revenue"] / seg_summary["Total_Revenue"].sum() * 100).round(1)

print(seg_summary.to_string())


# ═══════════════════════════════════════════════════════════
# 5. RFM VISUALISATIONS
# ═══════════════════════════════════════════════════════════
print("\n[5/7] Building RFM visualisations …")

seg_order = list(SEG_COLORS.keys())
seg_present = [s for s in seg_order if s in rfm["Segment"].unique()]
seg_counts  = rfm["Segment"].value_counts().reindex(seg_present).fillna(0)
seg_revenue = rfm.groupby("Segment")["Monetary"].sum().reindex(seg_present).fillna(0)

# ── Figure 2: Segment overview ────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(20, 7))
fig.suptitle("RFM Customer Segments", fontsize=16, fontweight="bold", color="#e0e0e0")

# Donut – customer count
ax = axes[0]
colors_used = [SEG_COLORS.get(s, "#888") for s in seg_present]
wedges, texts, autotexts = ax.pie(
    seg_counts, labels=seg_present, autopct="%1.1f%%",
    colors=colors_used, startangle=140,
    pctdistance=0.82, wedgeprops=dict(width=0.55),
    textprops=dict(color="#e0e0e0", fontsize=8)
)
for at in autotexts: at.set_fontsize(7)
ax.set_title("Customer Distribution", pad=12)

# Bar – revenue contribution
ax = axes[1]
rev_sorted = seg_revenue.sort_values(ascending=True)
c_list = [SEG_COLORS.get(s, "#888") for s in rev_sorted.index]
bars = ax.barh(rev_sorted.index, rev_sorted.values, color=c_list, alpha=0.88, height=0.6)
ax.set_title("Revenue by Segment")
ax.set_xlabel("Total Revenue (£)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}K"))
for bar, val in zip(bars, rev_sorted.values):
    ax.text(val + rev_sorted.max()*0.01, bar.get_y()+bar.get_height()/2,
            f"£{val/1e3:.1f}K", va="center", fontsize=8, color="#e0e0e0")

# Bubble – R vs F coloured by M
ax = axes[2]
scatter = ax.scatter(
    rfm["R_Score"], rfm["F_Score"],
    c=rfm["M_Score"], cmap="plasma",
    alpha=0.35, s=18, linewidths=0
)
plt.colorbar(scatter, ax=ax, label="M Score")
ax.set_title("R vs F Score (colour = M)")
ax.set_xlabel("Recency Score (5 = most recent)")
ax.set_ylabel("Frequency Score (5 = most frequent)")
ax.set_xticks(range(1,6)); ax.set_yticks(range(1,6))

plt.tight_layout()
plt.savefig(f"{OUT}/02_rfm_segments.png", dpi=150, bbox_inches="tight", facecolor="#0f1117")
plt.close()
print("  → Saved 02_rfm_segments.png")

# ── Figure 3: RFM distribution heatmaps ──────────────────
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle("RFM Score Distributions", fontsize=15, fontweight="bold", color="#e0e0e0")

# Heatmap R vs F
pivot_rf = rfm.groupby(["R_Score","F_Score"])["CustomerID"].count().unstack(fill_value=0)
cmap1 = LinearSegmentedColormap.from_list("pur_teal", ["#1a1d27","#7B61FF","#00D4AA"])
sns.heatmap(pivot_rf, ax=axes[0], cmap=cmap1, annot=True, fmt="d",
            linewidths=0.5, linecolor="#0f1117", cbar_kws={"label":"# Customers"})
axes[0].set_title("Recency vs Frequency (customer count)")
axes[0].set_xlabel("Frequency Score"); axes[0].set_ylabel("Recency Score")

# Heatmap F vs M
pivot_fm = rfm.groupby(["F_Score","M_Score"])["CustomerID"].count().unstack(fill_value=0)
sns.heatmap(pivot_fm, ax=axes[1], cmap=cmap1, annot=True, fmt="d",
            linewidths=0.5, linecolor="#0f1117", cbar_kws={"label":"# Customers"})
axes[1].set_title("Frequency vs Monetary (customer count)")
axes[1].set_xlabel("Monetary Score"); axes[1].set_ylabel("Frequency Score")

plt.tight_layout()
plt.savefig(f"{OUT}/03_rfm_heatmaps.png", dpi=150, bbox_inches="tight", facecolor="#0f1117")
plt.close()
print("  → Saved 03_rfm_heatmaps.png")

# ── Figure 4: RFM distributions ──────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("Distribution of RFM Metrics", fontsize=15, fontweight="bold", color="#e0e0e0")

for ax, col, color, label, cap in zip(
    axes,
    ["Recency","Frequency","Monetary"],
    ["#7B61FF","#00D4AA","#FFB347"],
    ["Days since last purchase","Number of invoices","Total spend (£)"],
    [365, 100, 5000]
):
    data = rfm[col].clip(upper=cap)
    ax.hist(data, bins=50, color=color, alpha=0.8, edgecolor="#0f1117")
    ax.axvline(data.median(), color="#FF6B6B", lw=1.5, ls="--", label=f"Median: {data.median():.0f}")
    ax.set_title(col); ax.set_xlabel(label); ax.set_ylabel("Customers")
    ax.legend()

plt.tight_layout()
plt.savefig(f"{OUT}/04_rfm_distributions.png", dpi=150, bbox_inches="tight", facecolor="#0f1117")
plt.close()
print("  → Saved 04_rfm_distributions.png")

# ── Figure 5: Segment profiles ───────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("Average RFM Values per Segment", fontsize=15, fontweight="bold", color="#e0e0e0")

for ax, metric, ylabel in zip(
    axes,
    ["Avg_Recency","Avg_Freq","Avg_Monetary"],
    ["Avg Recency (days)","Avg Frequency","Avg Monetary (£)"]
):
    ordered = seg_summary[metric].reindex(seg_present).sort_values(ascending=(metric=="Avg_Recency"))
    c_list  = [SEG_COLORS.get(s,"#888") for s in ordered.index]
    ax.barh(ordered.index, ordered.values, color=c_list, alpha=0.88, height=0.6)
    ax.set_xlabel(ylabel); ax.set_title(ylabel)

plt.tight_layout()
plt.savefig(f"{OUT}/05_segment_profiles.png", dpi=150, bbox_inches="tight", facecolor="#0f1117")
plt.close()
print("  → Saved 05_segment_profiles.png")


# ═══════════════════════════════════════════════════════════
# 6. COHORT ANALYSIS
# ═══════════════════════════════════════════════════════════
print("\n[6/7] Cohort analysis …")

df["CohortMonth"] = df.groupby("CustomerID")["InvoiceDate"].transform("min").dt.to_period("M")
df["InvoicePeriod"]= df["InvoiceDate"].dt.to_period("M")

def get_cohort_index(row):
    return (row["InvoicePeriod"].to_timestamp().year - row["CohortMonth"].to_timestamp().year)*12 + \
           (row["InvoicePeriod"].to_timestamp().month - row["CohortMonth"].to_timestamp().month)

df["CohortIndex"] = df.apply(get_cohort_index, axis=1)

cohort_data = df.groupby(["CohortMonth","CohortIndex"])["CustomerID"].nunique().reset_index()
cohort_pivot = cohort_data.pivot(index="CohortMonth", columns="CohortIndex", values="CustomerID")

cohort_size  = cohort_pivot.iloc[:, 0]
retention    = cohort_pivot.divide(cohort_size, axis=0) * 100
retention.index = retention.index.astype(str)

# ── Figure 6: Retention heatmap ───────────────────────────
fig, ax = plt.subplots(figsize=(20, 10))
fig.suptitle("Cohort Retention Rate (%)", fontsize=16, fontweight="bold", color="#e0e0e0")

cmap2 = LinearSegmentedColormap.from_list("ret", ["#1a1d27","#7B61FF","#00D4AA","#FFD700"])
ret_plot = retention.iloc[:, :13]    # show first 12 months
sns.heatmap(
    ret_plot, ax=ax, cmap=cmap2,
    annot=True, fmt=".1f", annot_kws={"size": 7.5},
    linewidths=0.4, linecolor="#0f1117",
    vmin=0, vmax=100,
    cbar_kws={"label": "Retention %", "shrink": 0.5}
)
ax.set_xlabel("Months Since First Purchase", labelpad=8)
ax.set_ylabel("Cohort (First Purchase Month)", labelpad=8)
ax.tick_params(axis="x", rotation=0)
ax.tick_params(axis="y", rotation=0)

plt.tight_layout()
plt.savefig(f"{OUT}/06_cohort_retention_heatmap.png", dpi=150, bbox_inches="tight", facecolor="#0f1117")
plt.close()
print("  → Saved 06_cohort_retention_heatmap.png")

# ── Figure 7: Retention curves ────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(18, 7))
fig.suptitle("Cohort Retention Curves", fontsize=15, fontweight="bold", color="#e0e0e0")

# All cohorts
ax = axes[0]
for i, (cohort, row) in enumerate(retention.iterrows()):
    ax.plot(row.dropna().index, row.dropna().values,
            alpha=0.5, lw=1.2, color=PALETTE[i % len(PALETTE)])
ax.set_title("All Cohort Retention Curves")
ax.set_xlabel("Months Since First Purchase"); ax.set_ylabel("Retention (%)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))

# Average retention per month
ax = axes[1]
avg_ret = retention.mean()
ax.plot(avg_ret.index, avg_ret.values, color=ACCENT, lw=2.5, marker="o", ms=5)
ax.fill_between(avg_ret.index, avg_ret.values, alpha=0.2, color=ACCENT)
ax.set_title("Average Retention Across All Cohorts")
ax.set_xlabel("Months Since First Purchase"); ax.set_ylabel("Avg Retention (%)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
for x, y in zip(avg_ret.index[:8], avg_ret.values[:8]):
    ax.annotate(f"{y:.1f}%", (x, y), textcoords="offset points",
                xytext=(0, 8), ha="center", fontsize=8, color="#e0e0e0")

plt.tight_layout()
plt.savefig(f"{OUT}/07_cohort_retention_curves.png", dpi=150, bbox_inches="tight", facecolor="#0f1117")
plt.close()
print("  → Saved 07_cohort_retention_curves.png")

# ── Figure 8: Cohort revenue ──────────────────────────────
cohort_rev = df.groupby(["CohortMonth","CohortIndex"])["TotalPrice"].sum().reset_index()
rev_pivot  = cohort_rev.pivot(index="CohortMonth", columns="CohortIndex", values="TotalPrice")
rev_pivot.index = rev_pivot.index.astype(str)

fig, ax = plt.subplots(figsize=(20, 10))
fig.suptitle("Cohort Revenue (£) by Month", fontsize=16, fontweight="bold", color="#e0e0e0")

cmap3 = LinearSegmentedColormap.from_list("rev", ["#1a1d27","#4FC3F7","#FFB347"])
sns.heatmap(
    rev_pivot.iloc[:, :13] / 1e3, ax=ax, cmap=cmap3,
    annot=True, fmt=".1f", annot_kws={"size":7.5},
    linewidths=0.4, linecolor="#0f1117",
    cbar_kws={"label":"Revenue (£K)", "shrink":0.5}
)
ax.set_xlabel("Months Since First Purchase", labelpad=8)
ax.set_ylabel("Cohort (First Purchase Month)", labelpad=8)
ax.tick_params(axis="x", rotation=0)

plt.tight_layout()
plt.savefig(f"{OUT}/08_cohort_revenue.png", dpi=150, bbox_inches="tight", facecolor="#0f1117")
plt.close()
print("  → Saved 08_cohort_revenue.png")


# ═══════════════════════════════════════════════════════════
# 7. FINAL SUMMARY
# ═══════════════════════════════════════════════════════════
print("\n[7/7] Summary statistics …")

total_rev   = rfm["Monetary"].sum()
champions   = rfm[rfm["Segment"]=="Champions"]
at_risk     = rfm[rfm["Segment"]=="At Risk"]
lost        = rfm[rfm["Segment"]=="Lost Customers"]

print(f"\n  Total revenue       : £{total_rev:,.0f}")
print(f"  Champions           : {len(champions):,} customers  "
      f"(£{champions['Monetary'].sum():,.0f} = "
      f"{champions['Monetary'].sum()/total_rev*100:.1f}% of revenue)")
print(f"  At-Risk customers   : {len(at_risk):,}")
print(f"  Lost customers      : {len(lost):,}")
print(f"  Avg month-1 retention: {retention.iloc[:,1].mean():.1f}%")
print(f"  Avg month-3 retention: {retention.iloc[:,3].mean():.1f}%")

# Export RFM table
rfm.to_csv(f"{OUT}/rfm_scores.csv", index=False)
seg_summary.to_csv(f"{OUT}/segment_summary.csv")
retention.to_csv(f"{OUT}/cohort_retention.csv")
print("\n  → Exported rfm_scores.csv, segment_summary.csv, cohort_retention.csv")

print("\n" + "=" * 60)
print("  All outputs saved to /mnt/user-data/outputs/")
print("=" * 60)
