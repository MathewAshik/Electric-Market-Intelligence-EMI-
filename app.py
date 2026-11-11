"""
ELECTRIC MARKET INTELLIGENCE (EMI)
Main Application & Executive Gateway
"""

import os
import sys
import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Electric Market Intelligence (EMI)",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Root path resolution
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.ui_components import load_custom_css, render_header, render_kpi_card, render_sidebar_info
from src.database import init_db, load_dataframe
from src.analysis import get_executive_kpis
from src.data_collection import LiveDataCollector
from src.visualization import plot_time_series_trend, plot_stacked_segment_area

# Initialize system
load_custom_css()
init_db()
render_sidebar_info()

# Header
render_header("Executive Summary & Intelligence Gateway", "Real-World Data Science & Machine Learning Ecosystem for Indian EV Mobility")

# Retrieve core data
df_monthly = load_dataframe("cleaned_monthly_ev_registrations")
df_states = load_dataframe("cleaned_statewise_ev_data")

if df_monthly.empty or df_states.empty:
    with st.spinner("Initializing Data Pipelines & Validating Snapshots..."):
        collector = LiveDataCollector()
        collector.sync_all_sources()
        df_monthly = load_dataframe("cleaned_monthly_ev_registrations")
        df_states = load_dataframe("cleaned_statewise_ev_data")

kpis = get_executive_kpis(df_monthly, df_states)

# Top KPI Metric Ribbon
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    render_kpi_card(
        label="Cumulative EV Sales",
        value=f"{kpis['total_evs_sold']:,}",
        delta=f"+{kpis['yoy_growth_pct']}% YoY",
        delta_type="positive" if kpis['yoy_growth_pct'] >= 0 else "negative",
        subtext="Total Indian EV Registrations"
    )

with col2:
    render_kpi_card(
        label=f"Monthly Sales ({kpis['latest_month_name']})",
        value=f"{kpis['latest_month_sales']:,}",
        delta=f"{kpis['mom_growth_pct']}% MoM",
        delta_type="positive" if kpis['mom_growth_pct'] >= 0 else "negative",
        subtext="Latest VAHAN Monthly Volume"
    )

with col3:
    render_kpi_card(
        label="EV Penetration Rate",
        value=f"{kpis['ev_penetration_current_pct']}%",
        delta="Target: 30% by 2030",
        delta_type="neutral",
        subtext="Share of Total Vehicle Sales"
    )

with col4:
    render_kpi_card(
        label="5-Year Market CAGR",
        value=f"{kpis['cagr_5yr_pct']}%",
        delta="Exponential Growth",
        delta_type="positive",
        subtext="Compound Annual Growth Rate"
    )

with col5:
    render_kpi_card(
        label="Public Chargers Deployed",
        value=f"{kpis['total_public_chargers']:,}",
        delta=f"{kpis['national_ev_to_charger_ratio']} EVs / Charger",
        delta_type="neutral",
        subtext="BEE Operational Stations"
    )

st.markdown("<br>", unsafe_allow_html=True)

# Main Grid: Historical Trajectory & Segment Composition
left_col, right_col = st.columns([3, 2])

with left_col:
    st.subheader("📈 India EV Adoption Acceleration (2018 - 2025)")
    fig_trend = plot_time_series_trend(
        df_monthly,
        x_col="Date",
        y_cols=["Total_EV_Sales", "Two_Wheeler", "Four_Wheeler"],
        title="Monthly Registrations Trajectory (Units)"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with right_col:
    st.subheader("⚡ Vehicle Category Volume Breakdown")
    fig_area = plot_stacked_segment_area(df_monthly)
    st.plotly_chart(fig_area, use_container_width=True)

st.markdown("---")

# Navigation Hub & Architecture Overview
st.subheader("🧭 Intelligence Platform Navigation Hub")

nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    st.markdown("""
    #### 📊 Market Surveillance
    - **[1. Executive Dashboard](Executive_Dashboard)**: Core metrics, KPIs & macro charts.
    - **[2. Live Market Monitor](Live_Market_Monitor)**: Live data ingestion, endpoint ping & status.
    - **[3. Market Analytics](Market_Analytics)**: Segment shares, CAGR & OEM competitive landscape.
    """)

with nav_col2:
    st.markdown("""
    #### 🗺️ Spatial & Data Exploration
    - **[4. Geographical Intelligence](Geographical_Intelligence)**: Interactive India map & state rankings.
    - **[5. Data Explorer](Data_Explorer)**: Searchable tables, null audit & CSV exporter.
    - **[6. Machine Learning Lab](Machine_Learning_Lab)**: Predictive modeling, test benchmarks & forecasting.
    """)

with nav_col3:
    st.markdown("""
    #### 🎓 Deep Dive & Methodology
    - **[7. Real-World Case Studies](Case_Studies)**: In-depth research & policy evaluations.
    - **[8. Market Insights](Market_Insights)**: Automated dynamic data-driven findings.
    - **[9. Methodology & Sources](Methodology_and_Sources)**: Data pipeline & academic documentation.
    """)

# System Health and Architecture
with st.expander("🛠️ System Architecture & Data Pipeline Blueprint"):
    st.markdown("""
    ```
    ┌───────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
    │  REAL-WORLD SOURCES   │ ───► │  INGESTION & CACHING    │ ───► │   DATA VALIDATION       │
    │  • VAHAN Dashboard    │      │  • Live API Connectivity│      │   • Null Check & Types  │
    │  • BEE Infrastructure │      │  • Snapshot Fallback    │      │   • Integrity Scoring   │
    │  • IEA Global Outlook │      │  • SQLite Storage       │      │   • Outlier Treatment   │
    └───────────────────────┘      └─────────────────────────┘      └─────────────────────────┘
                                                                                 │
                                                                                 ▼
    ┌───────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
    │ STREAMLIT BI PLATFORM │ ◄─── │  PREDICTIVE ML LAB      │ ◄─── │  FEATURE ENGINEERING    │
    │ • Interactive Charts  │      │  • Multi-Model Training │      │  • Lag & Rolling Window │
    │ • Scenario Simulator  │      │  • Hold-out Validation  │      │  • Cyclical Encoding    │
    │ • Dynamic Insights    │      │  • Horizon Forecasting  │      │  • Macroeconomic Ratios │
    └───────────────────────┘      └─────────────────────────┘      └─────────────────────────┘
    ```
    """)

