import streamlit as st
import pandas as pd
import plotly.express as px

# ===============================
# 1. LOAD DATA
# ===============================
@st.cache_data
def load_data():
    df = pd.read_csv("data_stunting.csv")
    return df

df = load_data()

# ===============================
# 2. JUDUL
# ===============================
st.title("Visualisasi Prevalensi Balita Stunting di Indonesia")

# ===============================
# 3. FILTER
# ===============================
st.sidebar.header("Filter Data")

# Tahun
tahun_list = sorted(df["tahun"].unique())
tahun_pilihan = st.sidebar.selectbox("Pilih Tahun", tahun_list)

# Provinsi
provinsi_list = ["Semua provinsi"] + sorted(df["nama_provinsi"].unique())
provinsi_pilihan = st.sidebar.selectbox("Pilih Provinsi", provinsi_list)

# Filter berdasarkan tahun
df_filtered = df[df["tahun"] == tahun_pilihan]

# Filter provinsi
if provinsi_pilihan != "Semua provinsi":
    df_filtered = df_filtered[df_filtered["nama_provinsi"] == provinsi_pilihan]

# Kabupaten / Kota
kota_list = ["Semua kabupaten/kota"] + sorted(df_filtered["nama_kabupaten_kota"].unique())
kota_pilihan = st.sidebar.selectbox("Pilih Kabupaten/Kota", kota_list)

if kota_pilihan != "Semua kabupaten/kota":
    df_filtered = df_filtered[df_filtered["nama_kabupaten_kota"] == kota_pilihan]

# ===============================
# 4. METRIC (TANPA PERSEN)
# ===============================
mean_nasional = df[df["tahun"] == tahun_pilihan]["prevalensi_balita_stunting"].mean()
mean_filtered = df_filtered["prevalensi_balita_stunting"].mean()

label_filter = "Rata-rata Data Terfilter"
if kota_pilihan != "Semua kabupaten/kota":
    label_filter = kota_pilihan
elif provinsi_pilihan != "Semua provinsi":
    label_filter = f"Provinsi {provinsi_pilihan}"

st.divider()

# ===============================
# 5. GRAFIK PER PROVINSI
# ===============================
st.subheader("Rata-rata Prevalensi Stunting per Provinsi")

df_tahun = df[df["tahun"] == tahun_pilihan]
prov_group = (
    df_tahun.groupby("nama_provinsi", as_index=False)["prevalensi_balita_stunting"]
    .mean()
    .rename(columns={"prevalensi_balita_stunting": "rata_rata"})
    .sort_values("rata_rata", ascending=False)
)

fig_prov = px.bar(
    prov_group,
    x="nama_provinsi",
    y="rata_rata",
    title=f"Rata-rata Stunting per Provinsi ({tahun_pilihan})",
    labels={"nama_provinsi": "Provinsi", "rata_rata": "Prevalensi"},
)
fig_prov.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_prov, width="stretch")

st.divider()

# ===============================
# 6. GRAFIK SEMUA KAB/KOTA (TANPA TOP 10)
# ===============================
st.subheader("Prevalensi Stunting Semua Kabupaten/Kota")

if len(df_filtered) > 0:

    df_sorted = df_filtered.sort_values("prevalensi_balita_stunting", ascending=False)

    fig_all = px.bar(
        df_sorted,
        x="prevalensi_balita_stunting",
        y="nama_kabupaten_kota",
        orientation="h",
        labels={
            "prevalensi_balita_stunting": "Prevalensi",
            "nama_kabupaten_kota": "Kabupaten/Kota",
        },
        title="Prevalensi Stunting Seluruh Kabupaten/Kota",
    )
    fig_all.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_all, width="stretch")

else:
    st.info("Tidak ada data yang cocok dengan filter.")

st.divider()

# ===============================
# 7. TABEL DATA
# ===============================
st.subheader("Data Detail Sesuai Filter")

if len(df_filtered) > 0:
    st.dataframe(
        df_filtered[
            [
                "nama_provinsi",
                "nama_kabupaten_kota",
                "prevalensi_balita_stunting",
                "satuan",
                "tahun"
            ]
        ].reset_index(drop=True)
    )
else:
    st.write("Tidak ada data yang cocok dengan filter.")
