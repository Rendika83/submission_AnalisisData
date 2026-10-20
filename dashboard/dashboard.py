import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from pathlib import Path

sns.set_theme(style="whitegrid")
st.set_page_config(page_title="E-Commerce Analytics Dashboard", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    csv_path = Path(__file__).parent / "main_data.csv"
    df = pd.read_csv(csv_path)
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    return df

all_df = load_data()

# Sidebar Filter Rentang Tanggal
min_date = all_df["order_purchase_timestamp"].min().date()
max_date = all_df["order_purchase_timestamp"].max().date()

with st.sidebar:
    st.title("🛒 E-Commerce Dashboard")
    st.markdown("Gunakan filter di bawah ini untuk menyesuaikan rentang waktu analisis:")
    date_range = st.date_input(
        label="Rentang Waktu Transaksi",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date)
    )

# Validasi input rentang tanggal agar tidak error saat user baru memilih 1 tanggal
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = date_range[0] if isinstance(date_range, tuple) else date_range
    end_date = start_date

main_df = all_df[
    (all_df["order_purchase_timestamp"].dt.date >= start_date) &
    (all_df["order_purchase_timestamp"].dt.date <= end_date)
].copy()

st.title("📊 E-Commerce Public Dataset Analytics Dashboard")
st.caption(f"Menampilkan data transaksi delivered periode **{start_date}** hingga **{end_date}**")

if main_df.empty:
    st.warning("Tidak ada data transaksi pada rentang tanggal yang dipilih. Silakan pilih rentang tanggal lain.")
    st.stop()

# Ringkasan Metrik Utama (KPI)
order_lvl = main_df.drop_duplicates(subset=["order_id"])
total_orders = order_lvl["order_id"].nunique()
total_revenue = main_df["price"].sum()
delay_rate = (order_lvl["is_delayed"].sum() / len(order_lvl) * 100) if len(order_lvl) > 0 else 0.0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Orders (Delivered)", f"{total_orders:,}")
with col2:
    st.metric("Total Revenue (BRL)", f"R$ {total_revenue:,.2f}")
with col3:
    st.metric("Delivery Delay Rate", f"{delay_rate:.2f}%")

st.markdown("---")

# Visualisasi 1: Top 10 & Bottom 10 Kategori Produk berdasarkan Revenue
st.subheader("1. Performa Pendapatan (Revenue) Kategori Produk (Top 10 vs Bottom 10)")

cat_rev = (
    main_df.groupby("product_category_name_english", as_index=False)["price"]
    .sum()
    .sort_values(by="price", ascending=False)
)

top10_cat = cat_rev.head(10)
bottom10_cat = cat_rev.tail(10).sort_values(by="price", ascending=True)

fig1, ax1 = plt.subplots(nrows=1, ncols=2, figsize=(18, 6))

palette_top = ["#1f77b4"] + ["#d3d3d3"] * max(0, len(top10_cat) - 1)
sns.barplot(
    x="price",
    y="product_category_name_english",
    hue="product_category_name_english",
    data=top10_cat,
    palette=palette_top,
    legend=False,
    ax=ax1[0]
)
ax1[0].set_title("10 Kategori dengan Revenue Tertinggi", fontsize=13, fontweight="bold")
ax1[0].set_xlabel("Total Revenue (BRL)")
ax1[0].set_ylabel(None)

palette_bottom = ["#d62728"] + ["#d3d3d3"] * max(0, len(bottom10_cat) - 1)
sns.barplot(
    x="price",
    y="product_category_name_english",
    hue="product_category_name_english",
    data=bottom10_cat,
    palette=palette_bottom,
    legend=False,
    ax=ax1[1]
)
ax1[1].set_title("10 Kategori dengan Revenue Terendah", fontsize=13, fontweight="bold")
ax1[1].set_xlabel("Total Revenue (BRL)")
ax1[1].set_ylabel(None)
ax1[1].invert_xaxis()
ax1[1].yaxis.set_label_position("right")
ax1[1].yaxis.tick_right()

plt.tight_layout()
st.pyplot(fig1)

st.markdown("---")

# Visualisasi 2: Tingkat Keterlambatan Pengiriman di 10 Negara Bagian Terbesar
st.subheader("2. Persentase Keterlambatan Pengiriman di 10 Negara Bagian dengan Pesanan Terbanyak")

state_df = order_lvl.groupby("customer_state", as_index=False).agg(
    total_orders=("order_id", "nunique"),
    delayed_orders=("is_delayed", "sum")
)
state_df["delay_rate_pct"] = (state_df["delayed_orders"] / state_df["total_orders"]) * 100
top10_state = (
    state_df.sort_values(by="total_orders", ascending=False)
    .head(10)
    .sort_values(by="delay_rate_pct", ascending=False)
)

fig2, ax2 = plt.subplots(figsize=(12, 5))
palette_delay = ["#d62728"] + ["#d3d3d3"] * max(0, len(top10_state) - 1)
sns.barplot(
    x="delay_rate_pct",
    y="customer_state",
    hue="customer_state",
    data=top10_state,
    palette=palette_delay,
    legend=False,
    ax=ax2
)
for container in ax2.containers:
    ax2.bar_label(container, fmt="%.2f%%", padding=4, fontsize=10)
ax2.set_xlim(0, max(top10_state["delay_rate_pct"].max() * 1.15, 1))
ax2.set_title("Persentase Pesanan Terlambat per Negara Bagian (%)", fontsize=13, fontweight="bold")
ax2.set_xlabel("Persentase Keterlambatan (%)")
ax2.set_ylabel("Negara Bagian (State)")
plt.tight_layout()
st.pyplot(fig2)

st.markdown("---")

# Visualisasi 3: Analisis Lanjutan RFM & Segmentasi Pelanggan
st.subheader("3. Analisis Lanjutan: RFM Parameters & Customer Segmentation")

ref_date = main_df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
rfm = main_df.groupby("customer_unique_id", as_index=False).agg(
    last_purchase=("order_purchase_timestamp", "max"),
    frequency=("order_id", "nunique"),
    monetary=("price", "sum")
)
rfm["recency"] = (ref_date - rfm["last_purchase"]).dt.days

# Tampilkan Metrik Rata-rata RFM
r_col, f_col, m_col = st.columns(3)
with r_col:
    st.metric("Average Recency (Days)", f"{rfm['recency'].mean():.1f} Hari")
with f_col:
    st.metric("Average Frequency", f"{rfm['frequency'].mean():.2f} Pesanan")
with m_col:
    st.metric("Average Monetary (BRL)", f"R$ {rfm['monetary'].mean():,.2f}")

def segment_customer(row):
    if row["recency"] <= 90 and row["monetary"] >= 150:
        return "High-Value Active"
    elif row["recency"] <= 180:
        return "Regular Active"
    elif row["recency"] <= 365:
        return "At-Risk (Perlu Re-engagement)"
    else:
        return "Churned / Inactive"

rfm["segment"] = rfm.apply(segment_customer, axis=1)
seg_counts = rfm["segment"].value_counts().reset_index()
seg_counts.columns = ["segment", "count"]

fig3, ax3 = plt.subplots(figsize=(12, 4.5))
palette_seg = ["#1f77b4"] + ["#d3d3d3"] * max(0, len(seg_counts) - 1)
sns.barplot(
    x="count",
    y="segment",
    hue="segment",
    data=seg_counts,
    palette=palette_seg,
    legend=False,
    ax=ax3
)
for container in ax3.containers:
    ax3.bar_label(container, fmt="%d", padding=4, fontsize=10)
ax3.set_xlim(0, max(seg_counts["count"].max() * 1.15, 1))
ax3.set_title("Distribusi Segmen Pelanggan Berdasarkan RFM Manual Grouping", fontsize=13, fontweight="bold")
ax3.set_xlabel("Jumlah Pelanggan Unik")
ax3.set_ylabel("Segmen Pelanggan")
plt.tight_layout()
st.pyplot(fig3)

st.caption("Copyright © 2026 - E-Commerce Data Analysis Dashboard")