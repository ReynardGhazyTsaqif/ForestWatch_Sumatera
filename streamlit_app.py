"""
ForestWatch Sumatera — Dashboard Streamlit
Jalankan: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
import sys
import os

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT       = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(ROOT, "data", "processed")
REPORT_DIR = os.path.join(ROOT, "reports", "clustering")
GEO_DIR    = os.path.join(ROOT, "data", "geojson")
SRC_DIR    = os.path.join(ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from visualization import (
    choropleth_loss_year,
    choropleth_cluster,
    line_trend,
    bar_ranking,
    heatmap_province_year,
    scatter_loss_co2,
    radar_cluster,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ForestWatch Sumatera",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background-color: #060907 !important;
    background-image: radial-gradient(circle at 50% 50%, #0c1811 0%, #060907 100%) !important;
}

[data-testid="stMainBlockContainer"] {
    padding-top: 1rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 100% !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #070c08 !important;
    border-right: 1px solid rgba(52, 211, 153, 0.15) !important;
    min-width: 220px !important;
    max-width: 260px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1rem !important;
    padding-left: 0.85rem !important;
    padding-right: 0.85rem !important;
}

/* Semua teks di sidebar */
[data-testid="stSidebar"],
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {
    color: #e2ede8 !important;
}

/* ── Radio sebagai nav button ── */
[data-testid="stSidebar"] .stRadio > label {
    display: none !important; /* sembunyikan label radio group */
}
[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 3px !important;
}
[data-testid="stSidebar"] .stRadio div[data-testid="stMarkdownContainer"] p {
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    color: #a1b5ad !important;
    margin: 0 !important;
    line-height: 1 !important;
}
/* Setiap item radio */
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {
    display: flex !important;
    align-items: center !important;
    padding: 9px 12px !important;
    border-radius: 8px !important;
    border: 1px solid transparent !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    background: transparent !important;
    gap: 0 !important;
}
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover {
    background: rgba(52, 211, 153, 0.08) !important;
    border-color: rgba(52, 211, 153, 0.18) !important;
}
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover div[data-testid="stMarkdownContainer"] p {
    color: #34d399 !important;
}
/* Sembunyikan lingkaran radio asli */
[data-testid="stSidebar"] .stRadio input[type="radio"] {
    display: none !important;
}
[data-testid="stSidebar"] .stRadio span[data-testid="stWidgetLabel"] {
    display: none !important;
}
/* Hilangkan wrapper circle dari BaseWeb */
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] > div:first-child {
    display: none !important;
}
/* Item yang aktif/terpilih */
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:has(input:checked) {
    background: rgba(52, 211, 153, 0.14) !important;
    border-color: rgba(52, 211, 153, 0.35) !important;
}
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:has(input:checked) div[data-testid="stMarkdownContainer"] p {
    color: #34d399 !important;
    font-weight: 600 !important;
}

/* ── Level toggle: radio horizontal pill ── */
.level-radio .stRadio > div[role="radiogroup"] {
    flex-direction: row !important;
    background: rgba(10, 18, 12, 0.6) !important;
    border: 1px solid rgba(52, 211, 153, 0.15) !important;
    border-radius: 8px !important;
    padding: 3px !important;
    gap: 3px !important;
}
.level-radio .stRadio label[data-baseweb="radio"] {
    flex: 1 !important;
    justify-content: center !important;
    padding: 6px 8px !important;
    border-radius: 6px !important;
    font-size: 0.78rem !important;
}
.level-radio .stRadio label[data-baseweb="radio"]:has(input:checked) {
    background: rgba(52, 211, 153, 0.18) !important;
    border-color: transparent !important;
}
.level-radio .stRadio div[data-testid="stMarkdownContainer"] p {
    font-size: 0.78rem !important;
}

/* ── Sidebar misc ── */
.sidebar-label {
    font-size: 0.65rem;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #4a7060;
    padding: 0 4px;
    margin-bottom: 6px;
    margin-top: 16px;
}
.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 2px 12px;
}
.sidebar-logo-icon { font-size: 1.6rem; line-height: 1; }
.sidebar-logo-title {
    font-size: 0.95rem; font-weight: 700; color: #34d399;
    font-family: 'IBM Plex Mono', monospace; letter-spacing: -0.01em;
}
.sidebar-logo-sub { font-size: 0.68rem; color: #4a7060; margin-top: 1px; }
.sidebar-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(52, 211, 153, 0.08); border: 1px solid rgba(52, 211, 153, 0.2);
    border-radius: 6px; padding: 4px 10px;
    font-size: 0.7rem; font-family: 'IBM Plex Mono', monospace; color: #4a9070;
    margin-top: 2px;
}
.badge-dot {
    width: 6px; height: 6px; background: #34d399; border-radius: 50%;
    display: inline-block; box-shadow: 0 0 5px #34d399;
}
.sidebar-footer {
    font-size: 0.68rem; color: #3a5a4a; line-height: 1.55;
    padding: 12px 4px 4px;
    border-top: 1px solid rgba(52, 211, 153, 0.08);
    margin-top: 8px;
}

/* ── KPI Cards ── */
.kpi-card {
    background: rgba(14, 24, 18, 0.7);
    border: 1px solid rgba(16, 185, 129, 0.25);
    border-radius: 12px; padding: 16px 18px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    backdrop-filter: blur(8px);
    height: 100%; box-sizing: border-box;
}
.kpi-card:hover {
    transform: translateY(-3px);
    border-color: rgba(52,211,153,0.5);
    box-shadow: 0 8px 30px rgba(16,185,129,0.2);
}
.kpi-label {
    font-size: 0.68rem; letter-spacing: 0.08em; text-transform: uppercase;
    color: #a7f3d0; font-family: 'IBM Plex Mono', monospace;
    font-weight: 600; margin-bottom: 6px; line-height: 1.3;
}
.kpi-value {
    font-size: clamp(1.4rem, 2.5vw, 2.1rem); font-weight: 700; color: #ffffff;
    font-family: 'IBM Plex Mono', monospace; line-height: 1.1; word-break: break-word;
}
.kpi-sub { font-size: 0.75rem; color: #86efac; margin-top: 5px; line-height: 1.4; }

/* ── Section Title ── */
.section-title {
    font-size: clamp(0.95rem, 1.5vw, 1.2rem); font-weight: 600;
    color: #34d399; margin-top: 8px; margin-bottom: 12px;
    border-left: 4px solid #10b981; padding-left: 10px; line-height: 1.4;
}

/* ── Info Box ── */
.info-box {
    background: rgba(30,41,59,0.25); border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px; padding: 16px 18px; margin-bottom: 16px;
}
.info-title { font-size: 0.9rem; font-weight: 600; color: #81c784; margin-bottom: 8px; }
.info-text { font-size: 0.85rem; color: #e2ede8; line-height: 1.65; }
.info-text ul { margin: 0; padding-left: 1.2rem; }
.info-text li { margin-bottom: 6px; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap: 6px; flex-wrap: wrap; }
.stTabs [data-baseweb="tab"] {
    background-color: rgba(30,41,59,0.2) !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-radius: 6px !important; padding: 7px 14px !important;
    color: #a1b5ad !important; font-size: 0.85rem !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #34d399 !important; background-color: rgba(16,185,129,0.08) !important; }
.stTabs [aria-selected="true"] {
    background-color: rgba(16,185,129,0.2) !important;
    border-color: rgba(52,211,153,0.4) !important;
    color: #34d399 !important; font-weight: 600 !important;
}

/* ── Hero Banner ── */
.hero-banner {
    background: linear-gradient(135deg, rgba(16,185,129,0.08) 0%, rgba(6,95,70,0.18) 100%);
    border: 1px solid rgba(52,211,153,0.2); border-radius: 12px;
    padding: 20px 24px; margin-bottom: 20px;
    box-shadow: 0 8px 32px 0 rgba(0,0,0,0.2); backdrop-filter: blur(4px);
}
.hero-title {
    font-size: clamp(1.2rem, 2.5vw, 1.75rem); font-weight: 700; color: #34d399;
    margin-bottom: 6px; letter-spacing: -0.01em;
}
.hero-subtitle { font-size: clamp(0.78rem, 1.2vw, 0.88rem); color: #a1b5ad; line-height: 1.6; }
.hero-badge {
    display: inline-block; background-color: rgba(52,211,153,0.12);
    border: 1px solid rgba(52,211,153,0.25); color: #34d399;
    padding: 2px 8px; border-radius: 50px; font-size: 0.7rem;
    font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 8px;
}

/* ── Filter container ── */
.filter-container {
    background: rgba(14,24,18,0.5); border: 1px solid rgba(52,211,153,0.1);
    border-radius: 10px; padding: 12px 16px; margin-bottom: 16px;
}

/* ── Misc ── */
hr { border-color: rgba(52,211,153,0.12) !important; margin: 18px 0 !important; }
.js-plotly-plot, .plotly { width: 100% !important; }
iframe { border-radius: 10px !important; border: 1px solid rgba(52,211,153,0.12) !important; }
[data-testid="stDataFrame"] { border-radius: 8px !important; overflow: hidden; }
label[data-testid="stWidgetLabel"] p {
    color: #a7f3d0 !important; font-size: 0.82rem !important; font-weight: 500 !important;
}

/* ── Mobile ── */
@media (max-width: 768px) {
    [data-testid="stMainBlockContainer"] {
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }
    .kpi-value { font-size: 1.3rem !important; }
    .level-radio .stRadio > div[role="radiogroup"] {
        flex-direction: row !important;
    }
}

[data-testid="stSidebar"][aria-expanded="false"] ~ [data-testid="stAppViewBlockContainer"],
[data-testid="stSidebar"][aria-expanded="false"] ~ * [data-testid="stMainBlockContainer"] {
    margin-left: 0 !important;
    width: 100% !important;
}
section[data-testid="stSidebar"][aria-expanded="false"] {
    width: 0 !important;
    min-width: 0 !important;
}

/* ── Fix 2: Nav item full width agar hover konsisten ── */
[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
    width: 100% !important;
}
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {
    width: 100% !important;
    box-sizing: border-box !important;
}


</style>
""", unsafe_allow_html=True)


# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_province_data() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "province_master.csv"))

@st.cache_data
def load_district_data() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "district_master.csv"))

@st.cache_data
def load_cluster_result(level: str) -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, f"cluster_result_{level}.csv"))

@st.cache_data
def load_cluster_summary(level: str) -> pd.DataFrame:
    return pd.read_csv(os.path.join(REPORT_DIR, f"cluster_summary_{level}.csv"))

@st.cache_data
def load_geojson(level: str) -> gpd.GeoDataFrame:
    return gpd.read_file(os.path.join(GEO_DIR, f"{level}.geojson"))


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">🌿</div>
        <div>
            <div class="sidebar-logo-title">ForestWatch</div>
            <div class="sidebar-logo-sub">Sumatera Dashboard</div>
        </div>
    </div>
    <div class="sidebar-badge">
        <span class="badge-dot"></span> GFW · 2001–2025 · LIVE
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:1px;background:rgba(52,211,153,0.1);margin:14px 0 10px;'></div>",
                unsafe_allow_html=True)

    # ── Navigasi (radio native, dikosmetik via CSS) ──
    st.markdown("<div class='sidebar-label'>Menu</div>", unsafe_allow_html=True)

    page = st.radio(
        "Navigasi",
        options=["📊 Ringkasan", "🗺️ Eksplorasi Spasial", "🔵 Analisis Kluster"],
        key="page",
        label_visibility="collapsed",   # sembunyikan label "Navigasi" tapi state tetap ada
    )

    st.markdown("<div style='height:1px;background:rgba(52,211,153,0.1);margin:14px 0 10px;'></div>",
                unsafe_allow_html=True)

    # ── Level Analisis ──
    st.markdown("<div class='sidebar-label'>Level Analisis</div>", unsafe_allow_html=True)

    # Bungkus dengan div ber-class agar CSS pill bisa menarget
    st.markdown("<div class='level-radio'>", unsafe_allow_html=True)
    level_label = st.radio(
        "Level",
        options=["Provinsi", "Kabupaten / Kota"],
        key="level",
        label_visibility="collapsed",
        horizontal=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    level = "province" if level_label == "Provinsi" else "district"

    # Footer
    st.markdown("""
    <div class="sidebar-footer">
        UAS Visualisasi Data Spasial &amp; Temporal<br>
        Sumber: Global Forest Watch (GFW)<br>
        10 Provinsi · 151 Kab/Kota · Sumatera
    </div>
    """, unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
df              = load_province_data() if level == "province" else load_district_data()
cluster_result  = load_cluster_result(level)
cluster_summary = load_cluster_summary(level)
gdf             = load_geojson(level)

region_col = "province" if level == "province" else "district"
years      = sorted(df["year"].unique())


# ── Helper ────────────────────────────────────────────────────────────────────
def kpi(label: str, value: str, sub: str = "") -> str:
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="kpi-card">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'{sub_html}</div>'
    )

def fmt_ha(n: float) -> str:
    if n >= 1_000_000: return f"{n/1_000_000:.2f}M ha"
    if n >= 1_000:     return f"{n/1_000:.1f}K ha"
    return f"{n:.0f} ha"

def fmt_co2(n: float) -> str:
    if n >= 1_000_000_000: return f"{n/1_000_000_000:.2f}B Mg"
    if n >= 1_000_000:     return f"{n/1_000_000:.2f}M Mg"
    return f"{n:.0f} Mg"


# ════════════════════════════════════════════════════════════════════════════
# HALAMAN 1 — RINGKASAN
# ════════════════════════════════════════════════════════════════════════════
if page == "📊 Ringkasan":

    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🌿 FORESTWATCH SUMATERA</div>
        <div class="hero-subtitle">
            Sistem intelijen lingkungan spasio-temporal untuk memantau degradasi hutan dan estimasi
            pelepasan emisi gas rumah kaca di Pulau Sumatera. Mencakup 10 provinsi dan 151 kabupaten/kota
            periode 2001–2025.
        </div>
        <div class="hero-badge">🟢 GFW 2001–2025</div>
    </div>
    """, unsafe_allow_html=True)

    df_prov         = load_province_data()
    total_loss      = df_prov["tree_cover_loss_ha"].sum()
    total_co2       = df_prov["co2_emissions"].sum()
    peak_year       = df_prov.groupby("year")["tree_cover_loss_ha"].sum().idxmax()
    worst_prov      = df_prov.groupby("province")["tree_cover_loss_ha"].sum().idxmax()
    worst_prov_loss = df_prov[df_prov["province"] == worst_prov]["tree_cover_loss_ha"].sum()
    recent_5yr      = df_prov[df_prov["year"] >= 2020]["tree_cover_loss_ha"].sum()
    early_5yr       = df_prov[df_prov["year"].between(2001, 2005)]["tree_cover_loss_ha"].sum()
    change_pct      = ((recent_5yr - early_5yr) / early_5yr) * 100

    c1, c2, c3, c4 = st.columns(4, gap="small")
    with c1:
        st.markdown(kpi("🌳 Loss Hutan Kumulatif", fmt_ha(total_loss), "Total Area Deforestasi"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi("💨 Emisi CO₂ Estimasi", fmt_co2(total_co2), "Pelepasan Gas Rumah Kaca"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi("📈 Tahun Puncak Loss", str(peak_year), "Laju Kehilangan Tertinggi"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi("🚨 Provinsi Terparah", worst_prov, f"Kontributor Terbesar ({fmt_ha(worst_prov_loss)})"), unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

    left_col, right_col = st.columns([6, 4], gap="medium")

    with left_col:
        st.markdown("<div class='section-title'>Tren Kehilangan Tutupan Pohon — Seluruh Sumatera</div>", unsafe_allow_html=True)
        sumatera_trend = df_prov.groupby("year")["tree_cover_loss_ha"].sum().reset_index()
        fig_trend = go.Figure(go.Scatter(
            x=sumatera_trend["year"],
            y=sumatera_trend["tree_cover_loss_ha"],
            mode="lines+markers",
            line=dict(color="#34d399", width=3, shape="spline"),
            marker=dict(size=6, color="#10b981"),
            fill="tozeroy",
            fillcolor="rgba(52,211,153,0.12)",
            name="Loss (ha)",
        ))
        fig_trend.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="Tahun", dtick=2,
                       gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.12)",
                       tickfont=dict(color="#a1b5ad")),
            yaxis=dict(title="Loss (ha)",
                       gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.12)",
                       tickfont=dict(color="#a1b5ad")),
            height=310, margin=dict(t=10, b=40, l=60, r=20), hovermode="x unified",
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with right_col:
        st.markdown("<div class='section-title'>Environmental Analytics Insights</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-box">
            <div class="info-title">💡 Analisis Tren Temporal & Pelepasan Emisi</div>
            <div class="info-text">
                <ul>
                    <li><b>Laju Deforestasi:</b> Sumatera kehilangan total <b>{fmt_ha(total_loss)}</b> tutupan pohon dalam 2001–2025.</li>
                    <li><b>Emisi Karbon:</b> Degradasi ini melepaskan <b>{fmt_co2(total_co2)}</b> ekuivalen CO₂.</li>
                    <li><b>Hotspot:</b> Provinsi <b>{worst_prov}</b> tercatat terparah dengan <b>{fmt_ha(worst_prov_loss)}</b>.</li>
                    <li><b>Tren 5 Tahun:</b> Dibanding 2001–2005, deforestasi 2020–2025 berubah
                        <b style="color:{'#f87171' if change_pct > 0 else '#34d399'}">{change_pct:+.1f}%</b>.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("<div class='section-title'>Matriks Intensitas Deforestasi Provinsi × Tahun (Spasio-Temporal)</div>", unsafe_allow_html=True)
    fig_heatmap = heatmap_province_year(df_prov, metric="tree_cover_loss_ha")
    st.plotly_chart(fig_heatmap, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# HALAMAN 2 — EKSPLORASI SPASIAL
# ════════════════════════════════════════════════════════════════════════════
elif page == "🗺️ Eksplorasi Spasial":

    st.markdown(
        f"<div class='section-title' style='font-size:clamp(1rem,2vw,1.4rem);'>"
        f"Eksplorasi Spasial Wilayah Sumatera ({level_label})</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([3, 3, 4], gap="medium")
    with col_ctrl1:
        selected_year = st.select_slider(
            "Tahun Monitoring", options=years, value=years[-1], key="year_slider"
        )
    with col_ctrl2:
        metric_label = st.selectbox(
            "Pilih Metrik Analisis",
            ["Kehilangan Tutupan Pohon (ha)", "Emisi CO₂ (Mg)"],
            key="metric_sel",
        )
        metric = "tree_cover_loss_ha" if "Pohon" in metric_label else "co2_emissions"
    with col_ctrl3:
        regions = sorted(df[region_col].unique())
        selected_region = st.selectbox(
            "Wilayah Fokus (Tren Detail)", regions, key="region_sel",
            help="Pilih wilayah untuk melihat kurva tren temporal di panel kanan.",
        )
    st.markdown("</div>", unsafe_allow_html=True)

    left_map, right_charts = st.columns([6, 4], gap="medium")

    with left_map:
        st.markdown(
            f"<div class='section-title'>Peta Distribusi Spasial — Tahun {selected_year}</div>",
            unsafe_allow_html=True,
        )
        m = choropleth_loss_year(df, gdf, year=selected_year, level=level, metric=metric)
        st_folium(m, use_container_width=True, height=480, returned_objects=[])

    with right_charts:
        st.markdown(
            f"<div class='section-title'>Karakteristik: {selected_region}</div>",
            unsafe_allow_html=True,
        )
        df_reg_yr = df[(df[region_col] == selected_region) & (df["year"] == selected_year)]
        if not df_reg_yr.empty:
            reg_loss = df_reg_yr["tree_cover_loss_ha"].values[0]
            reg_co2  = df_reg_yr["co2_emissions"].values[0]
            st.markdown(f"""
            <div class="info-box" style="padding:10px 14px;margin-bottom:12px;">
                <div class="info-text">
                    Tahun <b>{selected_year}</b> — <b>{selected_region}</b>:<br>
                    Loss: <b>{fmt_ha(reg_loss)}</b> &nbsp;|&nbsp; Emisi: <b>{fmt_co2(reg_co2)}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

        fig_line = line_trend(df, region=selected_region, level=level, metric=metric)
        st.plotly_chart(fig_line, use_container_width=True)

        fig_scatter = scatter_loss_co2(df, year=selected_year, level=level)
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")

    st.markdown(
        f"<div class='section-title'>Peringkat Degradasi Wilayah Terparah — Tahun {selected_year}</div>",
        unsafe_allow_html=True,
    )
    fig_bar = bar_ranking(df, year=selected_year, level=level, metric=metric)
    st.plotly_chart(fig_bar, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# HALAMAN 3 — ANALISIS KLUSTER
# ════════════════════════════════════════════════════════════════════════════
elif page == "🔵 Analisis Kluster":

    st.markdown(
        f"<div class='section-title' style='font-size:clamp(1rem,2vw,1.4rem);'>"
        f"Analisis Segmentasi Wilayah (K-Means Clustering) — {level_label}</div>",
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div class="info-box">
        <div class="info-title">🔵 Segmentasi Wilayah Berbasis Ciri Spasio-Temporal</div>
        <div class="info-text">
            Pengelompokan menggunakan algoritma <b>K-Means</b> berdasarkan 5 fitur temporal:
            <i>Rata-rata Loss, Puncak Kehilangan, Variabilitas (Std Dev) Laju, Kemiringan (Slope) Tren,
            dan Persentase Deforestasi Terkini (10 tahun terakhir)</i>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    cluster_labels = sorted(cluster_result["cluster_label"].unique())
    all_label      = "Semua Kluster"

    col_f1, col_f2 = st.columns([3, 9], gap="medium")
    with col_f1:
        selected_cluster = st.selectbox(
            "Filter Karakteristik Kluster",
            [all_label] + list(cluster_labels),
            key="cluster_filter",
        )
    with col_f2:
        severity_key = "Semua"
        if selected_cluster != all_label:
            severity_key = selected_cluster.split("–")[0].strip()

        CLUSTER_INTERPRETATIONS = {
            "Tinggi": "⚠️ <b>Bahaya Tingkat Tinggi:</b> Wilayah dengan sejarah kerusakan hutan masif dan laju deforestasi tahunan sangat tinggi. Zona prioritas utama restorasi.",
            "Sedang": "⚖️ <b>Bahaya Tingkat Sedang:</b> Laju kerusakan hutan sedang namun menunjukkan fluktuasi labil atau tren kemiringan yang perlu diawasi.",
            "Rendah": "🌱 <b>Bahaya Tingkat Rendah:</b> Wilayah yang relatif sukses mempertahankan tutupan vegetasi. Fokus konservasi preventif.",
            "Semua":  "🔍 Menampilkan seluruh segmentasi kluster. Pilih kategori kluster pada dropdown untuk melihat interpretasi spasialnya.",
        }
        interpretation = CLUSTER_INTERPRETATIONS.get(severity_key, CLUSTER_INTERPRETATIONS["Semua"])
        st.markdown(f"""
        <div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);
                    border-radius:8px;padding:11px 16px;font-size:0.85rem;color:#e2ede8;line-height:1.6;">
            {interpretation}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

    left_cl, right_cl = st.columns([6, 4], gap="medium")

    with left_cl:
        st.markdown("<div class='section-title'>Peta Spasial Cluster Wilayah</div>", unsafe_allow_html=True)
        m_cluster = choropleth_cluster(cluster_result, gdf, level=level)
        st_folium(m_cluster, use_container_width=True, height=460, returned_objects=[])

    with right_cl:
        st.markdown("<div class='section-title'>Profil Ciri Sentroid Kluster</div>", unsafe_allow_html=True)
        fig_radar = radar_cluster(cluster_summary, level=level)
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

    tab_summary, tab_details = st.tabs([
        "📊 Karakteristik Pusat Kluster",
        "📋 Rincian Wilayah per Kluster",
    ])

    with tab_summary:
        st.markdown("<div style='padding-top:8px;'></div>", unsafe_allow_html=True)
        st.markdown("##### Nilai Pusat Fitur (Rata-rata per Kelompok)")
        numeric_cols = cluster_summary.select_dtypes(include="number").columns
        fmt_dict = {c: "{:,.1f}" for c in numeric_cols}
        if "total_loss"  in fmt_dict: fmt_dict["total_loss"]  = "{:,.0f}"
        if "mean_loss"   in fmt_dict: fmt_dict["mean_loss"]   = "{:,.1f}"
        if "max_loss"    in fmt_dict: fmt_dict["max_loss"]    = "{:,.0f}"
        if "trend_slope" in fmt_dict: fmt_dict["trend_slope"] = "{:+.1f}"
        if "pct_recent"  in fmt_dict: fmt_dict["pct_recent"]  = "{:.1f}%"
        st.dataframe(cluster_summary.style.format(fmt_dict), use_container_width=True, hide_index=True)

    with tab_details:
        st.markdown("<div style='padding-top:8px;'></div>", unsafe_allow_html=True)
        st.markdown(f"##### Daftar Wilayah dalam Kelompok: {selected_cluster}")
        display_cols = [region_col, "cluster_label", "total_loss", "mean_loss", "trend_slope", "pct_recent"]
        display_cols = [c for c in display_cols if c in cluster_result.columns]
        df_display = (
            cluster_result if selected_cluster == all_label
            else cluster_result[cluster_result["cluster_label"] == selected_cluster]
        )
        st.dataframe(
            df_display[display_cols]
                .sort_values("total_loss", ascending=False)
                .reset_index(drop=True)
                .style.format({
                    "total_loss":  "{:,.0f}",
                    "mean_loss":   "{:,.1f}",
                    "trend_slope": "{:+.1f}",
                    "pct_recent":  "{:.1f}%",
                }),
            use_container_width=True,
            hide_index=True,
            height=340,
        )