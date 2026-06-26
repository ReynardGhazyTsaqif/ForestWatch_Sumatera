"""
ForestWatch Sumatera — Tahap 3: Exploratory Data Analysis (EDA)
===============================================================
Jalankan dari root proyek:
    python src/eda.py

Output:
    reports/eda/
        A1_tren_sumatera_total.png
        A2_tren_sumatera_co2.png
        B1_total_loss_per_provinsi.png
        B2_tren_per_provinsi.png
        B3_heatmap_provinsi_tahun.png
        C1_top10_kabupaten_total.png
        C2_top10_kabupaten_per_tahun.png
        D1_histogram_loss.png
        D2_boxplot_per_provinsi.png
        E1_scatter_loss_co2.png
        summary_insights.txt
"""

import os
import warnings
import textwrap

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# 0. KONFIGURASI
# ─────────────────────────────────────────────

# Sesuaikan BASE_DIR ke root proyek jika menjalankan dari lokasi lain
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PROVINCE = os.path.join(BASE_DIR, "data", "processed", "province_master.csv")
DATA_DISTRICT = os.path.join(BASE_DIR, "data", "processed", "district_master.csv")
OUT_DIR       = os.path.join(BASE_DIR, "reports", "eda")

os.makedirs(OUT_DIR, exist_ok=True)

# Palet warna konsisten per provinsi (10 warna distint)
PROVINCE_PALETTE = [
    "#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00",
    "#a65628", "#f781bf", "#999999", "#1b9e77", "#d95f02"
]

# Style global
plt.rcParams.update({
    "figure.dpi": 150,
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
})

def save(fig, fname, tight=True):
    path = os.path.join(OUT_DIR, fname)
    if tight:
        fig.savefig(path, bbox_inches="tight")
    else:
        fig.savefig(path)
    plt.close(fig)
    print(f"  [✓] Disimpan: {fname}")


# ─────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("  ForestWatch Sumatera — EDA")
print("="*60)

print("\n[1/6] Memuat data …")
prov_df = pd.read_csv(DATA_PROVINCE)
dist_df = pd.read_csv(DATA_DISTRICT)

# Validasi kolom
assert {"province", "year", "tree_cover_loss_ha", "co2_emissions"}.issubset(prov_df.columns), \
    "Kolom province_master.csv tidak sesuai skema!"
assert {"province", "district", "year", "tree_cover_loss_ha", "co2_emissions"}.issubset(dist_df.columns), \
    "Kolom district_master.csv tidak sesuai skema!"

prov_df["year"] = prov_df["year"].astype(int)
dist_df["year"] = dist_df["year"].astype(int)

print(f"  Provinsi  : {prov_df['province'].nunique()} provinsi, "
      f"{prov_df['year'].min()}–{prov_df['year'].max()}, "
      f"{len(prov_df):,} baris")
print(f"  Kabupaten : {dist_df['district'].nunique()} kab/kota, "
      f"{dist_df['year'].min()}–{dist_df['year'].max()}, "
      f"{len(dist_df):,} baris")

provinces = sorted(prov_df["province"].unique())
prov_color = {p: PROVINCE_PALETTE[i % len(PROVINCE_PALETTE)] for i, p in enumerate(provinces)}


# ─────────────────────────────────────────────
# A. TREN KESELURUHAN SUMATERA
# ─────────────────────────────────────────────

print("\n[2/6] A — Tren keseluruhan Sumatera …")

sumatera_yearly = prov_df.groupby("year").agg(
    total_loss=("tree_cover_loss_ha", "sum"),
    total_co2=("co2_emissions", "sum")
).reset_index()

# A1 — Total tree cover loss per tahun
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.fill_between(sumatera_yearly["year"], sumatera_yearly["total_loss"] / 1e3,
                alpha=0.18, color="#2c7bb6")
ax.plot(sumatera_yearly["year"], sumatera_yearly["total_loss"] / 1e3,
        color="#2c7bb6", linewidth=2.2, marker="o", markersize=5)

# Annotate peak
peak_row = sumatera_yearly.loc[sumatera_yearly["total_loss"].idxmax()]
ax.annotate(
    f"Puncak: {peak_row['year']}\n{peak_row['total_loss']/1e3:,.0f} ribu ha",
    xy=(peak_row["year"], peak_row["total_loss"] / 1e3),
    xytext=(peak_row["year"] + 1.2, peak_row["total_loss"] / 1e3 * 1.02),
    fontsize=9, color="#d7191c",
    arrowprops=dict(arrowstyle="->", color="#d7191c", lw=1.2)
)
ax.set_title("Tren Total Kehilangan Tutupan Pohon — Sumatera (2001–2025)")
ax.set_xlabel("Tahun")
ax.set_ylabel("Tree Cover Loss (ribu ha)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax.set_xticks(sumatera_yearly["year"])
ax.tick_params(axis="x", rotation=45)
save(fig, "A1_tren_sumatera_total.png")

# A2 — Total CO₂ per tahun
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.fill_between(sumatera_yearly["year"], sumatera_yearly["total_co2"] / 1e9,
                alpha=0.18, color="#d73027")
ax.plot(sumatera_yearly["year"], sumatera_yearly["total_co2"] / 1e9,
        color="#d73027", linewidth=2.2, marker="s", markersize=5)
ax.set_title("Tren Total Emisi CO₂ — Sumatera (2001–2025)")
ax.set_xlabel("Tahun")
ax.set_ylabel("Emisi CO₂ (miliar Mg CO₂e)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.2f}"))
ax.set_xticks(sumatera_yearly["year"])
ax.tick_params(axis="x", rotation=45)
save(fig, "A2_tren_sumatera_co2.png")


# ─────────────────────────────────────────────
# B. PERBANDINGAN ANTAR PROVINSI
# ─────────────────────────────────────────────

print("[3/6] B — Perbandingan antar provinsi …")

prov_total = (prov_df.groupby("province")["tree_cover_loss_ha"]
              .sum().sort_values(ascending=True).reset_index())

# B1 — Bar chart horizontal total per provinsi
fig, ax = plt.subplots(figsize=(9, 5.5))
colors_bar = [prov_color[p] for p in prov_total["province"]]
bars = ax.barh(prov_total["province"], prov_total["tree_cover_loss_ha"] / 1e3,
               color=colors_bar, edgecolor="white", height=0.7)
for bar, val in zip(bars, prov_total["tree_cover_loss_ha"] / 1e3):
    ax.text(val + 20, bar.get_y() + bar.get_height() / 2,
            f"{val:,.0f}", va="center", fontsize=8.5, color="#333")
ax.set_title("Total Kehilangan Tutupan Pohon per Provinsi (2001–2025)")
ax.set_xlabel("Total Tree Cover Loss (ribu ha)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
save(fig, "B1_total_loss_per_provinsi.png")

# B2 — Multi-line tren per provinsi
fig, ax = plt.subplots(figsize=(12, 6))
for prov in provinces:
    sub = prov_df[prov_df["province"] == prov].sort_values("year")
    ax.plot(sub["year"], sub["tree_cover_loss_ha"] / 1e3,
            label=prov, color=prov_color[prov], linewidth=1.6, alpha=0.85)
ax.set_title("Tren Kehilangan Tutupan Pohon per Provinsi (2001–2025)")
ax.set_xlabel("Tahun")
ax.set_ylabel("Tree Cover Loss (ribu ha)")
ax.legend(loc="upper right", fontsize=7.5, ncol=2, framealpha=0.8)
ax.set_xticks(sorted(prov_df["year"].unique()))
ax.tick_params(axis="x", rotation=45)
save(fig, "B2_tren_per_provinsi.png")

# B3 — Heatmap provinsi × tahun
pivot_prov = prov_df.pivot_table(
    index="province", columns="year", values="tree_cover_loss_ha", aggfunc="sum"
)
fig, ax = plt.subplots(figsize=(14, 5))
sns.heatmap(
    pivot_prov / 1e3,
    cmap="YlOrRd", ax=ax, linewidths=0.4, linecolor="white",
    cbar_kws={"label": "Tree Cover Loss (ribu ha)", "shrink": 0.7},
    fmt=".0f", annot=False
)
ax.set_title("Heatmap: Kehilangan Tutupan Pohon — Provinsi × Tahun (ribu ha)")
ax.set_xlabel("Tahun")
ax.set_ylabel("")
ax.tick_params(axis="x", rotation=45)
save(fig, "B3_heatmap_provinsi_tahun.png")


# ─────────────────────────────────────────────
# C. ANALISIS KABUPATEN/KOTA
# ─────────────────────────────────────────────

print("[4/6] C — Analisis kabupaten/kota …")

dist_total = (dist_df.groupby(["province", "district"])["tree_cover_loss_ha"]
              .sum().reset_index()
              .sort_values("tree_cover_loss_ha", ascending=False))

# C1 — Top 10 total loss
top10_total = dist_total.head(10).copy()
top10_total["label"] = top10_total["district"] + "\n(" + top10_total["province"].str[:4] + ")"

fig, ax = plt.subplots(figsize=(10, 5.5))
bar_colors = [prov_color.get(p, "#999") for p in top10_total["province"]]
bars = ax.barh(top10_total["label"][::-1], top10_total["tree_cover_loss_ha"][::-1] / 1e3,
               color=bar_colors[::-1], edgecolor="white", height=0.7)
for bar, val in zip(bars, top10_total["tree_cover_loss_ha"][::-1] / 1e3):
    ax.text(val + 5, bar.get_y() + bar.get_height() / 2,
            f"{val:,.0f}", va="center", fontsize=8.5)
ax.set_title("Top 10 Kabupaten/Kota — Total Kehilangan Tutupan Pohon (2001–2025)")
ax.set_xlabel("Total Tree Cover Loss (ribu ha)")
save(fig, "C1_top10_kabupaten_total.png")

# C2 — Top 10 kabupaten untuk tahun dengan loss tertinggi
peak_year = int(sumatera_yearly.loc[sumatera_yearly["total_loss"].idxmax(), "year"])
dist_peak = (dist_df[dist_df["year"] == peak_year]
             .groupby(["province", "district"])["tree_cover_loss_ha"]
             .sum().reset_index()
             .sort_values("tree_cover_loss_ha", ascending=False)
             .head(10))
dist_peak["label"] = dist_peak["district"] + "\n(" + dist_peak["province"].str[:4] + ")"

fig, ax = plt.subplots(figsize=(10, 5.5))
bar_colors2 = [prov_color.get(p, "#999") for p in dist_peak["province"]]
bars2 = ax.barh(dist_peak["label"][::-1], dist_peak["tree_cover_loss_ha"][::-1] / 1e3,
                color=bar_colors2[::-1], edgecolor="white", height=0.7)
for bar, val in zip(bars2, dist_peak["tree_cover_loss_ha"][::-1] / 1e3):
    ax.text(val + 1, bar.get_y() + bar.get_height() / 2,
            f"{val:,.0f}", va="center", fontsize=8.5)
ax.set_title(f"Top 10 Kabupaten/Kota — Kehilangan Tutupan Pohon Tahun {peak_year}")
ax.set_xlabel("Tree Cover Loss (ribu ha)")
save(fig, "C2_top10_kabupaten_per_tahun.png")


# ─────────────────────────────────────────────
# D. DISTRIBUSI DATA
# ─────────────────────────────────────────────

print("[5/6] D — Distribusi data …")

# D1 — Histogram
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
for ax, col, title, unit in zip(
    axes,
    ["tree_cover_loss_ha", "co2_emissions"],
    ["Distribusi Tree Cover Loss", "Distribusi Emisi CO₂"],
    ["ha", "Mg CO₂e"]
):
    data = prov_df[col].dropna()
    ax.hist(data / (1e3 if col == "tree_cover_loss_ha" else 1e6),
            bins=30, color="#4575b4", edgecolor="white", alpha=0.85)
    ax.set_title(title)
    ax.set_xlabel(f"{'ribu ha' if col == 'tree_cover_loss_ha' else 'juta Mg CO₂e'}")
    ax.set_ylabel("Frekuensi")
    mu = (data / (1e3 if col == "tree_cover_loss_ha" else 1e6)).mean()
    ax.axvline(mu, color="#d73027", linestyle="--", linewidth=1.5,
               label=f"Mean = {mu:,.1f}")
    ax.legend(fontsize=8.5)
fig.suptitle("Distribusi Data Level Provinsi (2001–2025)", y=1.01, fontsize=13)
save(fig, "D1_histogram_loss.png")

# D2 — Boxplot per provinsi
fig, ax = plt.subplots(figsize=(12, 5.5))
order = (prov_df.groupby("province")["tree_cover_loss_ha"]
         .median().sort_values(ascending=False).index.tolist())
prov_df["loss_ribu"] = prov_df["tree_cover_loss_ha"] / 1e3
sns.boxplot(
    data=prov_df, x="province", y="loss_ribu", order=order,
    palette=[prov_color[p] for p in order],
    flierprops={"marker": "o", "markersize": 3, "alpha": 0.5},
    ax=ax
)
ax.set_title("Distribusi Tahunan Tree Cover Loss per Provinsi (2001–2025)")
ax.set_xlabel("")
ax.set_ylabel("Tree Cover Loss (ribu ha)")
ax.tick_params(axis="x", rotation=35)
save(fig, "D2_boxplot_per_provinsi.png")


# ─────────────────────────────────────────────
# E. KORELASI
# ─────────────────────────────────────────────

print("[6/6] E — Korelasi loss vs CO₂ …")

corr_data = prov_df.dropna(subset=["tree_cover_loss_ha", "co2_emissions"])
r, p_val = stats.pearsonr(corr_data["tree_cover_loss_ha"], corr_data["co2_emissions"])

fig, ax = plt.subplots(figsize=(8, 6))
for prov in provinces:
    sub = corr_data[corr_data["province"] == prov]
    ax.scatter(sub["tree_cover_loss_ha"] / 1e3, sub["co2_emissions"] / 1e6,
               label=prov, color=prov_color[prov], s=35, alpha=0.75, edgecolors="white", linewidth=0.4)

# Regression line
x_fit = np.linspace(corr_data["tree_cover_loss_ha"].min(),
                    corr_data["tree_cover_loss_ha"].max(), 200)
slope, intercept, *_ = stats.linregress(corr_data["tree_cover_loss_ha"], corr_data["co2_emissions"])
ax.plot(x_fit / 1e3, (slope * x_fit + intercept) / 1e6,
        color="#333", linewidth=1.5, linestyle="--", label=f"Regresi linear\nr = {r:.4f}, p = {p_val:.2e}")

ax.set_title("Korelasi: Tree Cover Loss vs Emisi CO₂")
ax.set_xlabel("Tree Cover Loss (ribu ha)")
ax.set_ylabel("Emisi CO₂ (juta Mg CO₂e)")
ax.legend(fontsize=7.5, ncol=2, loc="upper left", framealpha=0.85)
save(fig, "E1_scatter_loss_co2.png")


# ─────────────────────────────────────────────
# RINGKASAN INSIGHTS
# ─────────────────────────────────────────────

total_sumatera    = prov_df["tree_cover_loss_ha"].sum()
total_co2         = prov_df["co2_emissions"].sum()
top_prov          = prov_total.sort_values("tree_cover_loss_ha", ascending=False).iloc[0]
top_district      = dist_total.iloc[0]
avg_loss_per_year = sumatera_yearly["total_loss"].mean()
trend_recent      = sumatera_yearly[sumatera_yearly["year"] >= 2015]["total_loss"].mean()
trend_early       = sumatera_yearly[sumatera_yearly["year"] <= 2010]["total_loss"].mean()

insights = textwrap.dedent(f"""
ForestWatch Sumatera — Ringkasan Insights EDA
Generated: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}
{'='*60}

A. TREN KESELURUHAN SUMATERA
  • Total kehilangan tutupan pohon (2001–2025) : {total_sumatera/1e6:.3f} juta ha
  • Total emisi CO₂ kumulatif                  : {total_co2/1e9:.3f} miliar Mg CO₂e
  • Rata-rata kehilangan per tahun             : {avg_loss_per_year/1e3:,.1f} ribu ha/tahun
  • Tahun dengan kehilangan tertinggi          : {peak_year}
  • Rata-rata loss 2001–2010                   : {trend_early/1e3:,.1f} ribu ha/tahun
  • Rata-rata loss 2015–2025                   : {trend_recent/1e3:,.1f} ribu ha/tahun
  • Perubahan tren (awal vs terkini)           : {"↑ meningkat" if trend_recent > trend_early else "↓ menurun"}

B. PERBANDINGAN PROVINSI
  • Provinsi dengan loss terbesar : {top_prov['province']} ({top_prov['tree_cover_loss_ha']/1e6:.3f} juta ha)
  • Provinsi terurut (tinggi→rendah):
{chr(10).join(f"    {i+1:2d}. {r['province']:<35} {r['tree_cover_loss_ha']/1e3:>8,.1f} ribu ha" for i, r in prov_total.sort_values('tree_cover_loss_ha', ascending=False).iterrows())}

C. KABUPATEN/KOTA
  • Kabupaten dengan total loss tertinggi : {top_district['district']} ({top_district['province']})
  • Total loss kabupaten tersebut         : {top_district['tree_cover_loss_ha']/1e3:,.1f} ribu ha

D. DISTRIBUSI
  • Mean  tree cover loss (provinsi/tahun): {prov_df['tree_cover_loss_ha'].mean()/1e3:,.1f} ribu ha
  • Median tree cover loss                : {prov_df['tree_cover_loss_ha'].median()/1e3:,.1f} ribu ha
  • Std dev                               : {prov_df['tree_cover_loss_ha'].std()/1e3:,.1f} ribu ha
  • Nilai minimum                         : {prov_df['tree_cover_loss_ha'].min():,.1f} ha
  • Nilai maksimum                        : {prov_df['tree_cover_loss_ha'].max()/1e3:,.1f} ribu ha

E. KORELASI
  • Pearson r (loss vs CO₂) : {r:.6f}
  • p-value                 : {p_val:.2e}
  • Interpretasi            : {"Korelasi sangat kuat & signifikan" if abs(r) > 0.95 and p_val < 0.05 else "Korelasi kuat" if abs(r) > 0.7 else "Korelasi moderat"}

REKOMENDASI FITUR UNTUK CLUSTERING (Tahap 4):
  • total_loss   — total kehilangan 2001–2025
  • mean_loss    — rata-rata tahunan
  • max_loss     — puncak kehilangan
  • std_loss     — variabilitas antar tahun
  • trend_slope  — kemiringan tren (OLS slope)
  • pct_recent   — proporsi loss 2015–2025 vs total (menangkap tren terkini)
""")

insights_path = os.path.join(OUT_DIR, "summary_insights.txt")
with open(insights_path, "w", encoding="utf-8") as f:
    f.write(insights)

print(f"\n  [✓] Insights disimpan: summary_insights.txt")
print("\n" + "="*60)
print(f"  EDA selesai! 11 file tersimpan di: reports/eda/")
print("="*60 + "\n")