


"""
ForestWatch Sumatera - GeoJSON Preparation v2
=============================================
Fix: tambah mapping lengkap nama provinsi & kabupaten/kota
     antara GeoJSON dan CSV master
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path

# ==============================================================================
# CONFIG
# ==============================================================================

PROVINSI_JSON   = r"D:\Unand\Sems 6\Visdat Spasial Temporal\UAS\Visdat Spasio Deforestasi Sumatera\data\geojson\Provinsi.json"
KABUPATEN_JSON  = r"D:\Unand\Sems 6\Visdat Spasial Temporal\UAS\Visdat Spasio Deforestasi Sumatera\data\geojson\Kabupaten.json"

PROVINCE_MASTER = r"D:\Unand\Sems 6\Visdat Spasial Temporal\UAS\Visdat Spasio Deforestasi Sumatera\data\processed\province_master.csv"
DISTRICT_MASTER = r"D:\Unand\Sems 6\Visdat Spasial Temporal\UAS\Visdat Spasio Deforestasi Sumatera\data\processed\district_master.csv"

OUTPUT_DIR      = r"D:\Unand\Sems 6\Visdat Spasial Temporal\UAS\Visdat Spasio Deforestasi Sumatera\data\geojson"

PROVINSI_SUMATERA = [
    "Aceh", "Sumatera Utara", "Sumatera Barat", "Riau", "Jambi",
    "Sumatera Selatan", "Bengkulu", "Lampung", "Kepulauan Riau",
    "Kepulauan Bangka Belitung",
]

# ==============================================================================
# MAPPING NAMA
# Kiri  = nama di GeoJSON  |  Kanan = nama di CSV master (dari GFW)
# ==============================================================================

PROVINCE_NAME_MAP = {
    "Kepulauan Bangka Belitung": "Bangka Belitung",
}

DISTRICT_NAME_MAP = {
    # Kota — GeoJSON pakai "Kota X", CSV pakai nama kota saja
    "Kota Banda Aceh":          "Banda Aceh",
    "Kota Bandar Lampung":      "Bandar Lampung",
    "Kota Batam":               "Batam",
    "Kota Bengkulu":            "Bengkulu",
    "Kota Bukittinggi":         "Bukittinggi",
    "Kota Dumai":               "Dumai",
    "Kota Gunungsitoli":        "Gunungsitoli",
    "Kota Jambi":               "Jambi",
    "Kota Langsa":              "Langsa",
    "Kota Lhokseumawe":         "Lhokseumawe",
    "Kota Lubuk Linggau":       "Lubuklinggau",
    "Kota Metro":               "Metro",
    "Kota Padang":              "Padang",
    "Kota Padang Panjang":      "Padang Panjang",
    "Kota Padang Sidempuan":    "Padangsidimpuan",
    "Kota Pagar Alam":          "Pagar Alam",
    "Kota Palembang":           "Palembang",
    "Kota Pangkal Pinang":      "Pangkalpinang",
    "Kota Pariaman":            "Pariaman",
    "Kota Payakumbuh":          "Payakumbuh",
    "Kota Pekanbaru":           "Pekanbaru",
    "Kota Pematangsiantar":     "Pematangsiantar",
    "Kota Prabumulih":          "Prabumulih",
    "Kota Sabang":              "Sabang",
    "Kota Sawahlunto":          "Sawahlunto",
    "Kota Sibolga":             "Sibolga",
    "Kota Subulussalam":        "Subulussalam",
    "Kota Sungai Penuh":        "Sungai Penuh",
    "Kota Tanjung Balai":       "Kota Tanjungbalai",
    "Kota Tanjung Pinang":      "Tanjungpinang",
    "Kota Tebing Tinggi":       "Tebingtinggi",
    # Kabupaten — perbedaan penulisan
    "Banyuasin":                "Banyu Asin",
    "Batanghari":               "Batang Hari",
    "Muko Muko":                "Mukomuko",
    "Musi Rawas Utara":         "Musi Rawas Utara",   # sama, cek lagi nanti
    "Pakpak Bharat":            "Pakpak Barat",
    "Penukal Abab Lematang Ilir": "Penukal Abab Lematang Ilir",  # sama
    "Pesisir Barat":            "Pesisir Barat",       # sama
    "Tanjung Jabung Barat":     "Tanjung Jabung B",
    "Tanjung Jabung Timur":     "Tanjung Jabung T",
    "Toba":                     "Toba Samosir",
    "Tulang Bawang":            "Tulangbawang",
}

# ==============================================================================
# TAHAP 1 — PROVINSI
# ==============================================================================

def prepare_province_geojson():
    print("\n" + "="*60)
    print("TAHAP 1: Provinsi.json")
    print("="*60)

    gdf = gpd.read_file(PROVINSI_JSON)

    # Filter Sumatera (pakai nama asli GeoJSON dulu)
    gdf_sum = gdf[gdf["PROVINSI"].isin(PROVINSI_SUMATERA)].copy()

    # Tambah satu yang belum masuk filter karena akan di-map namanya
    extra = gdf[gdf["PROVINSI"].isin(PROVINCE_NAME_MAP.keys()) & ~gdf["PROVINSI"].isin(PROVINSI_SUMATERA)]
    gdf_sum = pd.concat([gdf_sum, extra], ignore_index=True)

    # Standardisasi nama -> sesuai CSV master
    gdf_sum["province"] = gdf_sum["PROVINSI"].replace(PROVINCE_NAME_MAP)
    # Yang tidak ada di mapping tetap pakai nama asli
    mask = ~gdf_sum["PROVINSI"].isin(PROVINCE_NAME_MAP)
    gdf_sum.loc[mask, "province"] = gdf_sum.loc[mask, "PROVINSI"]

    if gdf_sum.crs is None or gdf_sum.crs.to_epsg() != 4326:
        gdf_sum = gdf_sum.to_crs(epsg=4326)

    gdf_out = gdf_sum[["province", "KODE_PROV", "geometry"]].copy()

    out = Path(OUTPUT_DIR)
    out.mkdir(parents=True, exist_ok=True)
    gdf_out.to_file(out / "province.geojson", driver="GeoJSON")
    print(f"[SAVED] province.geojson ({len(gdf_out)} fitur)")
    print(f"Provinsi: {sorted(gdf_out['province'].unique())}")
    return gdf_out


# ==============================================================================
# TAHAP 2 — KABUPATEN/KOTA
# ==============================================================================

def prepare_district_geojson():
    print("\n" + "="*60)
    print("TAHAP 2: Kabupaten.json (dissolve dari level desa)")
    print("="*60)

    print("Membaca file... (mungkin butuh waktu)")
    gdf = gpd.read_file(KABUPATEN_JSON)

    # Filter Sumatera
    gdf_sum = gdf[gdf["WADMPR"].isin(PROVINSI_SUMATERA)].copy()

    # Standardisasi nama kabupaten
    gdf_sum["district"] = gdf_sum["WADMKK"].replace(DISTRICT_NAME_MAP)
    mask = ~gdf_sum["WADMKK"].isin(DISTRICT_NAME_MAP)
    gdf_sum.loc[mask, "district"] = gdf_sum.loc[mask, "WADMKK"]

    # Standardisasi nama provinsi
    gdf_sum["province"] = gdf_sum["WADMPR"].replace(PROVINCE_NAME_MAP)
    mask2 = ~gdf_sum["WADMPR"].isin(PROVINCE_NAME_MAP)
    gdf_sum.loc[mask2, "province"] = gdf_sum.loc[mask2, "WADMPR"]

    # Dissolve ke level kabupaten
    print("Melakukan dissolve...")
    gdf_dissolved = (
        gdf_sum
        .dissolve(by=["province", "district"], as_index=False)
        [["province", "district", "geometry"]]
    )

    if gdf_dissolved.crs is None or gdf_dissolved.crs.to_epsg() != 4326:
        gdf_dissolved = gdf_dissolved.to_crs(epsg=4326)

    gdf_dissolved.to_file(Path(OUTPUT_DIR) / "district.geojson", driver="GeoJSON")
    print(f"[SAVED] district.geojson ({len(gdf_dissolved)} fitur)")
    return gdf_dissolved


# ==============================================================================
# TAHAP 3 — VALIDASI
# ==============================================================================

def validate_join(gdf_prov, gdf_dist):
    print("\n" + "="*60)
    print("TAHAP 3: Validasi Join")
    print("="*60)

    prov_master = pd.read_csv(PROVINCE_MASTER)
    dist_master = pd.read_csv(DISTRICT_MASTER)

    # Provinsi
    geo_p    = set(gdf_prov["province"].unique())
    csv_p    = set(prov_master["province"].dropna().unique())
    match_p  = geo_p & csv_p
    only_geo = geo_p - csv_p
    only_csv = csv_p - geo_p

    print(f"\n[PROVINSI] Match: {len(match_p)}/10")
    print(f"  OK  : {sorted(match_p)}")
    if only_geo: print(f"  GeoJSON only: {only_geo}")
    if only_csv: print(f"  CSV only    : {only_csv}")

    # Kabupaten
    geo_d    = set(gdf_dist["district"].unique())
    csv_d    = set(dist_master["district"].dropna().unique())
    match_d  = geo_d & csv_d
    only_geo2 = geo_d - csv_d
    only_csv2 = csv_d - geo_d

    print(f"\n[KABUPATEN/KOTA] Match: {len(match_d)} dari GeoJSON={len(geo_d)}, CSV={len(csv_d)}")
    if only_geo2:
        print(f"\n  GeoJSON tapi tidak di CSV ({len(only_geo2)}):")
        for x in sorted(only_geo2): print(f"    - {x}")
    if only_csv2:
        print(f"\n  CSV tapi tidak di GeoJSON ({len(only_csv2)}):")
        for x in sorted(only_csv2): print(f"    - {x}")
    if not only_geo2 and not only_csv2:
        print("  [SEMPURNA] Semua nama cocok!")


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("ForestWatch Sumatera - GeoJSON Preparation v2")
    gdf_prov = prepare_province_geojson()
    gdf_dist = prepare_district_geojson()
    validate_join(gdf_prov, gdf_dist)
    print("\n[DONE] Selesai!")