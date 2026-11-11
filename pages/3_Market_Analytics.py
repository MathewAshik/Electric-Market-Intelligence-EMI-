

import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.ui_components import load_custom_css, render_header, render_sidebar_info
from src.database import load_dataframe
from src.analysis import calculate_cagr, calculate_hhi
from src.visualization import plot_oem_market_share_donut, apply_chart_styling

st.set_page_config(page_title="Market Analytics | EMI", page_icon="📈", layout="wide")
load_custom_css()
render_sidebar_info()

render_header("Market Analytics", "Vehicle Segment Mix, OEM Market Share & Competitive Concentration")

df_monthly = load_dataframe("cleaned_monthly_ev_registrations")
df_oem = load_dataframe("cleaned_oem_market_share")

if df_monthly.empty or df_oem.empty:
    st.warning("Data loading in progress, please refresh.")
    st.stop()

# Tab Navigation
tab1, tab2, tab3 = st.tabs(["🏷️ Segment Evolution & CAGR", "🏭 OEM Competitive Battlefield", "⚖️ Market Concentration (HHI)"])

with tab1:
    st.subheader("Vehicle Class Growth & Mix Trends")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Yearly aggregate table
        yearly_summary = df_monthly.groupby("Year").agg({
            "Two_Wheeler": "sum",
            "Three_Wheeler": "sum",
            "Four_Wheeler": "sum",
            "Bus": "sum",
            "Total_EV_Sales": "sum"
        }).reset_index()
        
        yearly_summary["YoY_Growth_Pct"] = round(yearly_summary["Total_EV_Sales"].pct_change() * 100, 1).fillna(0)
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=yearly_summary["Year"], y=yearly_summary["Two_Wheeler"], name="2-Wheelers", marker_color="#00F2FE"))
        fig_bar.add_trace(go.Bar(x=yearly_summary["Year"], y=yearly_summary["Three_Wheeler"], name="3-Wheelers", marker_color="#4FACFE"))
        fig_bar.add_trace(go.Bar(x=yearly_summary["Year"], y=yearly_summary["Four_Wheeler"], name="4-Wheelers", marker_color="#00E676"))
        fig_bar.add_trace(go.Bar(x=yearly_summary["Year"], y=yearly_summary["Bus"], name="Commercial Buses", marker_color="#FFB300"))
        
        fig_bar.update_layout(barmode="stack")
        fig_bar = apply_chart_styling(fig_bar, title="Annual Sales by Vehicle Segment (Units)", height=400)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.markdown("#### Annual Growth & Segment Totals")
        st.dataframe(
            yearly_summary[["Year", "Two_Wheeler", "Four_Wheeler", "Total_EV_Sales", "YoY_Growth_Pct"]],
            use_container_width=True,
            hide_index=True
        )
        
        # Calculate Segment CAGRs (2019-2024)
        cagr_2w = calculate_cagr(
            yearly_summary[yearly_summary["Year"] == 2019]["Two_Wheeler"].values[0],
            yearly_summary[yearly_summary["Year"] == 2024]["Two_Wheeler"].values[0],
            5
        )
        cagr_4w = calculate_cagr(
            yearly_summary[yearly_summary["Year"] == 2019]["Four_Wheeler"].values[0],
            yearly_summary[yearly_summary["Year"] == 2024]["Four_Wheeler"].values[0],
            5
        )
        st.info(f"🚀 **Two-Wheeler 5-Year CAGR**: `{cagr_2w}%`\n\n⚡ **Four-Wheeler 5-Year CAGR**: `{cagr_4w}%`")

with tab2:
    st.subheader("OEM & Automaker Market Share Landscape")
    
    c_sel1, c_sel2 = st.columns(2)
    with c_sel1:
        selected_seg = st.selectbox("Select Segment", ["Two_Wheeler", "Four_Wheeler", "Bus"], index=0)
    with c_sel2:
        available_years = sorted(df_oem[df_oem["Segment"] == selected_seg]["Year"].unique(), reverse=True)
        selected_yr = st.selectbox("Select Year", available_years, index=0)
        
    col_oem1, col_oem2 = st.columns([1, 1])
    
    with col_oem1:
        fig_donut = plot_oem_market_share_donut(df_oem, segment=selected_seg, year=selected_yr)
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with col_oem2:
        # Multi-year OEM trajectory
        seg_oems = df_oem[df_oem["Segment"] == selected_seg]
        fig_oem_trend = px.line(
            seg_oems,
            x="Year",
            y="Market_Share_Pct",
            color="OEM",
            markers=True,
            title=f"<b>Historical Market Share Shift: {selected_seg.replace('_', ' ')}</b>"
        )
        fig_oem_trend = apply_chart_styling(fig_oem_trend, height=420)
        st.plotly_chart(fig_oem_trend, use_container_width=True)

with tab3:
    st.subheader("⚖️ Herfindahl-Hirschman Index (HHI) Concentration Analysis")
    st.markdown("""
    The **Herfindahl-Hirschman Index (HHI)** is the premier regulatory metric for measuring market concentration and antitrust risk:
    - **HHI < 1,500**: Unconcentrated, highly competitive market.
    - **1,500 ≤ HHI ≤ 2,500**: Moderately concentrated market.
    - **HHI > 2,500**: Highly concentrated market (Oligopoly / Dominant player).
    """)
    
    hhi_records = []
    for (seg, yr), grp in df_oem.groupby(["Segment", "Year"]):
        res = calculate_hhi(grp["Market_Share_Pct"].tolist())
        hhi_records.append({
            "Segment": seg.replace("_", " "),
            "Year": yr,
            "HHI Index": res["hhi_index"],
            "Market Structure": res["classification"],
            "Concentration Risk": res["concentration_risk"]
        })
    df_hhi = pd.DataFrame(hhi_records).sort_values(["Segment", "Year"], ascending=[True, False])
    st.dataframe(df_hhi, use_container_width=True, hide_index=True)

