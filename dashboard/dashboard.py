import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from pathlib import Path

sns.set(style="whitegrid")
st.set_page_config(page_title="E-Commerce Analytics Dashboard", layout="wide")

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
    st.markdown("Filter rentang waktu transaksi:")
    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[
    (all_df["order_purchase_timestamp"].dt.date >= start_date) &
    (all_df["order_purchase_timestamp"].dt.date <= end_date)
]

st.title("📊 E-Commerce Public Dataset Dashboard")

# Ringkasan Metrik Utama
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Orders", f"{main_df['order_id'].nunique():,}")
with col2:
    st.metric("Total Revenue (BRL)", f"R$ {main_df['price'].sum():,.2f}")
with col3:
    order_lvl = main_df.drop_duplicates(subset=["order_id"])
    delay_rate = (order_lvl["is_delayed"].sum() / len(order_lvl) * 100) if len(order_lvl) > 0 else 0
    st.metric("Delivery Delay Rate", f"{delay_rate:.2f}%")

st.markdown("---")

# Visualisasi 1: Top & Bottom Kategori Produk
st.subheader("1. Performa Revenue Kategori Produk (Top 10 vs Bottom 10)")
cat_rev = main_df.groupby("product_category_name_english")["price"].sum().reset_index()
cat_rev = cat_rev.sort_values(by="price", ascending=False)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(18, 6))
sns.barplot(x="price", y="product_category_name_english", data=cat_rev.head(10),
            palette=["#1f77b4"] + ["#d3d3d3"]*9, ax=ax[0])
ax[0].set_title("10 Kategori dengan Revenue Tertinggi")
ax[0].set_xlabel("Total Revenue (BRL)")
ax[0].set_ylabel(None)

sns.barplot(x="price", y="product_category_name_english", data=cat_rev.tail(10).sort_values(by="price", ascending=True),
            palette=["#d62728"] + ["#d3d3d3"]*9, ax=ax[1])
ax[1].set_title("10 Kategori dengan Revenue Terendah")
ax[1].set_xlabel("Total Revenue (BRL)")
ax[1].set_ylabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.tick_right()
st.pyplot(fig)

# Visualisasi 2: Keterlambatan Pengiriman per Negara Bagian
st.subheader("2. Persentase Keterlambatan Pengiriman di 10 Negara Bagian Terbesar")
state_df = order_lvl.groupby("customer_state").agg(
    total_orders=("order_id", "nunique"),
    delayed_orders=("is_delayed", "sum")
).reset_index()
state_df["delay_rate_pct"] = (state_df["delayed_orders"] / state_df["total_orders"]) * 100
top10_state = state_df.sort_values(by="total_orders", ascending=False).head(10).sort_values(by="delay_rate_pct", ascending=False)

fig2, ax2 = plt.subplots(figsize=(10, 5))
colors_delay = ["#d62728" if i == 0 else "#d3d3d3" for i in range(len(top10_state))]
sns.barplot(x="delay_rate_pct", y="customer_state", data=top10_state, palette=colors_delay, ax=ax2)
ax2.set_xlabel("Persentase Pesanan Terlambat (%)")
ax2.set_ylabel("Customer State")
st.pyplot(fig2)

# Visualisasi 3: RFM Customer Segmentation
st.subheader("3. Analisis Lanjutan: Segmentasi Pelanggan (RFM Manual Grouping)")
ref_date = main_df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
rfm = main_df.groupby("customer_unique_id", as_index=False).agg(
    last_purchase=("order_purchase_timestamp", "max"),
    frequency=("order_id", "nunique"),
    monetary=("price", "sum")
)
rfm["recency"] = (ref_date - rfm["last_purchase"]).dt.days

def segment_customer(row):
    if row["recency"] <= 90 and row["monetary"] >= 150:
        return "High-Value Active"
    elif row["recency"] <= 180:
        return "Regular Active"
    elif row["recency"] <= 365:
        return "At-Risk"
    else:
        return "Churned / Inactive"

rfm["segment"] = rfm.apply(segment_customer, axis=1)
seg_counts = rfm["segment"].value_counts().reset_index()
seg_counts.columns = ["segment", "count"]

fig3, ax3 = plt.subplots(figsize=(10, 4))
sns.barplot(x="count", y="segment", data=seg_counts, palette=["#1f77b4"] + ["#d3d3d3"]*(len(seg_counts)-1), ax=ax3)
ax3.set_xlabel("Jumlah Pelanggan Unik")
ax3.set_ylabel("Segmen")
st.pyplot(fig3)