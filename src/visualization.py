"""
ForestWatch Sumatera — Tahap 6: Visualisasi Spasio-Temporal
============================================================
Modul visualisasi yang dipanggil oleh streamlit_app.py.
Semua fungsi mengembalikan objek Figure (Plotly) atau Map (Folium)
sehingga bisa langsung di-render di Streamlit.

Estetika visual ditingkatkan ke kelas eksekutif/profesional.
"""

import json
import numpy as np
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import folium

# ─────────────────────────────────────────────
# KONSTANTA & ASSET WARNA
# ─────────────────────────────────────────────

CLUSTER_COLORS = {
    0: "#38bdf8",  # Sky Blue
    1: "#f87171",  # Coral Red
    2: "#34d399",  # Emerald Green
    3: "#fb923c",  # Amber Orange
    4: "#c084fc",  # Lavender Purple
    5: "#fbbf24",  # Yellow Gold
    6: "#94a3b8",  # Slate Gray
}

# Helper untuk mengonversi HEX ke RGBA untuk transparansi Plotly/Folium
def hex_to_rgba(hex_str: str, alpha: float = 0.15) -> str:
    hex_str = hex_str.lstrip('#')
    try:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"
    except Exception:
        return f"rgba(148, 163, 184, {alpha})"

# Formatter angka desimal ke satuan hektar (ha)
def format_loss_label(val: float) -> str:
    if val >= 1_000_000:
        return f"{val/1_000_000:.2f}M ha"
    if val >= 1_000:
        return f"{val/1_000:.1f}K ha"
    return f"{val:.0f} ha"

# Formatter angka desimal ke satuan emisi CO2 (Mg)
def format_co2_label(val: float) -> str:
    if val >= 1_000_000_000:
        return f"{val/1_000_000_000:.2f}B Mg"
    if val >= 1_000_000:
        return f"{val/1_000_000:.2f}M Mg"
    if val >= 1_000:
        return f"{val/1_000:.1f}K Mg"
    return f"{val:.0f} Mg"

# ─────────────────────────────────────────────
# LAYOUT & TYPOGRAPHY THEME (PLOTLY)
# ─────────────────────────────────────────────

def _apply_plotly_theme(fig: go.Figure, title: str = "", height: int = 350) -> go.Figure:
    """
    Menerapkan tema visual gelap eksekutif ke objek Plotly Figure.
    FIX: 'titlefont' diganti dengan 'title=dict(font=dict(...))' (deprecated di Plotly ≥ 5.x)
    """
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=14, color="#81c784", family="'IBM Plex Mono', monospace"),
            x=0.0,
            y=0.98,
            xanchor="left",
            yanchor="top"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2ede8", family="'IBM Plex Sans', sans-serif"),
        height=height,
        margin=dict(t=50, b=40, l=50, r=20),
        # FIX: gunakan title=dict(text=..., font=dict(...)) bukan titlefont=dict(...)
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            linecolor="rgba(255,255,255,0.12)",
            tickfont=dict(color="#a1b5ad", size=10),
            title=dict(
                font=dict(color="#a1b5ad", size=11)
            ),
            zeroline=False
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            linecolor="rgba(255,255,255,0.12)",
            tickfont=dict(color="#a1b5ad", size=10),
            title=dict(
                font=dict(color="#a1b5ad", size=11)
            ),
            zeroline=False
        ),
        legend=dict(
            bgcolor="rgba(12, 18, 14, 0.75)",
            bordercolor="rgba(46, 125, 50, 0.2)",
            borderwidth=1,
            font=dict(color="#e2ede8", size=10),
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    return fig


# ═══════════════════════════════════════════════════════
# A. CHOROPLETH — KEHILANGAN TAHUNAN (FOLIUM)
# ═══════════════════════════════════════════════════════

def choropleth_loss_year(
    df: pd.DataFrame,
    gdf: gpd.GeoDataFrame,
    year: int,
    level: str = "province",
    metric: str = "tree_cover_loss_ha",
) -> folium.Map:
    """
    Peta choropleth interaktif dengan visualisasi dark-matter dan data metrik
    terintegrasi langsung dalam tooltip kustom.
    """
    key_col = "province" if level == "province" else "district"
    geo_key = f"feature.properties.{key_col}"

    df_year = df[df["year"] == year].copy()

    # Hitung nilai peta untuk klasifikasi warna
    if metric == "tree_cover_loss_ha":
        df_year["map_value"] = df_year["tree_cover_loss_ha"] / 1_000
        legend_label = f"Kehilangan Tutupan Pohon (ribu ha) — {year}"
        fill_scale = "YlOrRd"
    else:
        df_year["map_value"] = df_year["co2_emissions"] / 1_000_000
        legend_label = f"Emisi CO₂e (juta Mg) — {year}"
        fill_scale = "OrRd"

    # Merge metrik numerik dan versi terformat ke GeoDataFrame
    gdf_merged = gdf.merge(
        df_year[[key_col, "tree_cover_loss_ha", "co2_emissions", "map_value"]],
        on=key_col, how="left"
    )
    gdf_merged["map_value"] = gdf_merged["map_value"].fillna(0)
    gdf_merged["tree_cover_loss_ha"] = gdf_merged["tree_cover_loss_ha"].fillna(0)
    gdf_merged["co2_emissions"] = gdf_merged["co2_emissions"].fillna(0)

    # Tambahkan format human-readable
    gdf_merged["loss_fmt"] = gdf_merged["tree_cover_loss_ha"].apply(format_loss_label)
    gdf_merged["co2_fmt"] = gdf_merged["co2_emissions"].apply(format_co2_label)

    # Konversi GeoDataFrame ke GeoJSON dict
    geo = json.loads(gdf_merged.to_json())

    # Map dengan tiles gelap (executive style)
    m = folium.Map(
        location=[-1.5, 102.5],
        zoom_start=6,
        tiles="CartoDB dark_matter",
        prefer_canvas=True,
    )

    folium.Choropleth(
        geo_data=geo,
        data=df_year,
        columns=[key_col, "map_value"],
        key_on=geo_key,
        fill_color=fill_scale,
        fill_opacity=0.75,
        line_color="#1e293b",
        line_weight=0.6,
        line_opacity=0.3,
        nan_fill_color="#1e293b",
        nan_fill_opacity=0.2,
        legend_name=legend_label,
        highlight=True,
    ).add_to(m)

    # Tooltip kustom dengan visual gelap
    tooltip_fields  = [key_col, "loss_fmt", "co2_fmt"]
    tooltip_aliases = [
        "Provinsi:" if level == "province" else "Kabupaten/Kota:",
        "Loss Hutan:",
        "Emisi CO₂:"
    ]

    folium.GeoJson(
        geo,
        style_function=lambda feat: {
            "fillColor": "transparent",
            "color": "transparent",
            "weight": 0,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            localize=True,
            sticky=True,
            style=(
                "background-color: #0c120e; "
                "color: #e2ede8; "
                "border: 1px solid rgba(46, 125, 50, 0.4); "
                "font-family: 'IBM Plex Sans', sans-serif; "
                "font-size: 13px; "
                "border-radius: 6px; "
                "padding: 10px; "
                "box-shadow: 3px 3px 10px rgba(0,0,0,0.6);"
            )
        ),
    ).add_to(m)

    return m


# ═══════════════════════════════════════════════════════
# B. CHOROPLETH — HASIL CLUSTERING (FOLIUM)
# ═══════════════════════════════════════════════════════

def choropleth_cluster(
    cluster_result: pd.DataFrame,
    gdf: gpd.GeoDataFrame,
    level: str = "province",
) -> folium.Map:
    """
    Peta spasial kluster dengan styling dark-matter, legenda glassmorphic,
    dan tooltip detail hasil pengelompokan.
    """
    key_col = "province" if level == "province" else "district"

    # Gabungkan data kluster ke GeoDataFrame
    gdf_merged = gdf.merge(
        cluster_result[[key_col, "cluster", "cluster_label", "total_loss"]],
        on=key_col, how="left"
    )
    gdf_merged["loss_fmt"] = gdf_merged["total_loss"].apply(format_loss_label)
    gdf_merged["cluster_label"] = gdf_merged["cluster_label"].fillna("Tidak Terklasifikasi (Tanpa Data)")

    geo = json.loads(gdf_merged.to_json())

    m = folium.Map(
        location=[-1.5, 102.5],
        zoom_start=6,
        tiles="CartoDB dark_matter",
        prefer_canvas=True,
    )

    # Dictionary lookup untuk warna wilayah
    lookup = cluster_result.set_index(key_col)[["cluster", "cluster_label"]].to_dict("index")

    def style_fn(feature):
        name  = feature["properties"].get(key_col, "")
        info  = lookup.get(name, {})
        c     = info.get("cluster", -1)
        color = CLUSTER_COLORS.get(c, "#475569")

        border_color  = "#1e293b"
        border_weight = 0.8
        if c == 1:
            border_color  = "rgba(244, 109, 67, 0.4)"
            border_weight = 1.0

        return {
            "fillColor":   color,
            "color":       border_color,
            "weight":      border_weight,
            "fillOpacity": 0.70,
        }

    tooltip_fields  = [key_col, "cluster_label", "loss_fmt"]
    tooltip_aliases = [
        "Provinsi:" if level == "province" else "Kabupaten/Kota:",
        "Karakteristik:",
        "Kumulatif Loss (2001–2024):"
    ]

    folium.GeoJson(
        geo,
        style_function=style_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            sticky=True,
            style=(
                "background-color: #0c120e; "
                "color: #e2ede8; "
                "border: 1px solid rgba(46, 125, 50, 0.4); "
                "font-family: 'IBM Plex Sans', sans-serif; "
                "font-size: 13px; "
                "border-radius: 6px; "
                "padding: 10px; "
                "box-shadow: 3px 3px 10px rgba(0,0,0,0.6);"
            )
        ),
    ).add_to(m)

    # Legenda manual bergaya glassmorphism
    legend_rows = (
        cluster_result[["cluster", "cluster_label"]]
        .drop_duplicates()
        .sort_values("cluster")
    )
    legend_html = (
        "<div style='position:fixed;bottom:35px;left:30px;z-index:1000;"
        "background:rgba(12, 18, 14, 0.85);backdrop-filter:blur(8px);"
        "-webkit-backdrop-filter:blur(8px);border:1px solid rgba(46,125,50,0.35);"
        "padding:12px 16px;border-radius:10px;"
        "box-shadow:5px 5px 15px rgba(0,0,0,0.65);font-family:sans-serif;font-size:12.5px;color:#e2ede8'>"
        "<b style='color:#81c784;font-family:monospace;display:block;margin-bottom:6px;letter-spacing:0.05em'>PROFIL KLUSTER</b>"
    )
    for _, row in legend_rows.iterrows():
        c     = row["cluster"]
        color = CLUSTER_COLORS.get(c, "#94a3b8")
        legend_html += (
            f"<div style='margin: 4px 0; display:flex; align-items:center;'>"
            f"<span style='display:inline-block;width:12px;height:12px;"
            f"background:{color};border-radius:3px;margin-right:8px;box-shadow:0 0 4px {color}'></span>"
            f"<span>Kluster {c}: {row['cluster_label']}</span>"
            f"</div>"
        )
    legend_html += "</div>"
    m.get_root().html.add_child(folium.Element(legend_html))

    return m


# ═══════════════════════════════════════════════════════
# C. LINE CHART — TREN TAHUNAN (PLOTLY)
# ═══════════════════════════════════════════════════════

def line_trend(
    df: pd.DataFrame,
    region: str | list[str],
    level: str = "province",
    metric: str = "tree_cover_loss_ha",
) -> go.Figure:
    """
    Garis tren tahunan interaktif — area chart halus dengan gradien bersinar.
    FIX: titlefont → title=dict(font=dict(...)) via _apply_plotly_theme
    """
    key_col = "province" if level == "province" else "district"
    ylabel  = "Tree Cover Loss (ha)" if metric == "tree_cover_loss_ha" else "Emisi CO₂ (Mg CO₂e)"

    selected = [region] if isinstance(region, str) else list(region)

    title = (
        f"Tren {ylabel} — "
        f"{', '.join(selected[:2])}{'...' if len(selected) > 2 else ''}"
    )

    filtered = df[df[key_col].isin(selected)].copy()

    fig = px.line(
        filtered,
        x="year",
        y=metric,
        color=key_col,
        line_shape="spline",
        markers=True,
        labels={"year": "Tahun", metric: ylabel, key_col: key_col.capitalize()},
        template=None
    )

    primary_color = "#34d399" if metric == "tree_cover_loss_ha" else "#f87171"

    fig.update_traces(line_width=2.5, marker=dict(size=6, symbol="circle"))

    if len(selected) == 1:
        rgba_fill = hex_to_rgba(primary_color, 0.15)
        fig.update_traces(
            line=dict(color=primary_color),
            fill="tozeroy",
            fillcolor=rgba_fill
        )

    fig = _apply_plotly_theme(fig, title=title, height=265)
    fig.update_layout(
        hovermode="x unified",
        xaxis=dict(tickmode="linear", dtick=4)
    )

    return fig


# ═══════════════════════════════════════════════════════
# D. BAR CHART — RANKING WILAYAH (PLOTLY)
# ═══════════════════════════════════════════════════════

def bar_ranking(
    df: pd.DataFrame,
    year: int | None = None,
    level: str = "province",
    top_n: int = 15,
    metric: str = "tree_cover_loss_ha",
) -> go.Figure:
    """
    Bar chart horizontal ranking wilayah.
    FIX: titlefont → title=dict(font=dict(...)) via _apply_plotly_theme
    """
    key_col = "province" if level == "province" else "district"
    ylabel  = "Tree Cover Loss (ha)" if metric == "tree_cover_loss_ha" else "Emisi CO₂ (Mg CO₂e)"

    if year is None:
        agg   = df.groupby(key_col)[metric].sum().reset_index()
        title = f"Top {top_n} {key_col.capitalize()} — Total {ylabel} (2001–2024)"
    else:
        agg   = df[df["year"] == year].groupby(key_col)[metric].sum().reset_index()
        title = f"Top {top_n} {key_col.capitalize()} — {ylabel} ({year})"

    agg = agg.nlargest(top_n, metric).sort_values(metric)

    if metric == "tree_cover_loss_ha":
        agg["text_val"] = agg[metric].apply(format_loss_label)
        color_scale = "Greens"
    else:
        agg["text_val"] = agg[metric].apply(format_co2_label)
        color_scale = "Reds"

    fig = px.bar(
        agg,
        x=metric,
        y=key_col,
        orientation="h",
        labels={metric: ylabel, key_col: ""},
        color=metric,
        color_continuous_scale=color_scale,
        text="text_val",
        template=None,
    )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
        marker=dict(line=dict(width=0))
    )

    fig = _apply_plotly_theme(fig, title=title, height=380)
    fig.update_layout(
        coloraxis_showscale=False,
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
    )
    return fig


# ═══════════════════════════════════════════════════════
# E. HEATMAP — PROVINSI × TAHUN (PLOTLY)
# ═══════════════════════════════════════════════════════

def heatmap_province_year(
    prov_df: pd.DataFrame,
    metric: str = "tree_cover_loss_ha",
) -> go.Figure:
    """
    Heatmap interaktif provinsi × tahun dengan styling gelap.
    FIX: titlefont → title=dict(font=dict(...)) via _apply_plotly_theme
    """
    pivot = prov_df.pivot_table(
        index="province", columns="year", values=metric, aggfunc="sum"
    )
    ylabel      = "Tree Cover Loss (ha)" if metric == "tree_cover_loss_ha" else "Emisi CO₂ (Mg CO₂e)"
    color_scale = "Greens" if metric == "tree_cover_loss_ha" else "Reds"

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[str(y) for y in pivot.columns],
        y=pivot.index.tolist(),
        colorscale=color_scale,
        colorbar=dict(
            title=dict(
                text=ylabel,
                font=dict(size=10, color="#a1b5ad")   # FIX: title dict, bukan titlefont
            ),
            tickfont=dict(color="#a1b5ad", size=9),
            thickness=15
        ),
        hovertemplate="Provinsi: %{y}<br>Tahun: %{x}<br>Nilai: %{z:,.0f}<extra></extra>",
    ))

    title = f"Heatmap: {ylabel} — Provinsi × Tahun"
    fig   = _apply_plotly_theme(fig, title=title, height=380)
    fig.update_layout(
        xaxis_title="Tahun",
        yaxis_title="",
        xaxis=dict(tickangle=-45, gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    return fig


# ═══════════════════════════════════════════════════════
# F. SCATTER — LOSS VS CO₂ (PLOTLY)
# ═══════════════════════════════════════════════════════

def scatter_loss_co2(
    df: pd.DataFrame,
    level: str = "province",
    year: int | None = None,
) -> go.Figure:
    """
    Scatter plot korelasi tree_cover_loss_ha vs co2_emissions dengan garis tren OLS.
    FIX: titlefont → title=dict(font=dict(...)) via _apply_plotly_theme
    """
    key_col = "province" if level == "province" else "district"
    subset  = df if year is None else df[df["year"] == year]
    agg     = subset.groupby(key_col)[["tree_cover_loss_ha", "co2_emissions"]].sum().reset_index()
    period  = "2001–2024" if year is None else str(year)

    fig = px.scatter(
        agg,
        x="tree_cover_loss_ha",
        y="co2_emissions",
        text=key_col,
        labels={
            "tree_cover_loss_ha": "Tree Cover Loss (ha)",
            "co2_emissions":      "Emisi CO₂ (Mg CO₂e)",
        },
        trendline="ols",
        trendline_color_override="#ef4444",
        template=None,
    )

    fig.update_traces(
        textposition="top center",
        marker=dict(
            size=11,
            color="#10b981",
            opacity=0.85,
            line=dict(width=1.2, color="#0c120e")
        ),
        selector=dict(mode="markers+text"),
    )

    fig.update_traces(
        line=dict(dash="dash", width=2),
        selector=dict(type="scatter", mode="lines")
    )

    title = f"Korelasi: Loss vs Emisi CO₂ — {period}"
    fig   = _apply_plotly_theme(fig, title=title, height=280)
    fig.update_layout(showlegend=False)

    return fig


# ═══════════════════════════════════════════════════════
# G. RADAR — PROFIL KLUSTER (PLOTLY)
# ═══════════════════════════════════════════════════════

def radar_cluster(
    cluster_summary_df: pd.DataFrame,
    level: str | None = None,
) -> go.Figure:
    """
    Radar chart interaktif profil kluster.
    FIX: titlefont → title=dict(font=dict(...)) di update_layout langsung.
    """
    feat_cols = ["total_loss", "mean_loss", "max_loss", "std_loss", "trend_slope", "pct_recent"]

    clean_labels = [
        "Total Loss",
        "Rerata Loss",
        "Puncak Loss",
        "Variabilitas",
        "Kemiringan Tren",
        "Loss Terkini (%)"
    ]

    missing = [c for c in feat_cols if c not in cluster_summary_df.columns]
    if missing:
        raise ValueError(f"radar_cluster: kolom berikut tidak ditemukan: {missing}")

    # Normalisasi 0–1 per fitur
    norm = cluster_summary_df[feat_cols].copy()
    for col in feat_cols:
        mn, mx = norm[col].min(), norm[col].max()
        norm[col] = (norm[col] - mn) / (mx - mn + 1e-9)

    label_col = "label" if "label" in cluster_summary_df.columns else "cluster_label"

    fig = go.Figure()
    for i, row in cluster_summary_df.iterrows():
        values = norm.loc[i, feat_cols].tolist()
        values += values[:1]
        c      = row.get("cluster", i)
        color  = CLUSTER_COLORS.get(int(c), "#94a3b8")
        lbl    = row.get(label_col, f"Kluster {c}")

        rgba_fill = hex_to_rgba(color, 0.12)

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=clean_labels + [clean_labels[0]],
            fill="toself",
            fillcolor=rgba_fill,
            line=dict(color=color, width=2.5),
            name=f"Kluster {c}: {lbl}",
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                gridcolor="rgba(255,255,255,0.06)",
                linecolor="rgba(255,255,255,0.12)",
                tickfont=dict(color="#a1b5ad", size=9)
            ),
            angularaxis=dict(
                gridcolor="rgba(255,255,255,0.06)",
                linecolor="rgba(255,255,255,0.12)",
                tickfont=dict(color="#e2ede8", size=10, family="'IBM Plex Sans'")
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2ede8", family="'IBM Plex Sans', sans-serif"),
        title=dict(
            text="Profil Fitur per Kluster (Skala 0–1)",
            font=dict(size=14, color="#81c784", family="'IBM Plex Mono', monospace")
        ),
        height=380,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            x=0.5,
            xanchor="center",
            bgcolor="rgba(12, 18, 14, 0.7)",
            bordercolor="rgba(46, 125, 50, 0.2)",
            borderwidth=1,
            font=dict(size=9.5)
        ),
    )
    return fig