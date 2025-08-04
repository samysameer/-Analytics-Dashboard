import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

df = pd.read_csv("hotels (1).csv")
df.columns = df.columns.str.strip()

st.set_page_config(layout="wide")

st.sidebar.image("12.png", width=100)
st.sidebar.title("Hotel Dashboard Filters")

years = sorted(df['arrival_date_year'].dropna().unique())
months = df['arrival_date_month'].dropna().unique()

selected_year = st.sidebar.selectbox("Select Year", years)
selected_month = st.sidebar.selectbox("Select Month", months)

filtered_df = df[(df['arrival_date_year'] == selected_year) & 
                 (df['arrival_date_month'] == selected_month)]

st.title("🏨 Hotel Booking Dashboard")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Bookings", f"{filtered_df.shape[0]}")
col2.metric("Countries", f"{filtered_df['country'].nunique()}")
col3.metric("Avg. ADR", f"${filtered_df['adr'].mean():.2f}")
col4.metric("Max Special Requests", f"{filtered_df['total_of_special_requests'].max()}")

st.subheader("💰 Average ADR per Country")
avg_adr = filtered_df.groupby("country")["adr"].mean().sort_values(ascending=False).head(10)
fig1, ax1 = plt.subplots()
avg_adr.plot(kind="bar", ax=ax1, color='skyblue')
ax1.set_ylabel("Average ADR ($)")
plt.xticks(rotation=45)
st.pyplot(fig1)

st.subheader("📊 Market Segment Share")
market_counts = filtered_df['market_segment'].value_counts()
online_ta_count = market_counts.get('Online TA', 0)
other_count = market_counts.sum() - online_ta_count
simplified_counts = pd.Series({'Online TA': other_count, 'Other': online_ta_count})
fig2, ax2 = plt.subplots()
ax2.pie(
    simplified_counts,
    labels=simplified_counts.index,
    autopct='%1.1f%%',
    startangle=140,
    colors=['#1f77b4', '#ff7f0e']
)
ax2.axis("equal")
st.pyplot(fig2)

st.subheader("📈 Monthly Booking Trend")
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
month_to_number = {month: i+1 for i, month in enumerate(month_order)}
df['month_num'] = df['arrival_date_month'].map(month_to_number)
monthly_trend = df.groupby(['arrival_date_year', 'month_num']).size().reset_index(name='Bookings')
fig3, ax3 = plt.subplots(figsize=(12, 6))
for year in monthly_trend['arrival_date_year'].unique():
    subset = monthly_trend[monthly_trend['arrival_date_year'] == year]
    ax3.plot(subset['month_num'], subset['Bookings'], marker='o', label=str(year))
ax3.set_xticks(range(1, 13))
ax3.set_xticklabels(month_order, rotation=45)
ax3.set_ylabel("Bookings")
ax3.set_xlabel("Month")
ax3.legend(title="Year")
plt.tight_layout()
st.pyplot(fig3)

st.subheader("🌍 ADR Bubble Map by Country")
if 'country' in df.columns:
    adr_by_country = filtered_df.groupby("country")["adr"].mean().reset_index()
    fig_map = px.scatter_geo(
        adr_by_country,
        locations="country",
        locationmode="ISO-3",
        color="adr",
        size="adr",
        projection="natural earth",
        title="Average ADR per Country",
        color_continuous_scale="Plasma"
    )
    fig_map.update_traces(marker_line_width=0)
    st.plotly_chart(fig_map, use_container_width=True)

st.subheader("🔗 Correlation Heatmap")
numeric_df = filtered_df.select_dtypes(include=['float64', 'int64'])
st.sidebar.subheader("🔧 Correlation Heatmap Settings")
selected_corr_cols = st.sidebar.multiselect(
    "Select Numeric Columns for Correlation",
    options=numeric_df.columns.tolist(),
    default=numeric_df.columns.tolist()
)
if selected_corr_cols:
    corr_matrix = numeric_df[selected_corr_cols].corr()
    fig_corr, ax_corr = plt.subplots(figsize=(10, 6))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", ax=ax_corr)
    st.pyplot(fig_corr)
else:
    st.info("Please select at least one column to display the correlation heatmap.")

st.subheader("⬇️ Download Filtered Data")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("Download CSV", csv, "filtered_data.csv", "text/csv")
