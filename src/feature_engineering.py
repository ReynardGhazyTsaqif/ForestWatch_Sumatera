import os
import joblib
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler

# ─────────────────────────────────────────────
# 0. KONFIGURASI
# ─────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PROVINCE = os.path.join(BASE_DIR, "data", "processed", "province_master.csv")
DATA_DISTRICT = os.path.join(BASE_DIR, "data", "processed", "district_master.csv")
OUT_DIR       = os.path.join(BASE_DIR, "data", "processed")

RECENT_START = 2015

# Semua statistik yang dihitung (disimpan di CSV)
STAT_COLS = ["total_loss", "mean_loss", "max_loss", "std_loss", "trend_slope", "pct_recent"]

# Hanya ini yang masuk ke clustering (total_loss dikeluarkan)
FEATURE_COLS = ["mean_loss", "max_loss", "std_loss", "trend_slope", "pct_recent"]


# ─────────────────────────────────────────────
# 1. FUNGSI HITUNG FITUR
# ─────────────────────────────────────────────

def compute_features(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    """
    Hitung statistik clustering dari time series tree_cover_loss_ha per wilayah.

    Kolom output:
        [*group_cols] + STAT_COLS (total_loss disertakan untuk referensi dashboard)

    Catatan: total_loss dihitung tapi tidak dipakai untuk clustering —
    lihat FEATURE_COLS di atas.
    """
    records = []

    for keys, grp in df.groupby(group_cols):
        grp   = grp.sort_values("year")
        loss  = grp["tree_cover_loss_ha"].values
        years = grp["year"].values.astype(float)

        total_loss = loss.sum()
        mean_loss  = loss.mean()
        max_loss   = loss.max()
        std_loss   = loss.std(ddof=1) if len(loss) > 1 else 0.0

        # OLS slope (ha/tahun)
        slope = stats.linregress(years, loss).slope if len(years) > 1 else 0.0

        # Proporsi loss periode terkini vs total
        recent_loss = grp.loc[grp["year"] >= RECENT_START, "tree_cover_loss_ha"].sum()
        pct_recent  = (recent_loss / total_loss * 100) if total_loss > 0 else 0.0

        row = dict(zip(group_cols, keys if isinstance(keys, tuple) else (keys,)))
        row.update({
            "total_loss":  total_loss,   # disimpan untuk dashboard, BUKAN fitur clustering
            "mean_loss":   mean_loss,
            "max_loss":    max_loss,
            "std_loss":    std_loss,
            "trend_slope": slope,
            "pct_recent":  pct_recent,
        })
        records.append(row)

    return pd.DataFrame(records)


def scale_and_save(features_df: pd.DataFrame, name: str) -> pd.DataFrame:
    """
    StandardScaler pada FEATURE_COLS (5 fitur, tanpa total_loss),
    simpan scaler ke .pkl, kembalikan DataFrame + kolom _scaled.
    """
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features_df[FEATURE_COLS])

    scaled_cols = [f"{c}_scaled" for c in FEATURE_COLS]
    scaled_df   = pd.DataFrame(scaled, columns=scaled_cols, index=features_df.index)
    result      = pd.concat([features_df, scaled_df], axis=1)

    scaler_path = os.path.join(OUT_DIR, f"scaler_{name}.pkl")
    joblib.dump(scaler, scaler_path)
    print(f"  [✓] Scaler disimpan : scaler_{name}.pkl")
    print(f"  [i] Fitur clustering : {FEATURE_COLS}")

    return result


# ─────────────────────────────────────────────
# 2. MAIN
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("  ForestWatch Sumatera — Feature Engineering v2")
print("  Fitur clustering: mean/max/std_loss, trend_slope, pct_recent")
print("  (total_loss dihitung tapi tidak dipakai clustering)")
print("="*60)

print("\n[1/4] Memuat data …")
prov_df = pd.read_csv(DATA_PROVINCE)
dist_df = pd.read_csv(DATA_DISTRICT)
prov_df["year"] = prov_df["year"].astype(int)
dist_df["year"] = dist_df["year"].astype(int)
print(f"  Provinsi  : {len(prov_df):,} baris")
print(f"  Kabupaten : {len(dist_df):,} baris")

print("\n[2/4] Menghitung fitur …")
feat_prov = compute_features(prov_df, group_cols=["province"])
feat_dist = compute_features(dist_df, group_cols=["province", "district"])
print(f"  Fitur provinsi  : {feat_prov.shape[0]} wilayah × {len(STAT_COLS)} statistik")
print(f"  Fitur kabupaten : {feat_dist.shape[0]} wilayah × {len(STAT_COLS)} statistik")
print(f"  Fitur masuk clustering : {FEATURE_COLS}")

print("\n[3/4] StandardScaler (5 fitur) …")
feat_prov_scaled = scale_and_save(feat_prov, "province")
feat_dist_scaled = scale_and_save(feat_dist, "district")

print("\n[4/4] Menyimpan CSV …")
feat_prov_scaled.to_csv(os.path.join(OUT_DIR, "cluster_features_province.csv"), index=False)
feat_dist_scaled.to_csv(os.path.join(OUT_DIR, "cluster_features_district.csv"), index=False)
print(f"  [✓] cluster_features_province.csv")
print(f"  [✓] cluster_features_district.csv")

print("\n── Preview: cluster_features_province.csv ──")
print(feat_prov[["province"] + STAT_COLS].to_string(index=False, float_format="{:,.1f}".format))

print("\n── Preview: Top 10 kabupaten (by mean_loss) ──")
print(feat_dist.nlargest(10, "mean_loss")[["province", "district"] + STAT_COLS]
      .to_string(index=False, float_format="{:,.1f}".format))

print("\n" + "="*60)
print("  Feature Engineering v2 selesai!")
print("="*60 + "\n")