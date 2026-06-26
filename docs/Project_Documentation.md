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
- **Level 2:** Kabupaten/Kota (seluruh kab/kota di 10 provinsi tersebut)

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

**adm1_metadata.csv:**
```
name, adm1__id
Aceh, 1
Bengkulu, 5
...
```

**adm2_metadata.csv:**
```
name, adm2__id
Bangka Selatan, 2
...
```

> **Catatan penting:** Kolom ID di metadata adalah `adm1__id` dan `adm2__id` (double underscore).
> Saat mapping, semua nilai ID harus dikonversi ke `str` karena tipe bisa berbeda antara data utama (int) dan metadata (str).

### Lokasi Dataset Lokal
```
D:\Unand\Sems 6\Visdat Spasial Temporal\UAS\
├── Dataset\Dataset Provinsi\                        ← ZIP provinsi (langsung di sini)
│   ├── Kehilangan tutupan pohon di Aceh, Indonesia.zip
│   ├── Kehilangan tutupan pohon di Bengkulu, Indonesia.zip
│   └── ...
│
└── Dataset\Dataset Kota\           ← ZIP kabupaten (subfolder per provinsi)
    ├── bengkulu\
    │   ├── Kehilangan tutupan pohon di Bengkulu Selatan, Bengkulu, Indonesia.zip
    │   └── ...
    └── ...
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
forestwatch-sumatera/
│
├── data/
│   ├── raw/
│   │   ├── province/          ← ZIP atau CSV mentah provinsi
│   │   └── district/          ← ZIP atau CSV mentah kabupaten
│   ├── processed/
│   │   ├── province_master.csv   ✅ SUDAH DIBUAT
│   │   └── district_master.csv   ✅ SUDAH DIBUAT
│   └── geojson/
│       ├── province.geojson      ← BELUM
│       └── district.geojson      ← BELUM
│
├── src/
│   ├── preprocessing/
│   ├── clustering/
│   ├── visualization/
│   └── utils/
│
├── app/
├── models/
├── reports/
├── docs/
│
├── streamlit_app.py
├── requirements.txt
└── collect_datasets.py        ✅ SUDAH DIBUAT (v3)
```

---

## 6. Skema Dataset Output

### province_master.csv ✅ Sudah dibuat
```
province, year, tree_cover_loss_ha, co2_emissions
Aceh, 2001, 18277.9, 10876310.2
Aceh, 2002, ...
```

### district_master.csv ✅ Sudah dibuat
```
province, district, year, tree_cover_loss_ha, co2_emissions
Bengkulu, Bengkulu Selatan, 2001, 708.2, 502354.4
Bengkulu, Bengkulu Selatan, 2002, ...
```

### cluster_features.csv ← BELUM
```
province/district, total_loss, mean_loss, max_loss, min_loss, std_loss
```

### cluster_result.csv ← BELUM
```
province/district, cluster_label
```

---

## 7. Tahapan Proyek & Status

| # | Tahap | Status | Keterangan |
|---|-------|--------|------------|
| 1 | Persiapan Data | ✅ **SELESAI** | `province_master.csv` dan `district_master.csv` sudah dibuat via `collect_datasets.py` |
| 2 | Persiapan Data Spasial | ⬜ Belum | Unduh GeoJSON provinsi & kabupaten, join dengan data master |
| 3 | Exploratory Data Analysis (EDA) | ⬜ Belum | Tren tahunan, wilayah loss tertinggi, distribusi, korelasi CO2 |
| 4 | Feature Engineering | ⬜ Belum | Hitung total/mean/max/min/std loss per wilayah → `cluster_features.csv` |
| 5 | K-Means Clustering | ⬜ Belum | Elbow method, Silhouette Score, training, simpan label → `cluster_result.csv` |
| 6 | Visualisasi Spasio-Temporal | ⬜ Belum | Choropleth, time slider, line chart, bar chart, cluster map |
| 7 | Dashboard Streamlit | ⬜ Belum | KPI, mode analisis, integrasi semua visualisasi |
| 8 | Evaluasi | ⬜ Belum | Evaluasi clustering & fungsionalitas sistem |

---

## 8. Detail Tahap Berikutnya (Tahap 2 — GeoJSON)

### Tujuan
Mendapatkan file GeoJSON batas wilayah provinsi dan kabupaten/kota di Sumatera untuk digunakan pada peta choropleth Folium.

### Sumber GeoJSON yang direkomendasikan
- **GADM** (https://gadm.org/download_country.html) — pilih Indonesia, Level 1 (Provinsi) dan Level 2 (Kabupaten)
- **Humanitarian Data Exchange (HDX)** — cari "Indonesia administrative boundaries"

### Langkah
1. Unduh GeoJSON Indonesia Level 1 → filter hanya 10 provinsi Sumatera → simpan sebagai `province.geojson`
2. Unduh GeoJSON Indonesia Level 2 → filter kabupaten/kota di 10 provinsi Sumatera → simpan sebagai `district.geojson`
3. Pastikan nama wilayah di GeoJSON cocok dengan nama di `province_master.csv` dan `district_master.csv` (perlu standardisasi jika berbeda)
4. Join GeoJSON dengan data master untuk validasi

### Potensi masalah
- Perbedaan ejaan nama wilayah antara GFW dan GADM (misal: "Jakarta Raya" vs "DKI Jakarta")
- Perlu membuat mapping manual jika ada perbedaan nama

---

## 9. Detail Tahap 3 — EDA

Analisis yang akan dilakukan:
- Tren kehilangan tutupan pohon per tahun (seluruh Sumatera)
- Tren per provinsi (line chart multi-series)
- Ranking provinsi berdasarkan total loss 2001–2024
- Ranking kabupaten/kota berdasarkan total loss
- Distribusi nilai tree_cover_loss_ha (histogram)
- Korelasi antara `tree_cover_loss_ha` dan `co2_emissions`
- Identifikasi tahun puncak kehilangan (per wilayah dan keseluruhan)

---

## 10. Detail Tahap 5 — K-Means Clustering

### Fitur yang digunakan
Dihitung dari data 2001–2024 per wilayah:

| Fitur | Deskripsi |
|-------|-----------|
| `total_loss` | Total kehilangan tutupan pohon selama 2001–2024 |
| `mean_loss` | Rata-rata kehilangan per tahun |
| `max_loss` | Kehilangan tertinggi dalam satu tahun |
| `min_loss` | Kehilangan terendah dalam satu tahun |
| `std_loss` | Standar deviasi kehilangan per tahun |

### Proses
1. StandardScaler untuk normalisasi fitur
2. Elbow Method (inertia) untuk menentukan nilai K optimal
3. Silhouette Score untuk validasi K
4. Training K-Means dengan K terpilih
5. Simpan label cluster ke `cluster_result.csv`

---

## 11. Detail Tahap 7 — Dashboard Streamlit

### Halaman Utama
- KPI: Total Tree Cover Loss (ha) seluruh Sumatera 2001–2024
- KPI: Total CO2 Emissions
- Wilayah terburuk (provinsi & kabupaten)
- Tahun terburuk

### Mode Analisis
Pengguna dapat memilih:
- **Mode Provinsi** — analisis di tingkat provinsi
- **Mode Kabupaten/Kota** — analisis di tingkat kabupaten/kota

### Komponen Visualisasi
- Peta Choropleth (Folium) dengan time slider 2001–2024
- Line chart tren kehilangan (Plotly)
- Bar chart ranking wilayah (Plotly)
- Peta cluster hasil K-Means (Folium)

---

## 12. File Penting yang Sudah Ada

| File | Lokasi | Keterangan |
|------|--------|------------|
| `collect_datasets.py` | Root proyek | Script pengumpul & preprocessing data dari ZIP GFW (v3) |
| `province_master.csv` | `data/processed/` | Dataset provinsi yang sudah bersih |
| `district_master.csv` | `data/processed/` | Dataset kabupaten/kota yang sudah bersih |
| `Project_Plan.md` | `docs/` | Dokumen rencana proyek awal |

---

## 13. Catatan Teknis Penting

- **collect_datasets.py v3** adalah versi yang benar dan sudah teruji. Versi sebelumnya (v1, v2) memiliki bug pada pembacaan nama kolom metadata.
- Kolom metadata GFW menggunakan `adm1__id` dan `adm2__id` (double underscore, bukan single).
- Mapping kode angka ke nama wilayah harus menggunakan `.astype(str).str.strip()` pada kedua sisi untuk menghindari type mismatch.
- Dataset GFW hanya berisi data Indonesia (iso=IDN), tidak perlu filter berdasarkan iso.
- Threshold tutupan pohon yang digunakan GFW adalah **30%** (sesuai metadata unduhan).

---

*Dokumen ini diperbarui: 25 Juni 2026*
*Sesi berikutnya: Lanjutkan dari Tahap 2 — Persiapan Data Spasial (GeoJSON)*