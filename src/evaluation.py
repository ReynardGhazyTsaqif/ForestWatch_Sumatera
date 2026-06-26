"""
ForestWatch Sumatera — Evaluasi Clustering
==========================================
Mengevaluasi kualitas hasil K-Means clustering dengan metrik internal:
  - Silhouette Score (per kluster & global)
  - Davies-Bouldin Index
  - Calinski-Harabasz Index
  - Visualisasi PCA 2D
  - Distribusi fitur per kluster (boxplot)
  - Feature importance via variance kontribusi
  - Ringkasan komparatif provinsi vs kabupaten

Jalankan setelah clustering.py selesai:
    python src/evaluasi.py
"""

import os
import warnings
import joblib

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

from sklearn.decomposition import PCA
from sklearn.metrics import (
    silhouette_score,
    silhouette_samples,
    davies_bouldin_score,
    calinski_harabasz_score,
)

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# 0. KONFIGURASI
# ─────────────────────────────────────────────

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR   = os.path.join(BASE_DIR, "data", "processed")
REPORT_DIR = os.path.join(BASE_DIR, "reports", "clustering")

os.makedirs(REPORT_DIR, exist_ok=True)

FEATURE_COLS = ["mean_loss", "max_loss", "std_loss", "trend_slope", "pct_recent"]
SCALED_COLS  = [f"{c}_scaled" for c in FEATURE_COLS]

FEATURE_LABELS = {
    "mean_loss":   "Rerata Loss (ha/thn)",
    "max_loss":    "Puncak Loss (ha)",
    "std_loss":    "Variabilitas (Std)",
    "trend_slope": "Kemiringan Tren",
    "pct_recent":  "Loss Terkini (%)",
}

CLUSTER_COLORS = [
    "#2166ac", "#d73027", "#1a9850",
    "#f46d43", "#762a83", "#fee08b", "#4d4d4d",
]

plt.rcParams.update({
    "figure.dpi":        150,
    "font.family":       "DejaVu Sans",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "grid.alpha":        0.25,
    "axes.titlesize":    11,
    "axes.labelsize":    9,
    "xtick.labelsize":   8,
    "ytick.labelsize":   8,
    "legend.fontsize":   8.5,
})


# ─────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────

def save(fig: plt.Figure, fname: str):
    path = os.path.join(REPORT_DIR, fname)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  [✓] {fname}")


def cluster_palette(n: int) -> list[str]:
    return [CLUSTER_COLORS[i % len(CLUSTER_COLORS)] for i in range(n)]


# ─────────────────────────────────────────────
# 1. METRIK INTERNAL
# ─────────────────────────────────────────────

def compute_metrics(X: np.ndarray, labels: np.ndarray) -> dict:
    """
    Hitung tiga metrik evaluasi clustering internal.

    Interpretasi:
      Silhouette  ∈ [-1, 1]  → semakin tinggi semakin baik
      Davies-Bouldin ≥ 0     → semakin rendah semakin baik
      Calinski-Harabasz ≥ 0  → semakin tinggi semakin baik
    """
    sil  = silhouette_score(X, labels)
    db   = davies_bouldin_score(X, labels)
    ch   = calinski_harabasz_score(X, labels)
    return {"silhouette": sil, "davies_bouldin": db, "calinski_harabasz": ch}


def print_metrics(metrics: dict, name: str):
    print(f"\n  ── Metrik Internal [{name.upper()}] ──")
    print(f"  Silhouette Score      : {metrics['silhouette']:+.4f}  (baik jika > 0.50)")
    print(f"  Davies-Bouldin Index  : {metrics['davies_bouldin']:.4f}   (baik jika < 1.00)")
    print(f"  Calinski-Harabasz     : {metrics['calinski_harabasz']:,.1f}  (semakin tinggi semakin baik)")


# ─────────────────────────────────────────────
# 2. SILHOUETTE PER KLUSTER
# ─────────────────────────────────────────────

def plot_silhouette(X: np.ndarray, labels: np.ndarray, name: str):
    """
    Visualisasi silhouette coefficient tiap sampel, dikelompokkan per kluster.
    """
    sil_vals  = silhouette_samples(X, labels)
    k         = len(np.unique(labels))
    palette   = cluster_palette(k)
    global_sil = sil_vals.mean()

    fig, ax = plt.subplots(figsize=(8, max(4, k * 1.2)))
    y_lower = 10

    for i in range(k):
        vals_i = np.sort(sil_vals[labels == i])
        size_i = vals_i.shape[0]
        y_upper = y_lower + size_i

        ax.fill_betweenx(
            np.arange(y_lower, y_upper),
            0, vals_i,
            facecolor=palette[i], alpha=0.80, edgecolor="none"
        )
        ax.text(-0.05, y_lower + size_i / 2, f"K{i}", fontsize=8,
                va="center", ha="right", color=palette[i], fontweight="bold")
        y_lower = y_upper + 10

    ax.axvline(global_sil, color="#e74c3c", linestyle="--", linewidth=1.5,
               label=f"Rata-rata global = {global_sil:.3f}")
    ax.set_xlim([-0.2, 1.0])
    ax.set_xlabel("Silhouette Coefficient")
    ax.set_ylabel("Sampel (dikelompokkan per kluster)")
    ax.set_title(f"Silhouette per Kluster — {name.capitalize()}")
    ax.set_yticks([])
    ax.legend(loc="upper right")
    save(fig, f"eval_silhouette_{name}.png")


# ─────────────────────────────────────────────
# 3. PCA SCATTER 2D
# ─────────────────────────────────────────────

def plot_pca(
    X: np.ndarray,
    labels: np.ndarray,
    id_series: pd.Series,
    name: str,
):
    """
    Proyeksi 2D via PCA. Label wilayah ditampilkan di scatter point.
    Lingkaran kepercayaan (1-std ellipse) per kluster ditambahkan.
    """
    pca    = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X)
    var    = pca.explained_variance_ratio_ * 100
    k      = len(np.unique(labels))
    palette = cluster_palette(k)

    fig, ax = plt.subplots(figsize=(10, 7))

    for i in range(k):
        mask = labels == i
        xs, ys = coords[mask, 0], coords[mask, 1]
        color  = palette[i]

        ax.scatter(xs, ys, c=color, s=70, alpha=0.85,
                   edgecolors="white", linewidths=0.5, zorder=3)

        # Anotasi nama wilayah (dipotong bila terlalu panjang)
        for x, y, lbl in zip(xs, ys, id_series[mask].values):
            short = str(lbl)[:12] + ("…" if len(str(lbl)) > 12 else "")
            ax.annotate(short, (x, y), fontsize=5.5, alpha=0.75,
                        xytext=(3, 3), textcoords="offset points")

        # Ellipse 1-std (kovarians)
        if mask.sum() > 2:
            cx, cy = xs.mean(), ys.mean()
            sx, sy = xs.std(), ys.std()
            ellipse = plt.matplotlib.patches.Ellipse(
                (cx, cy), width=2 * sx, height=2 * sy,
                angle=0, color=color, alpha=0.10, zorder=1
            )
            ax.add_patch(ellipse)
            ax.scatter([cx], [cy], c=color, s=120, marker="X",
                       edgecolors="white", linewidths=0.8, zorder=4)

    # Legenda kluster
    handles = [
        mpatches.Patch(color=palette[i], label=f"Kluster {i}")
        for i in range(k)
    ]
    ax.legend(handles=handles, loc="upper right", framealpha=0.7)
    ax.set_xlabel(f"PC1 ({var[0]:.1f}% variansi)")
    ax.set_ylabel(f"PC2 ({var[1]:.1f}% variansi)")
    ax.set_title(f"Proyeksi PCA 2D — {name.capitalize()} (total variansi tertangkap: {sum(var):.1f}%)")
    save(fig, f"eval_pca_{name}.png")


# ─────────────────────────────────────────────
# 4. BOXPLOT DISTRIBUSI FITUR
# ─────────────────────────────────────────────

def plot_boxplot(df: pd.DataFrame, name: str):
    """
    Grid boxplot setiap fitur, dikelompokkan per kluster.
    Menunjukkan sebaran & outlier tiap kelompok.
    """
    k       = df["cluster"].nunique()
    palette = cluster_palette(k)
    n_feat  = len(FEATURE_COLS)

    fig, axes = plt.subplots(1, n_feat, figsize=(3.5 * n_feat, 5), sharey=False)
    if n_feat == 1:
        axes = [axes]

    for ax, feat in zip(axes, FEATURE_COLS):
        data_by_cluster = [
            df.loc[df["cluster"] == i, feat].dropna().values
            for i in sorted(df["cluster"].unique())
        ]
        bp = ax.boxplot(
            data_by_cluster,
            patch_artist=True,
            widths=0.55,
            medianprops=dict(color="white", linewidth=2),
            whiskerprops=dict(linewidth=1.2),
            capprops=dict(linewidth=1.2),
            flierprops=dict(marker="o", markersize=3, alpha=0.5),
        )
        for patch, color in zip(bp["boxes"], palette):
            patch.set_facecolor(color)
            patch.set_alpha(0.75)
        for flier, color in zip(bp["fliers"], palette):
            flier.set_markerfacecolor(color)

        ax.set_title(FEATURE_LABELS.get(feat, feat), pad=6)
        ax.set_xlabel("Kluster")
        ax.set_xticks(range(1, k + 1))
        ax.set_xticklabels([f"K{i}" for i in sorted(df["cluster"].unique())])

    fig.suptitle(f"Distribusi Fitur per Kluster — {name.capitalize()}", y=1.01, fontsize=12)
    plt.tight_layout()
    save(fig, f"eval_boxplot_{name}.png")


# ─────────────────────────────────────────────
# 5. FEATURE IMPORTANCE (VARIANCE BETWEEN-CLUSTER)
# ─────────────────────────────────────────────

def plot_feature_importance(df: pd.DataFrame, name: str):
    """
    Mengukur kontribusi setiap fitur menggunakan rasio variansi antar-kluster
    terhadap total variansi (eta-squared / Between-Cluster SS ratio).

    Interpretasi: fitur dengan rasio tinggi = pembeda kluster terkuat.
    """
    grand_mean = df[FEATURE_COLS].mean()
    ss_total   = {}
    ss_between = {}

    for feat in FEATURE_COLS:
        grand = grand_mean[feat]
        ss_total[feat]   = ((df[feat] - grand) ** 2).sum()
        ss_bet = 0
        for i, grp in df.groupby("cluster"):
            n_i    = len(grp)
            mean_i = grp[feat].mean()
            ss_bet += n_i * (mean_i - grand) ** 2
        ss_between[feat] = ss_bet

    eta_sq = {f: ss_between[f] / (ss_total[f] + 1e-9) for f in FEATURE_COLS}
    eta_df = (
        pd.Series(eta_sq)
        .rename("eta_squared")
        .reset_index()
        .rename(columns={"index": "feature"})
        .sort_values("eta_squared", ascending=True)
    )
    eta_df["label"] = eta_df["feature"].map(FEATURE_LABELS)

    fig, ax = plt.subplots(figsize=(8, 4))
    colors  = ["#d73027" if v >= 0.5 else "#2166ac" if v >= 0.25 else "#92c5de"
               for v in eta_df["eta_squared"]]
    bars = ax.barh(eta_df["label"], eta_df["eta_squared"],
                   color=colors, edgecolor="white", height=0.55)

    for bar, val in zip(bars, eta_df["eta_squared"]):
        ax.text(val + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{val:.3f}", va="center", fontsize=8.5, fontweight="bold")

    ax.axvline(0.50, color="#d73027", linestyle="--", linewidth=1.2, alpha=0.7,
               label="Threshold tinggi (η²≥0.50)")
    ax.axvline(0.25, color="#f46d43", linestyle=":", linewidth=1.2, alpha=0.7,
               label="Threshold sedang (η²≥0.25)")
    ax.set_xlim([0, 1.1])
    ax.set_xlabel("Eta-Squared (η²) — Rasio SS antar-kluster / SS total")
    ax.set_title(f"Kontribusi Fitur sebagai Pembeda Kluster — {name.capitalize()}")
    ax.legend(loc="lower right", framealpha=0.6)
    save(fig, f"eval_feature_importance_{name}.png")

    return eta_df


# ─────────────────────────────────────────────
# 6. RINGKASAN TABEL EVALUASI
# ─────────────────────────────────────────────

def save_eval_table(
    metrics_prov: dict,
    metrics_dist: dict,
    eta_prov: pd.DataFrame,
    eta_dist: pd.DataFrame,
):
    """
    Menyimpan ringkasan evaluasi ke CSV dan menampilkan tabel komparatif.
    """
    rows = []
    for name, metrics, eta in [
        ("province", metrics_prov, eta_prov),
        ("district", metrics_dist, eta_dist),
    ]:
        best_feat  = eta.sort_values("eta_squared", ascending=False).iloc[0]
        worst_feat = eta.sort_values("eta_squared", ascending=True).iloc[0]
        rows.append({
            "level":                name,
            "silhouette_score":     round(metrics["silhouette"], 4),
            "davies_bouldin_index": round(metrics["davies_bouldin"], 4),
            "calinski_harabasz":    round(metrics["calinski_harabasz"], 2),
            "best_discriminator":   best_feat["feature"],
            "best_eta_sq":          round(best_feat["eta_squared"], 4),
            "weakest_discriminator": worst_feat["feature"],
            "weakest_eta_sq":       round(worst_feat["eta_squared"], 4),
            "quality_judgement":    _judge(metrics),
        })

    eval_df = pd.DataFrame(rows)
    out_path = os.path.join(REPORT_DIR, "eval_summary.csv")
    eval_df.to_csv(out_path, index=False)
    print(f"\n  [✓] eval_summary.csv")

    print("\n" + "═" * 68)
    print("  TABEL RINGKASAN EVALUASI CLUSTERING")
    print("═" * 68)
    for _, row in eval_df.iterrows():
        print(f"\n  Level            : {row['level'].upper()}")
        print(f"  Silhouette Score : {row['silhouette_score']:+.4f}   ({_interpret_sil(row['silhouette_score'])})")
        print(f"  Davies-Bouldin   : {row['davies_bouldin_index']:.4f}    ({_interpret_db(row['davies_bouldin_index'])})")
        print(f"  Calinski-Harabasz: {row['calinski_harabasz']:,.1f}")
        print(f"  Pembeda Terkuat  : {row['best_discriminator']} (η²={row['best_eta_sq']:.3f})")
        print(f"  Pembeda Terlemah : {row['weakest_discriminator']} (η²={row['weakest_eta_sq']:.3f})")
        print(f"  Kualitas Kluster : {row['quality_judgement']}")
    print("═" * 68)

    return eval_df


def _judge(metrics: dict) -> str:
    sil = metrics["silhouette"]
    db  = metrics["davies_bouldin"]
    if sil >= 0.60 and db <= 0.80:
        return "✅ SANGAT BAIK — kluster kompak dan terpisah jelas"
    if sil >= 0.40 and db <= 1.20:
        return "✔️  CUKUP BAIK — struktur kluster cukup bermakna"
    if sil >= 0.25:
        return "⚠️  LEMAH — kluster ada tapi batas kabur, coba k berbeda"
    return "❌ BURUK — data mungkin tidak cocok dengan k ini"


def _interpret_sil(val: float) -> str:
    if val >= 0.70: return "Sangat baik"
    if val >= 0.50: return "Baik"
    if val >= 0.25: return "Sedang"
    return "Lemah"


def _interpret_db(val: float) -> str:
    if val <= 0.50: return "Sangat baik"
    if val <= 1.00: return "Baik"
    if val <= 1.50: return "Sedang"
    return "Lemah"


# ─────────────────────────────────────────────
# 7. PIPELINE UTAMA
# ─────────────────────────────────────────────

def evaluate(feat_path: str, result_path: str, id_col: str, name: str):
    """
    Pipeline evaluasi lengkap untuk satu level (province / district).
    """
    print(f"\n{'─' * 55}")
    print(f"  Evaluasi: {name.upper()}")
    print(f"{'─' * 55}")

    # Load data fitur (dengan kolom _scaled) dan hasil cluster
    feat_df   = pd.read_csv(feat_path)
    result_df = pd.read_csv(result_path)

    # Gabungkan cluster ke feat_df berdasarkan id_col
    # Tentukan kolom yang digunakan untuk merge
    merge_cols = [id_col]

    # Untuk level district, tambahkan province sebagai key merge
    if id_col != "province" and "province" in feat_df.columns and "province" in result_df.columns:
        merge_cols.append("province")
        
    df = feat_df.merge(result_df[[*merge_cols, "cluster", "cluster_label"]], on=merge_cols, how="left")
    df = df.dropna(subset=["cluster"])
    df["cluster"] = df["cluster"].astype(int)

    # Validasi kolom scaled
    missing = [c for c in SCALED_COLS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Kolom scaled tidak ditemukan: {missing}\n"
            "Jalankan ulang feature_engineering.py terlebih dahulu."
        )

    X      = df[SCALED_COLS].values
    labels = df["cluster"].values

    n_clusters = len(np.unique(labels))
    print(f"  Wilayah  : {len(df)}")
    print(f"  Kluster  : {n_clusters}")
    print(f"  Fitur    : {FEATURE_COLS}")

    # Distribusi per kluster
    print("\n  Distribusi wilayah per kluster:")
    for i, grp in df.groupby("cluster"):
        lbl = grp["cluster_label"].iloc[0]
        print(f"    K{i} ({lbl}): {len(grp)} wilayah")

    # Metrik internal
    metrics = compute_metrics(X, labels)
    print_metrics(metrics, name)

    # Plot
    print("\n  Menyimpan grafik evaluasi …")
    plot_silhouette(X, labels, name)
    plot_pca(X, labels, df[id_col], name)
    plot_boxplot(df, name)
    eta_df = plot_feature_importance(df, name)

    return metrics, eta_df


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  ForestWatch Sumatera — Evaluasi Clustering")
    print("  Metrik: Silhouette · Davies-Bouldin · Calinski-Harabasz")
    print("  Visualisasi: Silhouette · PCA · Boxplot · Eta-Squared")
    print("=" * 60)

    # ── Provinsi ──────────────────────────────────────────
    metrics_prov, eta_prov = evaluate(
        feat_path   = os.path.join(DATA_DIR, "cluster_features_province.csv"),
        result_path = os.path.join(DATA_DIR, "cluster_result_province.csv"),
        id_col      = "province",
        name        = "province",
    )

    # ── Kabupaten / Kota ──────────────────────────────────
    metrics_dist, eta_dist = evaluate(
        feat_path   = os.path.join(DATA_DIR, "cluster_features_district.csv"),
        result_path = os.path.join(DATA_DIR, "cluster_result_district.csv"),
        id_col      = "district",
        name        = "district",
    )

    # ── Ringkasan CSV + Tabel ─────────────────────────────
    save_eval_table(metrics_prov, metrics_dist, eta_prov, eta_dist)

    print(f"\n  Output tersimpan di: reports/clustering/")
    print("  File yang dihasilkan:")
    print("    eval_silhouette_province.png  — silhouette tiap sampel")
    print("    eval_silhouette_district.png")
    print("    eval_pca_province.png         — proyeksi PCA 2D")
    print("    eval_pca_district.png")
    print("    eval_boxplot_province.png     — distribusi fitur per kluster")
    print("    eval_boxplot_district.png")
    print("    eval_feature_importance_*.png — pembeda kluster terkuat")
    print("    eval_summary.csv              — tabel evaluasi komparatif")
    print("\n" + "=" * 60)
    print("  Evaluasi selesai!")
    print("=" * 60 + "\n")