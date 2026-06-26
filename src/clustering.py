import os
import warnings
import joblib

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# 0. KONFIGURASI
# ─────────────────────────────────────────────

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR   = os.path.join(BASE_DIR, "data", "processed")
OUT_DATA   = os.path.join(BASE_DIR, "data", "processed")
OUT_REPORT = os.path.join(BASE_DIR, "reports", "clustering")

os.makedirs(OUT_REPORT, exist_ok=True)

# 5 fitur clustering (total_loss TIDAK dipakai)
FEATURE_COLS = ["mean_loss", "max_loss", "std_loss", "trend_slope", "pct_recent"]
SCALED_COLS  = [f"{c}_scaled" for c in FEATURE_COLS]

# total_loss tetap ada di CSV untuk keperluan summary & dashboard
ALL_STAT_COLS = ["total_loss"] + FEATURE_COLS

K_RANGE      = range(2, 8)
RANDOM_STATE = 42

CLUSTER_COLORS = ["#2166ac", "#d73027", "#1a9850", "#f46d43", "#762a83", "#fee08b", "#4d4d4d"]

plt.rcParams.update({
    "figure.dpi": 150, "font.family": "DejaVu Sans",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.3,
    "axes.titlesize": 12, "axes.labelsize": 10,
})

def save(fig, fname):
    fig.savefig(os.path.join(OUT_REPORT, fname), bbox_inches="tight")
    plt.close(fig)
    print(f"  [✓] {fname}")


# ─────────────────────────────────────────────
# 1. ELBOW + SILHOUETTE
# ─────────────────────────────────────────────

def elbow_silhouette(X_scaled: np.ndarray, name: str) -> int:
    inertias, sil_scores = [], []

    for k in K_RANGE:
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
        km.fit(X_scaled)
        inertias.append(km.inertia_)
        sil_scores.append(silhouette_score(X_scaled, km.labels_))

    k_list    = list(K_RANGE)
    k_optimal = k_list[int(np.argmax(sil_scores))]

    # Elbow
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(k_list, inertias, marker="o", color="#2166ac", linewidth=2)
    ax.set_title(f"Elbow Method — {name.capitalize()}")
    ax.set_xlabel("Jumlah Kluster (k)")
    ax.set_ylabel("Inertia (Within-Cluster SSE)")
    ax.set_xticks(k_list)
    save(fig, f"elbow_{name}.png")

    # Silhouette
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(
        k_list, sil_scores,
        color=["#d73027" if k == k_optimal else "#92c5de" for k in k_list],
        edgecolor="white", width=0.6,
    )
    for bar, val in zip(bars, sil_scores):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.003,
                f"{val:.3f}", ha="center", va="bottom", fontsize=9)
    ax.set_title(f"Silhouette Score — {name.capitalize()}")
    ax.set_xlabel("Jumlah Kluster (k)")
    ax.set_ylabel("Silhouette Score")
    ax.set_xticks(k_list)
    ax.annotate(
        f"k optimal = {k_optimal}",
        xy=(k_optimal, max(sil_scores)),
        xytext=(k_optimal + 0.4, max(sil_scores) - 0.02),
        fontsize=9, color="#d73027",
        arrowprops=dict(arrowstyle="->", color="#d73027", lw=1.2),
    )
    save(fig, f"silhouette_{name}.png")

    print(f"  Silhouette : { {k: round(s,3) for k, s in zip(k_list, sil_scores)} }")
    print(f"  → k optimal: {k_optimal}")
    return k_optimal


# ─────────────────────────────────────────────
# 2. RADAR CHART
# ─────────────────────────────────────────────

def radar_chart(summary_df: pd.DataFrame, name: str):
    labels  = FEATURE_COLS
    n_feat  = len(labels)
    angles  = np.linspace(0, 2 * np.pi, n_feat, endpoint=False).tolist()
    angles += angles[:1]

    norm = summary_df[labels].copy()
    for col in labels:
        mn, mx = norm[col].min(), norm[col].max()
        norm[col] = (norm[col] - mn) / (mx - mn + 1e-9)

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"polar": True})
    for i, row in norm.iterrows():
        values = row[labels].tolist() + [row[labels[0]]]
        color  = CLUSTER_COLORS[i % len(CLUSTER_COLORS)]
        ax.plot(angles, values, color=color, linewidth=2, label=f"Kluster {i}")
        ax.fill(angles, values, color=color, alpha=0.12)

    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=8.5)
    ax.set_ylim(0, 1)
    ax.set_title(f"Profil Kluster — {name.capitalize()}", pad=18)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=8.5)
    save(fig, f"radar_{name}.png")


# ─────────────────────────────────────────────
# 3. AUTO LABEL (v2 — tanpa total_loss)
# ─────────────────────────────────────────────

def auto_label(row: pd.Series, p25_mean: float, p75_mean: float) -> str:
    """
    Label berdasarkan mean_loss (severity), trend_slope (arah),
    dan pct_recent (tekanan terkini).

    mean_loss dipakai sebagai proxy severity karena sudah dinormalisasi
    per-tahun → tidak bias oleh luas wilayah seperti total_loss.
    """
    mean   = row["mean_loss"]
    slope  = row["trend_slope"]
    recent = row["pct_recent"]
    std    = row["std_loss"]

    # Severity dari mean_loss
    if mean >= p75_mean:
        severity = "Tinggi"
    elif mean <= p25_mean:
        severity = "Rendah"
    else:
        severity = "Sedang"

    # Arah tren
    if slope > 0 and recent > 50:
        trend = "Meningkat"
    elif slope < 0 and recent < 40:
        trend = "Menurun"
    elif abs(slope) < 50 or (40 <= recent <= 55):
        trend = "Stabil"
    else:
        trend = "Fluktuatif"

    return f"{severity} – {trend}"


# ─────────────────────────────────────────────
# 4. PIPELINE
# ─────────────────────────────────────────────

def run_clustering(feat_path: str, id_cols: list[str], name: str):
    print(f"\n{'─'*50}")
    print(f"  Level: {name.upper()}")
    print(f"  Fitur clustering: {FEATURE_COLS}")
    print(f"{'─'*50}")

    df = pd.read_csv(feat_path)
    X  = df[SCALED_COLS].values

    print(f"  Data: {df.shape[0]} wilayah × {len(SCALED_COLS)} fitur (scaled)")

    # Cek SCALED_COLS tersedia
    missing = [c for c in SCALED_COLS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Kolom berikut tidak ada di {feat_path}: {missing}\n"
            f"Pastikan feature_engineering.py v2 sudah dijalankan ulang."
        )

    print("\n  Mencari k optimal …")
    k_opt = elbow_silhouette(X, name)

    print(f"\n  Training KMeans(k={k_opt}) …")
    km = KMeans(n_clusters=k_opt, random_state=RANDOM_STATE, n_init=20)
    km.fit(X)
    df["cluster"] = km.labels_

    joblib.dump(km, os.path.join(OUT_DATA, f"kmeans_{name}.pkl"))
    print(f"  [✓] kmeans_{name}.pkl")

    # Summary: rata-rata SEMUA statistik per kluster (termasuk total_loss untuk dashboard)
    stat_cols_available = [c for c in ALL_STAT_COLS if c in df.columns]
    summary = df.groupby("cluster")[stat_cols_available].mean().reset_index()

    # Auto-label berdasarkan mean_loss
    p25_mean = df["mean_loss"].quantile(0.25)
    p75_mean = df["mean_loss"].quantile(0.75)
    summary["label"] = summary.apply(
        lambda row: auto_label(row, p25_mean, p75_mean), axis=1
    )
    summary["n_wilayah"] = df.groupby("cluster").size().values

    print("\n  ── Ringkasan Kluster ──")
    display_cols = ["cluster", "label", "n_wilayah", "mean_loss", "std_loss",
                    "trend_slope", "pct_recent"]
    if "total_loss" in summary.columns:
        display_cols.insert(3, "total_loss")
    print(summary[display_cols].to_string(index=False, float_format="{:,.1f}".format))

    # Simpan summary
    sum_path = os.path.join(OUT_REPORT, f"cluster_summary_{name}.csv")
    summary.to_csv(sum_path, index=False)
    print(f"\n  [✓] cluster_summary_{name}.csv")

    radar_chart(summary, name)

    # Hasil akhir per wilayah
    label_map = summary.set_index("cluster")["label"].to_dict()
    df["cluster_label"] = df["cluster"].map(label_map)
    result = df[id_cols + stat_cols_available + ["cluster", "cluster_label"]]

    result.to_csv(os.path.join(OUT_DATA, f"cluster_result_{name}.csv"), index=False)
    print(f"  [✓] cluster_result_{name}.csv")

    return result, summary


# ─────────────────────────────────────────────
# 5. MAIN
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("  ForestWatch Sumatera — K-Means Clustering v2")
print("  Fitur: mean/max/std_loss, trend_slope, pct_recent")
print("  (total_loss dikeluarkan dari clustering)")
print("="*60)

result_prov, summary_prov = run_clustering(
    os.path.join(DATA_DIR, "cluster_features_province.csv"),
    id_cols=["province"], name="province",
)
result_dist, summary_dist = run_clustering(
    os.path.join(DATA_DIR, "cluster_features_district.csv"),
    id_cols=["province", "district"], name="district",
)

print("\n" + "="*60)
print("  Clustering v2 selesai!")
print(f"  Model : data/processed/kmeans_*.pkl")
print(f"  Hasil : data/processed/cluster_result_*.csv")
print(f"  Grafik: reports/clustering/")
print("="*60 + "\n")