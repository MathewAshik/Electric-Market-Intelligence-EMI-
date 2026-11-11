"""
PAGE 4: GEOGRAPHICAL INTELLIGENCE
Spatial Distribution, State-Level Penetration & Infrastructure Disparities
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.ui_components import load_custom_css, render_header, render_kpi_card, render_sidebar_info
from src.database import load_dataframe
from src.analysis import get_state_analytics
from src.visualization import plot_state_bubble_map, plot_state_ranking_bar, apply_chart_styling

st.set_page_config(page_title="Geographical Intelligence | EMI", page_icon="🗺️", layout="wide")
load_custom_css()
render_sidebar_info()

render_header("Geographical Intelligence", "State-Level Registrations, Regional Analysis & Infrastructure Density")

df_states = load_dataframe("cleaned_statewise_ev_data")

if df_states.empty:
    st.warning("State dataset not found. Please refresh.")
    st.stop()

analytics = get_state_analytics(df_states)

# Region KPI Quick Summary
reg_summary = analytics["region_summary"]
r_cols = st.columns(len(reg_summary))
for i, (_, row) in enumerate(reg_summary.iterrows()):
    with r_cols[i]:
        render_kpi_card(
            label=f"{row['Region']} India",
            value=f"{int(row['Total_EV_Registrations']):,}",
            delta=f"{row['Regional_EV_Share_Pct']}% Share",
            delta_type="positive" if row["Regional_EV_Share_Pct"] > 15 else "neutral",
            subtext=f"{int(row['Public_Charging_Stations'])} Chargers"
        )

st.markdown("<br>", unsafe_allow_html=True)

# Main Geographical Map
st.subheader("🗺️ India EV Adoption & Public Charging Station Map")
fig_map = plot_state_bubble_map(df_states)
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# State Leaderboard & Bottleneck Analysis
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🏆 Top 10 States by EV Registrations")
    fig_top = plot_state_ranking_bar(df_states, top_n=10, metric="Total_EV_Registrations", title="Top 10 States by Registration Volume")
    st.plotly_chart(fig_top, use_container_width=True)

with col_right:
    st.subheader("⚠️ Critical Charging Station Bottlenecks")
    fig_bot = plot_state_ranking_bar(df_states, top_n=10, metric="EVs_Per_Public_Charger", title="Highest EVs per Operational Public Charger (Acute Shortage)")
    st.plotly_chart(fig_bot, use_container_width=True)

st.markdown("---")

# Micro-Profile Explorer
st.subheader("🔍 State Deep-Dive Micro Profile")
state_names = sorted(df_states["State"].unique().tolist())
selected_state = st.selectbox("Select State / Union Territory to Inspect:", state_names, index=state_names.index("Maharashtra"))

state_row = df_states[df_states["State"] == selected_state].iloc[0]

p1, p2, p3, p4 = st.columns(4)
with p1:
    st.metric("Total EV Registrations", f"{int(state_row['Total_EV_Registrations']):,}")
with p2:
    st.metric("Public Chargers Deployed", f"{int(state_row['Public_Charging_Stations']):,}")
with p3:
    st.metric("EV Penetration Rate", f"{state_row['EV_Penetration_Pct']}%")
with p4:
    st.metric("Charging Adequacy Score", f"{state_row['Charging_Adequacy_Score']} / 10")

st.markdown(f"""
- **Region**: `{state_row['Region']}` | **State Code**: `{state_row['State_Code']}` | **Policy Incentive Rating**: `{state_row['Policy_Incentive']}`
- **Vehicle Mix**: Two-Wheelers: `{int(state_row['Two_Wheeler']):,}` | Three-Wheelers: `{int(state_row['Three_Wheeler']):,}` | Four-Wheelers: `{int(state_row['Four_Wheeler']):,}` | Buses: `{int(state_row['Bus']):,}`
- **EVs per Charger**: `{state_row['EVs_Per_Public_Charger']:.1f}:1` (National Benchmark: 25:1)
""")

