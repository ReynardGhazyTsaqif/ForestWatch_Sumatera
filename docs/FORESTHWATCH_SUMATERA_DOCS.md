# ForestWatch Sumatera — Project Documentation

> **Dokumen ini dibuat untuk memudahkan onboarding di sesi/chat baru.**
> Baca dari atas ke bawah untuk memahami konteks penuh proyek sebelum melanjutkan.

---

## 1. Ringkasan Proyek

**ForestWatch Sumatera** adalah aplikasi web interaktif berbasis **Streamlit** untuk visualisasi dan analisis spasio-temporal kehilangan tutupan pohon (*tree cover loss*) di Pulau Sumatera periode **2001–2024**.

Aplikasi ini menggabungkan:
- Visualisasi peta choropleth interaktif (Folium)
- Analisis tren tahunan (Plotly)
- K-Means Clustering untuk pengelompokan wilayah

**Luaran akhir:**
1. Aplikasi Streamlit yang dapat dijalankan lokal maupun di-deploy
2. Artikel ilmiah
3. Video presentasi

---

## 2. Ruang Lingkup

### Wilayah
Pulau Sumatera — 10 provinsi:

| No | Provinsi |
|----|----------|
| 1 | Aceh |
| 2 | Sumatera Utara |
| 3 | Sumatera Barat |
| 4 | Riau |
| 5 | Jambi |
| 6 | Sumatera Selatan |
| 7 | Bengkulu |
| 8 | Lampung |
| 9 | Kepulauan Riau |
| 10 | Kepulauan Bangka Belitung |

### Level Analisis
- **Level 1:** Provinsi
- **Level 2:** Kabupaten/Kota (151 kabupaten/kota — 3 kabupaten pemekaran baru tidak ada datanya di GFW)

---

## 3. Dataset

### Sumber Data
**Global Forest Watch (GFW)** — diunduh manual per wilayah dalam format ZIP.

### Struktur File ZIP (dari GFW)
Setiap ZIP berisi beberapa file CSV:

| File | Keterangan |
|------|------------|
| `treecover_loss__ha.csv` | **File utama** — data kehilangan tutupan pohon per tahun |
| `adm1_metadata.csv` | Mapping kode adm1 → nama provinsi |
| `adm2_metadata.csv` | Mapping kode adm2 → nama kabupaten/kota |
| `treecover_extent_2000__ha.csv` | Luas tutupan pohon tahun 2000 (referensi) |
| `metadata.csv` | Metadata unduhan (threshold, tahun, link, dll.) |

### Skema Kolom Data Mentah

**treecover_loss__ha.csv (Provinsi):**
```
iso, adm1, umd_tree_cover_loss__year, umd_tree_cover_loss__ha, gfw_gross_emissions_co2e_all_gases__Mg
IDN, 5, 2001, 18277.9, 10876310.2
```

**treecover_loss__ha.csv (Kabupaten/Kota):**
```
iso, adm1, adm2, umd_tree_cover_loss__year, umd_tree_cover_loss__ha, gfw_gross_emissions_co2e_all_gases__Mg
IDN, 3, 2, 2001, 708.2, 502354.4
```

### Lokasi Dataset Lokal
```
D:\Unand\Sems 6\Visdat Spasial Temporal\UAS\
├── Dataset\                         ← ZIP provinsi
└── Dataset\Dataset Kota\            ← ZIP kabupaten (subfolder per provinsi)
```

---

## 4. Teknologi

| Kategori | Library |
|----------|---------|
| Bahasa | Python |
| Data Processing | Pandas, NumPy |
| Spatial Processing | GeoPandas, Shapely |
| Machine Learning | Scikit-Learn |
| Visualisasi | Plotly, Folium |
| Dashboard | Streamlit |

---

## 5. Struktur Folder Proyek

```
D:\Unand\Sems 6\Visdat Spasial Temporal\UAS\Visdat Spasio Deforestasi Sumatera\
│
├── data\
│   ├── processed\
│   │   ├── province_master.csv               ✅ SELESAI
│   │   ├── district_master.csv               ✅ SELESAI
│   │   ├── cluster_features_province.csv     ✅ SELESAI
│   │   ├── cluster_features_district.csv     ✅ SELESAI
│   │   ├── cluster_result_province.csv       ✅ SELESAI
│   │   ├── cluster_result_district.csv       ✅ SELESAI
│   │   ├── scaler_province.pkl               ✅ SELESAI
│   │   ├── scaler_district.pkl               ✅ SELESAI
│   │   ├── kmeans_province.pkl               ✅ SELESAI
│   │   └── kmeans_district.pkl               ✅ SELESAI
│   └── geojson\
│       ├── province.geojson                  ✅ SELESAI
│       ├── district.geojson                  ✅ SELESAI
│       └── prepare_geojson.py                ✅ SELESAI (v2)
│
├── reports\
│   ├── eda\                                  ✅ SELESAI
│   │   ├── A1_tren_sumatera_total.png
│   │   ├── A2_tren_sumatera_co2.png
│   │   ├── B1_total_loss_per_provinsi.png
│   │   ├── B2_tren_per_provinsi.png
│   │   ├── B3_heatmap_provinsi_tahun.png
│   │   ├── C1_top10_kabupaten_total.png
│   │   ├── C2_top10_kabupaten_per_tahun.png
│   │   ├── D1_histogram_loss.png
│   │   ├── D2_boxplot_per_provinsi.png
│   │   ├── E1_scatter_loss_co2.png
│   │   └── summary_insights.txt
│   └── clustering\                           ✅ SELESAI
│       ├── elbow_province.png
│       ├── elbow_district.png
│       ├── silhouette_province.png
│       ├── silhouette_district.png
│       ├── radar_province.png
│       ├── radar_district.png
│       ├── cluster_summary_province.csv
│       └── cluster_summary_district.csv
│
├── src\
│   ├── eda.py                                ✅ SELESAI
│   ├── feature_engineering.py               ✅ SELESAI
│   ├── clustering.py                        ✅ SELESAI
│   ├── visualization.py                     ✅ SELESAI
│   ├── preprocessing\
│   └── utils\
│
├── collect_datasets.py                       ✅ SELESAI (v4)
├── streamlit_app.py                          ← BELUM
└── requirements.txt                          ← BELUM
```

---

## 6. Skema Dataset Output

### province_master.csv ✅
```
province, year, tree_cover_loss_ha, co2_emissions
Aceh, 2001, 18277.9, 10876310.2
```
- 10 provinsi × 24 tahun = 240 baris

### district_master.csv ✅
```
province, district, year, tree_cover_loss_ha, co2_emissions
Bangka Belitung, Bangka Selatan, 2001, 708.2, 502354.4
```
- 151 kabupaten/kota × 24 tahun = ±3624 baris

### province.geojson ✅
- 10 fitur (MultiPolygon), CRS: EPSG:4326
- Kolom utama: `province`, `KODE_PROV`, `geometry`

### district.geojson ✅
- 154 fitur (hasil dissolve dari level desa), CRS: EPSG:4326
- Kolom utama: `province`, `district`, `geometry`
- 3 kabupaten pemekaran baru tidak ada di CSV (tampil abu-abu di peta)

### cluster_features_province.csv / cluster_features_district.csv ✅
```
province/district, total_loss, mean_loss, max_loss, std_loss, trend_slope, pct_recent,
[+ versi _scaled untuk setiap fitur]
```

### cluster_result_province.csv / cluster_result_district.csv ✅
```
province/district, [6 fitur], cluster, cluster_label
```

---

## 7. Tahapan Proyek & Status

| # | Tahap | Status | Keterangan |
|---|-------|--------|------------|
| 1 | Persiapan Data | ✅ **SELESAI** | `province_master.csv` dan `district_master.csv` via `collect_datasets.py` v4 |
| 2 | Persiapan Data Spasial | ✅ **SELESAI** | `province.geojson` dan `district.geojson`, join 10/10 provinsi, 151/154 kabupaten |
| 3 | EDA | ✅ **SELESAI** | `src/eda.py` — 10 grafik PNG + `summary_insights.txt` di `reports/eda/` |
| 4 | Feature Engineering | ✅ **SELESAI** | `src/feature_engineering.py` — 6 fitur + StandardScaler tersimpan sebagai `.pkl` |
| 5 | K-Means Clustering | ✅ **SELESAI** | `src/clustering.py` — Elbow + Silhouette, model `.pkl`, hasil `cluster_result_*.csv` |
| 6 | Visualisasi | ✅ **SELESAI** | `src/visualization.py` — 7 fungsi (Folium + Plotly), di-import oleh Streamlit |
| 7 | Dashboard Streamlit | ⬜ **BERIKUTNYA** | `streamlit_app.py` — KPI, mode analisis, integrasi semua visualisasi |
| 8 | Evaluasi | ⬜ Belum | Evaluasi clustering & fungsionalitas |

---

## 8. Catatan Teknis Penting

### collect_datasets.py (v4 — versi final)
- Nama wilayah diambil dari nama file ZIP menggunakan regex
- Format: `"Kehilangan tutupan pohon di <WILAYAH>, <INDUK>, Indonesia.zip"`
- v1–v3 gagal karena mapping via `adm1_metadata` (type mismatch int vs str)

### prepare_geojson.py (v2 — versi final)
- `Kabupaten.json` adalah level desa (518 fitur) → dissolve ke level kabupaten → 154 fitur
- Kolom: `PROVINSI`, `WADMPR`, `WADMKK`
- Mapping nama: `PROVINCE_NAME_MAP` dan `DISTRICT_NAME_MAP` di dalam script

### eda.py (v1)
- Output statis PNG via Matplotlib + Seaborn
- Palet warna 10 warna konsisten per provinsi (`PROVINCE_PALETTE`)
- Korelasi via `scipy.stats.pearsonr`
- Auto-buat `reports/eda/` + `summary_insights.txt`

### feature_engineering.py (v1)
- 6 fitur: `total_loss`, `mean_loss`, `max_loss`, `std_loss`, `trend_slope`, `pct_recent`
- `trend_slope` = OLS slope (ha/tahun) via `scipy.stats.linregress`
- `pct_recent` = % loss 2015–2024 vs total
- StandardScaler disimpan sebagai `scaler_*.pkl` via `joblib`

### clustering.py (v1)
- Uji k=2–7, pilih k optimal dari silhouette tertinggi (otomatis)
- KMeans final dengan `n_init=20`, `random_state=42`
- Auto-label kluster berdasarkan `total_loss` (kuartil) + `trend_slope` + `pct_recent`
- Output: model `.pkl`, `cluster_result_*.csv`, grafik di `reports/clustering/`
- **Catatan:** setelah jalankan, cek `cluster_summary_*.csv` dan rename label kluster manual jika perlu sebelum lanjut ke Streamlit

### visualization.py (v1)
- Modul murni — **tidak dijalankan langsung**, di-import oleh `streamlit_app.py`
- 7 fungsi tersedia:

| Fungsi | Tipe Output | Kegunaan |
|--------|-------------|----------|
| `choropleth_loss_year()` | Folium Map | Peta loss per tahun (dikontrol slider) |
| `choropleth_cluster()` | Folium Map | Peta warna kluster + legend otomatis |
| `line_trend()` | Plotly Figure | Tren tahunan wilayah terpilih |
| `bar_ranking()` | Plotly Figure | Ranking loss/CO₂ per tahun atau total |
| `heatmap_province_year()` | Plotly Figure | Heatmap provinsi × tahun |
| `scatter_loss_co2()` | Plotly Figure | Scatter loss vs CO₂ + trendline OLS |
| `radar_cluster()` | Plotly Figure | Radar profil fitur antar kluster |

- Semua fungsi menerima `level="province"/"district"` dan `metric="tree_cover_loss_ha"/"co2_emissions"`

### 3 kabupaten tanpa data (bukan error)
- **Musi Rawas Utara**, **Penukal Abab Lematang Ilir**, **Pesisir Barat** — pemekaran 2012–2013
- Ada di GeoJSON, tidak di CSV → tampil abu-abu di peta (informatif)

---

## 9. Detail Tahap Berikutnya — Tahap 7: Dashboard Streamlit

### Struktur Halaman
Dashboard dibagi menjadi **3 halaman** via `st.sidebar`:

**Halaman 1 — Ringkasan (Overview)**
- KPI cards: total loss Sumatera, total CO₂, tahun puncak, provinsi terparah
- Line chart tren keseluruhan Sumatera (2001–2024)
- Heatmap provinsi × tahun

**Halaman 2 — Eksplorasi Spasial**
- Selector: level (provinsi/kabupaten), tahun, metrik
- Choropleth Folium loss per tahun (dikontrol slider tahun)
- Bar ranking wilayah di bawah peta
- Line chart tren untuk wilayah yang diklik/dipilih

**Halaman 3 — Analisis Kluster**
- Choropleth Folium warna kluster
- Radar chart profil kluster (Plotly)
- Tabel ringkasan kluster (`cluster_summary_*.csv`)
- Filter: tampilkan wilayah per kluster tertentu

### Catatan Implementasi
- Gunakan `streamlit-folium` (`st_folium`) untuk render peta Folium
- Cache data dengan `@st.cache_data` untuk semua file CSV dan GeoJSON
- Simpan state selector (level, tahun, metrik) di `st.session_state`
- File: `streamlit_app.py` di root proyek

---

## 10. File Penting

| File | Lokasi | Keterangan |
|------|--------|------------|
| `collect_datasets.py` (v4) | Root | Pengumpul data dari ZIP GFW |
| `prepare_geojson.py` (v2) | `data/geojson/` | Preprocessing GeoJSON |
| `eda.py` (v1) | `src/` | EDA lengkap |
| `feature_engineering.py` (v1) | `src/` | Hitung 6 fitur + StandardScaler |
| `clustering.py` (v1) | `src/` | K-Means + evaluasi + labeling |
| `visualization.py` (v1) | `src/` | 7 fungsi visualisasi (Folium + Plotly) |
| `province_master.csv` | `data/processed/` | Dataset provinsi bersih |
| `district_master.csv` | `data/processed/` | Dataset kabupaten/kota bersih |
| `cluster_features_*.csv` | `data/processed/` | Fitur clustering (mentah + scaled) |
| `cluster_result_*.csv` | `data/processed/` | Hasil label kluster per wilayah |
| `scaler_*.pkl` | `data/processed/` | StandardScaler tersimpan |
| `kmeans_*.pkl` | `data/processed/` | Model K-Means tersimpan |
| `province.geojson` | `data/geojson/` | Batas wilayah provinsi |
| `district.geojson` | `data/geojson/` | Batas wilayah kabupaten/kota |

---

*Dokumen diperbarui: 25 Juni 2026*
*Sesi berikutnya: Lanjutkan dari Tahap 7 — Dashboard Streamlit*