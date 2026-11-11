"""
PAGE 8: MARKET INSIGHTS
Automated Dynamic Analytical Insight Engine & Strategic Market Forecasts
"""

import os
import sys
import streamlit as st
import pandas as pd

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.ui_components import load_custom_css, render_header, render_sidebar_info
from src.insights import AutomatedInsightEngine

st.set_page_config(page_title="Market Insights | EMI", page_icon="💡", layout="wide")
load_custom_css()
render_sidebar_info()

render_header("Market Insights Engine", "Automated Heuristic Observations, Trend Synthesis & Strategic Outlook")

# Initialize Insight Engine
with st.spinner("Analyzing datasets and generating real-time dynamic market insights..."):
    engine = AutomatedInsightEngine()
    insights = engine.generate_all_insights()

st.markdown(f"**Identified Dynamic Insights**: `{len(insights)} Automated Findings Derived Directly from Data`")

# Category Filter
categories = list(set([ins["category"] for ins in insights]))
selected_cat = st.multiselect("Filter by Insight Domain:", categories, default=categories)

# Render Dynamic Insight Cards
for ins in insights:
    if ins["category"] in selected_cat:
        card_class = "insight-card"
        if ins["severity"] == "WARNING":
            card_class += " warning"
        elif ins["severity"] == "SUCCESS":
            card_class += " success"
        elif ins["severity"] == "ALERT":
            card_class += " alert"
            
        badge_class = "badge-live" if ins["severity"] == "SUCCESS" else "badge-warning" if ins["severity"] == "WARNING" else "badge-cached"
        
        st.markdown(f"""
        <div class="{card_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="{badge_class}">{ins['badge']}</span>
                <span style="font-size: 0.8rem; color: #94A3B8; font-weight: 600;">Domain: {ins['category']}</span>
            </div>
            <h3 style="margin: 6px 0 10px 0; font-size: 1.25rem; color: #FFFFFF;">{ins['title']}</h3>
            <p style="color: #CBD5E1; font-size: 0.95rem; line-height: 1.6; margin-bottom: 12px;">{ins['observation']}</p>
            <div style="background: rgba(0, 0, 0, 0.25); border-radius: 6px; padding: 10px 14px; border: 1px solid rgba(255, 255, 255, 0.08);">
                <span style="color: #00F2FE; font-weight: 700; font-size: 0.85rem;">⚡ Strategic Takeaway: </span>
                <span style="color: #94A3B8; font-size: 0.85rem;">{ins['actionable_takeaway']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Strategic Market Matrix
st.subheader("🎯 Market Risk vs Opportunity Matrix")

col_opp, col_risk = st.columns(2)

with col_opp:
    st.markdown("""
    #### 🚀 Prime Growth Opportunities
    1. **E-3W Tier-2/3 Commercial Fleet Electrification**:
       - 3-Wheelers represent the fastest route to 80% electrification due to operational payback in under 12 months.
    2. **Battery-as-a-Service (BaaS) Business Models**:
       - Separating battery cost from ex-showroom sticker price (e.g. MG Windsor EV) reduces upfront acquisition cost by ~35%.
    3. **Captive Fleet Depot Charging**:
       - Dedicated charging hubs for municipal e-buses and logistics delivery fleets guarantee high asset utilization.
    """)

with col_risk:
    st.markdown("""
    #### ⚠️ Structural Market Risks
    1. **Tapering of Direct Purchase Subsidies (FAME → PM E-DRIVE)**:
       - Reduction in per-kWh consumer subsidies requires OEMs to accelerate localization to avoid margin squeeze.
    2. **Grid Distribution Bottlenecks**:
       - Clustering of fast DC charging stations without transformer upgrades causes localized peak-load strains for DISCOMs.
    3. **Residual Resale Value Uncertainty**:
       - Consumer uncertainty regarding 5-year battery degradation and secondary market resale pricing.
    """)

