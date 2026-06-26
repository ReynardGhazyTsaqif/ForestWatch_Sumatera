"""
ForestWatch Sumatera - Dataset Collector v3
===========================================
Fix:
- Kolom metadata adalah 'adm1__id' dan 'adm2__id' (bukan 'adm1'/'id')
- Mapping dilakukan dengan konversi tipe ke string agar cocok

CARA PENGGUNAAN:
    python collect_datasets.py

Sesuaikan CONFIG di bawah sebelum menjalankan.
"""

import zipfile
import pandas as pd
from pathlib import Path

# ==============================================================================
# CONFIG - SESUAIKAN PATH INI
# ==============================================================================

# Folder utama tempat semua ZIP provinsi berada
PROVINCE_ZIP_DIR = r"D:\Unand\Sems 6\Visdat Spasial Temporal\UAS\Visdat Spasio Deforestasi Sumatera\data\raw\Dataset Provinsi"

# Folder utama tempat semua ZIP kabupaten/kota berada (subfolder per provinsi)
DISTRICT_ZIP_DIR = r"D:\Unand\Sems 6\Visdat Spasial Temporal\UAS\Visdat Spasio Deforestasi Sumatera\data\raw\Dataset Kota\semua"

# Folder output untuk menyimpan hasil
OUTPUT_DIR = r"D:\Unand\Sems 6\Visdat Spasial Temporal\UAS\Visdat Spasio Deforestasi Sumatera\data\processed"

# ==============================================================================
# HELPER
# ==============================================================================

def read_csv_from_zip(z: zipfile.ZipFile, keyword: str) -> pd.DataFrame | None:
    """Cari dan baca CSV di dalam ZIP yang mengandung keyword."""
    matched = [
        name for name in z.namelist()
        if keyword.lower() in name.lower() and name.endswith(".csv")
    ]
    if not matched:
        return None
    with z.open(matched[0]) as f:
        return pd.read_csv(f)


def build_adm_map(meta_df: pd.DataFrame, id_keyword: str, name_keyword: str = "name") -> dict:
    """
    Bangun dict {id -> nama} dari metadata DataFrame.
    id_keyword: kata kunci untuk kolom ID (misal 'adm1__id' atau 'adm2__id')
    Semua key dikonversi ke string agar cocok saat mapping.
    """
    meta_df.columns = meta_df.columns.str.strip().str.lower()

    # Cari kolom ID yang mengandung keyword
    id_col = next((c for c in meta_df.columns if id_keyword.lower() in c), None)
    # Cari kolom nama
    name_col = next((c for c in meta_df.columns if name_keyword.lower() in c), None)

    if not id_col or not name_col:
        print(f"    [WARN] Kolom tidak ditemukan. Tersedia: {list(meta_df.columns)} | Dicari: id='{id_keyword}', name='{name_keyword}'")
        return {}

    # Konversi ID ke string agar tipe selalu cocok saat .map()
    mapping = {str(k).strip(): str(v).strip() for k, v in zip(meta_df[id_col], meta_df[name_col])}
    print(f"    [META] Kolom '{id_col}' -> '{name_col}' | {len(mapping)} entri | Contoh: {dict(list(mapping.items())[:3])}")
    return mapping


# ==============================================================================
# PROVINSI
# ==============================================================================

def process_province_zip(zip_path: Path) -> pd.DataFrame | None:
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:

            # 1. Baca adm1_metadata -> mapping adm1__id -> name
            meta1 = read_csv_from_zip(z, "adm1_metadata")
            adm1_map = build_adm_map(meta1, id_keyword="adm1__id") if meta1 is not None else {}

            # 2. Baca treecover_loss__ha
            loss_df = read_csv_from_zip(z, "treecover_loss__ha")
            if loss_df is None:
                print(f"  [SKIP] treecover_loss__ha tidak ditemukan di {zip_path.name}")
                return None

            loss_df.columns = loss_df.columns.str.strip().str.lower()
            print(f"    [DATA] Kolom treecover_loss: {list(loss_df.columns)}")
            print(f"    [DATA] Contoh adm1 values: {loss_df['adm1'].unique()[:5] if 'adm1' in loss_df.columns else 'kolom adm1 tidak ada'}")

            # Rename kolom ke standar
            loss_df = loss_df.rename(columns={
                "umd_tree_cover_loss__year":               "year",
                "umd_tree_cover_loss__ha":                 "tree_cover_loss_ha",
                "gfw_gross_emissions_co2e_all_gases__mg":  "co2_emissions",
            })

            # 3. Map adm1 -> nama provinsi (konversi ke string dulu)
            if adm1_map and "adm1" in loss_df.columns:
                loss_df["province"] = loss_df["adm1"].astype(str).str.strip().map(adm1_map)
            else:
                loss_df["province"] = _infer_name(zip_path)

            result = loss_df[["province", "year", "tree_cover_loss_ha", "co2_emissions"]].copy()
            result = result.dropna(subset=["year", "tree_cover_loss_ha"])
            result["year"] = result["year"].astype(int)

            unmapped = result["province"].isna().sum()
            if unmapped > 0:
                print(f"    [WARN] {unmapped} baris tidak ter-mapping ke nama provinsi!")

            print(f"  [OK] {zip_path.name}: {len(result)} baris | Provinsi: {result['province'].dropna().unique()}")
            return result

    except zipfile.BadZipFile:
        print(f"  [ERROR] ZIP rusak: {zip_path.name}")
    except Exception as e:
        print(f"  [ERROR] {zip_path.name}: {e}")
    return None


# ==============================================================================
# KABUPATEN/KOTA
# ==============================================================================

def process_district_zip(zip_path: Path) -> pd.DataFrame | None:
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:

            # 1. adm1_metadata -> nama provinsi
            meta1 = read_csv_from_zip(z, "adm1_metadata")
            adm1_map = build_adm_map(meta1, id_keyword="adm1__id") if meta1 is not None else {}

            # 2. adm2_metadata -> nama kabupaten/kota
            meta2 = read_csv_from_zip(z, "adm2_metadata")
            adm2_map = build_adm_map(meta2, id_keyword="adm2__id") if meta2 is not None else {}

            # 3. treecover_loss__ha
            loss_df = read_csv_from_zip(z, "treecover_loss__ha")
            if loss_df is None:
                print(f"  [SKIP] treecover_loss__ha tidak ditemukan di {zip_path.name}")
                return None

            loss_df.columns = loss_df.columns.str.strip().str.lower()
            print(f"    [DATA] Kolom treecover_loss: {list(loss_df.columns)}")

            loss_df = loss_df.rename(columns={
                "umd_tree_cover_loss__year":               "year",
                "umd_tree_cover_loss__ha":                 "tree_cover_loss_ha",
                "gfw_gross_emissions_co2e_all_gases__mg":  "co2_emissions",
            })

            # 4. Map kode -> nama
            if adm1_map and "adm1" in loss_df.columns:
                loss_df["province"] = loss_df["adm1"].astype(str).str.strip().map(adm1_map)
            else:
                loss_df["province"] = zip_path.parent.name

            if adm2_map and "adm2" in loss_df.columns:
                loss_df["district"] = loss_df["adm2"].astype(str).str.strip().map(adm2_map)
            else:
                loss_df["district"] = _infer_name(zip_path)

            result = loss_df[["province", "district", "year", "tree_cover_loss_ha", "co2_emissions"]].copy()
            result = result.dropna(subset=["year", "tree_cover_loss_ha"])
            result["year"] = result["year"].astype(int)

            unmapped_prov = result["province"].isna().sum()
            unmapped_dist = result["district"].isna().sum()
            if unmapped_prov > 0:
                print(f"    [WARN] {unmapped_prov} baris tidak ter-mapping ke nama provinsi!")
            if unmapped_dist > 0:
                print(f"    [WARN] {unmapped_dist} baris tidak ter-mapping ke nama kabupaten/kota!")

            print(f"  [OK] {zip_path.name}: {len(result)} baris | {result['province'].dropna().unique()} - {result['district'].dropna().unique()}")
            return result

    except zipfile.BadZipFile:
        print(f"  [ERROR] ZIP rusak: {zip_path.name}")
    except Exception as e:
        print(f"  [ERROR] {zip_path.name}: {e}")
    return None


def _infer_name(zip_path: Path) -> str:
    name = zip_path.stem
    if " di " in name:
        return name.split(" di ")[-1].split(",")[0].strip()
    return name


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("=" * 60)
    print("ForestWatch Sumatera - Dataset Collector v3")
    print("=" * 60)

    # --- PROVINSI ---
    print("\n[TAHAP 1] PROVINSI")
    prov_dir  = Path(PROVINCE_ZIP_DIR)
    prov_zips = list(prov_dir.glob("*.zip"))
    print(f"Ditemukan {len(prov_zips)} ZIP.")

    prov_dfs = []
    for z in prov_zips:
        print(f"\n-> {z.name}")
        df = process_province_zip(z)
        if df is not None:
            prov_dfs.append(df)

    # --- KABUPATEN/KOTA ---
    print("\n[TAHAP 2] KABUPATEN/KOTA")
    dist_dir  = Path(DISTRICT_ZIP_DIR)
    dist_zips = list(dist_dir.rglob("*.zip"))
    print(f"Ditemukan {len(dist_zips)} ZIP.")

    dist_dfs = []
    for z in dist_zips:
        print(f"\n-> {z.name}")
        df = process_district_zip(z)
        if df is not None:
            dist_dfs.append(df)

    # --- SIMPAN ---
    print("\n[TAHAP 3] MENYIMPAN OUTPUT")
    out = Path(OUTPUT_DIR)
    out.mkdir(parents=True, exist_ok=True)

    if prov_dfs:
        prov_master = (
            pd.concat(prov_dfs, ignore_index=True)
            .sort_values(["province", "year"])
            .reset_index(drop=True)
        )
        prov_master.to_csv(out / "province_master.csv", index=False)
        print(f"\n[SAVED] province_master.csv")
        print(f"  Baris          : {len(prov_master)}")
        print(f"  Provinsi unik  : {prov_master['province'].nunique()} -> {sorted(prov_master['province'].dropna().unique())}")
        print(f"  Rentang tahun  : {prov_master['year'].min()} - {prov_master['year'].max()}")
        print(prov_master.head(5).to_string(index=False))
    else:
        print("[WARN] Tidak ada data provinsi.")

    if dist_dfs:
        dist_master = (
            pd.concat(dist_dfs, ignore_index=True)
            .sort_values(["province", "district", "year"])
            .reset_index(drop=True)
        )
        dist_master.to_csv(out / "district_master.csv", index=False)
        print(f"\n[SAVED] district_master.csv")
        print(f"  Baris              : {len(dist_master)}")
        print(f"  Provinsi unik      : {dist_master['province'].nunique()}")
        print(f"  Kabupaten/Kota unik: {dist_master['district'].nunique()}")
        print(f"  Rentang tahun      : {dist_master['year'].min()} - {dist_master['year'].max()}")
        print(dist_master.head(5).to_string(index=False))
    else:
        print("[WARN] Tidak ada data kabupaten/kota.")

    print("\n[DONE] Selesai!")


if __name__ == "__main__":
    main()