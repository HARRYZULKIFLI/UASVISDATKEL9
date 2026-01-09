import streamlit as st
import pandas as pd
import plotly.express as px

# ===============================
# PAGE CONFIG + STYLE
# ===============================
st.set_page_config(page_title="Dashboard Stunting", page_icon="📊", layout="wide")
st.markdown("""
<style>
/* --- clean + aesthetic --- */
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
[data-testid="stSidebar"] {border-right: 1px solid rgba(255,255,255,0.08);}
h1,h2,h3 {letter-spacing: -0.3px;}
.small-muted {opacity: .72; font-size: 0.9rem;}
.kpi-card {padding: 14px 16px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.03);}
.kpi-title {font-size: 0.85rem; opacity: .72; margin-bottom: 6px;}
.kpi-value {font-size: 1.5rem; font-weight: 700; line-height: 1.15;}
.kpi-sub {font-size: 0.85rem; opacity: .72; margin-top: 6px;}
hr {opacity: .15;}
</style>
""", unsafe_allow_html=True)

# Plotly template (biar konsisten & cakep)
try:
    import plotly.io as pio
    pio.templates.default = "plotly_dark"
except Exception:
    pass

# ===============================
# LOAD DATA
# ===============================
@st.cache_data
def load_data():
    df = pd.read_csv("data_stunting.csv")
    # rapihin kolom string
    for c in ["nama_provinsi", "nama_kabupaten_kota"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    return df

df = load_data()

# ===============================
# HEADER
# ===============================
left, right = st.columns([0.72, 0.28])
with left:
    st.title("📊 Dashboard Prevalensi Balita Stunting")
    st.markdown('<div class="small-muted">Visualisasi interaktif berbasis data CSV (kabupaten/kota, provinsi, tahun).</div>', unsafe_allow_html=True)
with right:
    st.markdown('<div class="kpi-card"><div class="kpi-title">Dataset</div>'
                f'<div class="kpi-value">{len(df):,} baris</div>'
                f'<div class="kpi-sub">Kolom: {df.shape[1]}</div></div>', unsafe_allow_html=True)

st.divider()

# ===============================
# SIDEBAR FILTER
# ===============================
st.sidebar.header("🎛️ Filter & Tampilan")

# Tahun (support "Semua tahun")
tahun_list = sorted(df["tahun"].unique()) if "tahun" in df.columns else []
tahun_opsi = ["Semua tahun"] + tahun_list
tahun_pilihan = st.sidebar.selectbox("Pilih Tahun", tahun_opsi, index=0 if len(tahun_opsi) else 0)

# Provinsi (support "Semua provinsi")
prov_list = sorted(df["nama_provinsi"].unique()) if "nama_provinsi" in df.columns else []
prov_opsi = ["Semua provinsi"] + prov_list
prov_pilihan = st.sidebar.selectbox("Pilih Provinsi", prov_opsi, index=0 if len(prov_opsi) else 0)

# Filter dasar
df_filtered = df.copy()
if tahun_pilihan != "Semua tahun" and "tahun" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["tahun"] == tahun_pilihan]
if prov_pilihan != "Semua provinsi" and "nama_provinsi" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["nama_provinsi"] == prov_pilihan]

# Kab/Kota (mengikuti filter di atas)
kota_opsi = ["Semua kabupaten/kota"]
if "nama_kabupaten_kota" in df_filtered.columns and len(df_filtered) > 0:
    kota_opsi += sorted(df_filtered["nama_kabupaten_kota"].unique())
kota_pilihan = st.sidebar.selectbox("Pilih Kabupaten/Kota", kota_opsi, index=0)

if kota_pilihan != "Semua kabupaten/kota" and "nama_kabupaten_kota" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["nama_kabupaten_kota"] == kota_pilihan]

st.sidebar.divider()

# Controls untuk ranking
mode_rank = st.sidebar.radio("Mode Ranking", ["Top", "Bottom"], horizontal=True)
n_rank_max = max(5, min(50, len(df_filtered) if len(df_filtered) else 5))
n_rank = st.sidebar.slider("Jumlah ditampilkan", 5, n_rank_max, min(10, n_rank_max))

# Controls untuk bins histogram
bins = st.sidebar.slider("Bins Histogram", 5, 30, 12)

# ===============================
# KPI SECTION
# ===============================
if len(df_filtered) == 0:
    st.warning("Tidak ada data yang cocok dengan filter. Coba ubah tahun/provinsi/kabupaten.")
    st.stop()

metric_cols = st.columns(4)
val_col = "prevalensi_balita_stunting"

avg_all = df[val_col].mean() if val_col in df.columns else None
avg_f = df_filtered[val_col].mean()
mx = df_filtered[val_col].max()
mn = df_filtered[val_col].min()

label_scope = "Rata-rata Terfilter"
if kota_pilihan != "Semua kabupaten/kota":
    label_scope = kota_pilihan
elif prov_pilihan != "Semua provinsi":
    label_scope = f"Provinsi {prov_pilihan}"
elif tahun_pilihan != "Semua tahun":
    label_scope = f"Tahun {tahun_pilihan}"

def kpi(card_col, title, value, sub=""):
    with card_col:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-title">{title}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

kpi(metric_cols[0], "Rata-rata Nasional", f"{avg_all:.2f}" if avg_all is not None else "-", "Semua data")
kpi(metric_cols[1], "Rata-rata Filter", f"{avg_f:.2f}", label_scope)
kpi(metric_cols[2], "Tertinggi (Filter)", f"{mx:.2f}", "Max prevalensi")
kpi(metric_cols[3], "Terendah (Filter)", f"{mn:.2f}", "Min prevalensi")

st.divider()

# ===============================
# TABS
# ===============================
tab1, tab2, tab3 = st.tabs(["📈 Insight Utama", "🏆 Ranking", "📋 Data Detail"])

# -------------------------------
# TAB 1: INSIGHT UTAMA
# -------------------------------
with tab1:
    c1, c2 = st.columns([0.58, 0.42], gap="large")

    # Histogram
    with c1:
        st.subheader("Distribusi Prevalensi (Histogram)")
        fig_hist = px.histogram(
            df_filtered,
            x=val_col,
            nbins=bins,
            labels={val_col: "Prevalensi"},
            title=None
        )
        fig_hist.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=380)
        st.plotly_chart(fig_hist, use_container_width=True)

    # Box Plot
    with c2:
        st.subheader("Sebaran & Outlier (Box Plot)")
        fig_box = px.box(
            df_filtered,
            y=val_col,
            points="all",
            labels={val_col: "Prevalensi"},
            title=None
        )
        fig_box.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=380)
        st.plotly_chart(fig_box, use_container_width=True)

    st.divider()

    # Tren (kalau data multi tahun tersedia)
    st.subheader("Tren (Jika Ada Lebih dari 1 Tahun)")
    if "tahun" in df.columns and df["tahun"].nunique() > 1:
        trend_base = df.copy()
        if prov_pilihan != "Semua provinsi":
            trend_base = trend_base[trend_base["nama_provinsi"] == prov_pilihan]
        trend = trend_base.groupby("tahun", as_index=False)[val_col].mean()
        fig_trend = px.line(trend, x="tahun", y=val_col, markers=True, labels={"tahun":"Tahun", val_col:"Rata-rata Prevalensi"})
        fig_trend.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=360)
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Dataset kamu saat ini cuma punya 1 tahun, jadi grafik tren belum bisa. Kalau ditambah tahun lain (mis. 2021–2023), tab ini otomatis jadi hidup.")

# -------------------------------
# TAB 2: RANKING
# -------------------------------
with tab2:
    st.subheader("Ranking Kabupaten/Kota")
    rank_df = df_filtered.copy()
    asc = True if mode_rank == "Bottom" else False
    rank_df = rank_df.sort_values(val_col, ascending=asc).head(n_rank)

    fig_rank = px.bar(
        rank_df,
        x=val_col,
        y="nama_kabupaten_kota",
        orientation="h",
        labels={val_col: "Prevalensi", "nama_kabupaten_kota": "Kabupaten/Kota"},
        title=None
    )
    fig_rank.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        height=max(420, 26 * len(rank_df) + 160),
        yaxis=dict(autorange="reversed")
    )
    st.plotly_chart(fig_rank, use_container_width=True)

    st.divider()

    st.subheader("Scatter: Prevalensi vs Kode (Quick View)")
    if "kode_kabupaten_kota" in df_filtered.columns:
        fig_scatter = px.scatter(
            df_filtered,
            x="kode_kabupaten_kota",
            y=val_col,
            hover_name="nama_kabupaten_kota",
            labels={"kode_kabupaten_kota":"Kode Kab/Kota", val_col:"Prevalensi"},
            title=None
        )
        fig_scatter.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=360)
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Kolom kode_kabupaten_kota tidak ditemukan di dataset.")

# -------------------------------
# TAB 3: DATA DETAIL
# -------------------------------
with tab3:
    st.subheader("Tabel Data Sesuai Filter")
    show_cols = [c for c in ["nama_provinsi","nama_kabupaten_kota",val_col,"satuan","tahun","kode_kabupaten_kota","kode_provinsi"] if c in df.columns]
    st.dataframe(df_filtered[show_cols].reset_index(drop=True), use_container_width=True)

    st.divider()
    st.subheader("Download Data Terfilter")
    st.download_button(
        "⬇️ Download CSV (filtered)",
        data=df_filtered.to_csv(index=False).encode("utf-8"),
        file_name="data_stunting_filtered.csv",
        mime="text/csv"
    )

# ===============================
# FOOTER
# ===============================
st.markdown("<div class='small-muted'>Made with Streamlit + Plotly • Tips: tambah data multi-tahun / multi-provinsi biar insight makin kaya.</div>", unsafe_allow_html=True)
