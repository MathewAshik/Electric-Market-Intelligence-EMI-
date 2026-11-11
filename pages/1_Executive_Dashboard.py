"""
PAGE 1: EXECUTIVE DASHBOARD
Comprehensive Overview of India's Electric Vehicle Market
"""

import os
import sys
import streamlit as st
import pandas as pd

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.ui_components import load_custom_css, render_header, render_kpi_card, render_sidebar_info
from src.database import load_dataframe
from src.analysis import get_executive_kpis
from src.visualization import plot_time_series_trend, plot_stacked_segment_area, plot_state_ranking_bar

st.set_page_config(page_title="Executive Dashboard | EMI", page_icon="⚡", layout="wide")
load_custom_css()
render_sidebar_info()

render_header("Executive Dashboard", "Macro Indicators, Market Growth Metrics & Fleet Performance")

# Data Loading
df_monthly = load_dataframe("cleaned_monthly_ev_registrations")
df_states = load_dataframe("cleaned_statewise_ev_data")
df_econ = load_dataframe("cleaned_economic_data")

if df_monthly.empty:
    st.warning("Data is initializing, please refresh.")
    st.stop()

# Filters in Expander
with st.expander("🔍 Interactive Market Filters", expanded=True):
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        years = sorted(df_monthly["Year"].unique().tolist())
        selected_years = st.multiselect("Select Years to Analyze", options=years, default=years)
        
    with col_f2:
        segments = ["Two_Wheeler", "Three_Wheeler", "Four_Wheeler", "Bus"]
        selected_segments = st.multiselect("Vehicle Segments", options=segments, default=["Two_Wheeler", "Four_Wheeler", "Three_Wheeler"])
        
    with col_f3:
        min_date = pd.to_datetime(df_monthly["Date"]).min().date()
        max_date = pd.to_datetime(df_monthly["Date"]).max().date()
        date_range = st.date_input("Date Range", value=[min_date, max_date], min_value=min_date, max_value=max_date)

# Apply filters
df_filtered = df_monthly[df_monthly["Year"].isin(selected_years)].copy()
if len(date_range) == 2:
    start_d, end_d = date_range
    df_filtered["Date_DT"] = pd.to_datetime(df_filtered["Date"]).dt.date
    df_filtered = df_filtered[(df_filtered["Date_DT"] >= start_d) & (df_filtered["Date_DT"] <= end_d)]

kpis = get_executive_kpis(df_filtered, df_states)

# Top KPI row
k1, k2, k3, k4 = st.columns(4)

with k1:
    render_kpi_card(
        label="Filtered EV Registrations",
        value=f"{kpis['total_evs_sold']:,}",
        delta=f"+{kpis['yoy_growth_pct']}% YoY",
        delta_type="positive" if kpis['yoy_growth_pct'] >= 0 else "negative",
        subtext="Total Volume in Selection"
    )

with k2:
    render_kpi_card(
        label="Latest Monthly Run-Rate",
        value=f"{kpis['latest_month_sales']:,}",
        delta=f"{kpis['mom_growth_pct']}% MoM",
        delta_type="positive" if kpis['mom_growth_pct'] >= 0 else "negative",
        subtext=f"Recorded in {kpis['latest_month_name']}"
    )

with k3:
    render_kpi_card(
        label="Current EV Penetration",
        value=f"{kpis['ev_penetration_current_pct']}%",
        delta="Share of Total Auto Sales",
        delta_type="neutral",
        subtext="National ICE Disruption Ratio"
    )

with k4:
    render_kpi_card(
        label="Total CO2 Avoided",
        value=f"{kpis['total_co2_saved_mt']:,} MT",
        delta="Decarbonization Impact",
        delta_type="positive",
        subtext="Estimated Lifecycle Tailpipe Avoidance"
    )

st.markdown("<br>", unsafe_allow_html=True)

# Trend Visualizations
c1, c2 = st.columns([3, 2])

with c1:
    st.subheader("📊 Registration Trajectory by Selected Segments")
    fig_line = plot_time_series_trend(
        df_filtered,
        x_col="Date",
        y_cols=selected_segments or ["Total_EV_Sales"],
        title="Monthly EV Registrations in Selected Range"
    )
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    st.subheader("🏆 Leading States by Cumulative Adoption")
    fig_states = plot_state_ranking_bar(df_states, top_n=8, metric="Total_EV_Registrations", title="Top 8 Indian States by EV Registrations")
    st.plotly_chart(fig_states, use_container_width=True)

st.markdown("---")

# Economic Impact Summary
st.subheader("💰 Economic Parity & Fuel Disparity Dynamics")
e1, e2 = st.columns(2)

with e1:
    if not df_econ.empty:
        st.markdown("""
        #### Commuter Running Cost Comparison (INR per Km)
        | Vehicle Class | ICE (Petrol/Diesel) | Electric Vehicle (EV) | Net Commuter Savings |
        | :--- | :--- | :--- | :--- |
        | **Two-Wheeler (2W)** | **₹ 2.33 / km** | **₹ 0.23 / km** | **₹ 2.10 / km (90% Savings)** |
        | **Four-Wheeler (4W)** | **₹ 7.50 / km** | **₹ 1.25 / km** | **₹ 6.25 / km (83% Savings)** |
        | **Commercial 3W** | **₹ 3.80 / km** | **₹ 0.45 / km** | **₹ 3.35 / km (88% Savings)** |
        """)
        st.info("💡 **Key Finding**: Commercial fleet operators recover the upfront EV price premium within 11 to 14 months purely on fuel arbitrage.")

with e2:
    if not df_econ.empty:
        import plotly.graph_objects as go
        fig_econ = go.Figure()
        fig_econ.add_trace(go.Scatter(
            x=df_econ["Year"],
            y=df_econ["Battery_Pack_USD_per_kWh"],
            mode="lines+markers",
            name="Battery Pack ($/kWh)",
            line=dict(color="#00F2FE", width=3)
        ))
        fig_econ.add_trace(go.Scatter(
            x=df_econ["Year"],
            y=df_econ["Petrol_Price_INR_per_L"],
            mode="lines+markers",
            name="Petrol Price (₹/Litre)",
            line=dict(color="#FF5252", width=3)
        ))
        fig_econ.update_layout(
            title="<b>Battery Cost Deflation vs Petrol Inflation (2018-2025)</b>",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E0E6ED"),
            height=280,
            margin=dict(l=30, r=20, t=40, b=30)
        )
        st.plotly_chart(fig_econ, use_container_width=True)

