"""
ELECTRIC MARKET INTELLIGENCE (EMI)
UI Components & Shared Layout Utilities
"""

import os
import streamlit as st

def load_custom_css():
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "custom.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="emi-header-container">
        <h1 class="emi-title">⚡ ELECTRIC MARKET INTELLIGENCE (EMI)</h1>
        <div class="emi-tagline">Discover Trends • Analyze Markets • Predict the Future</div>
        <p class="emi-subtitle"><b>{title}</b> &mdash; {subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def render_kpi_card(label: str, value: str, delta: str = "", delta_type: str = "positive", subtext: str = ""):
    delta_class = "kpi-delta-positive" if delta_type == "positive" else "kpi-delta-negative" if delta_type == "negative" else "kpi-subtext"
    delta_symbol = "▲" if delta_type == "positive" else "▼" if delta_type == "negative" else "•"
    
    delta_html = f'<div class="{delta_class}">{delta_symbol} {delta}</div>' if delta else ""
    subtext_html = f'<div class="kpi-subtext">{subtext}</div>' if subtext else ""
    
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
        {subtext_html}
    </div>
    """, unsafe_allow_html=True)

def render_sidebar_info():
    with st.sidebar:
        st.markdown("""
        <div style="padding: 10px 0 20px 0; border-bottom: 1px solid #252D3D;">
            <div style="font-weight: 800; font-size: 1.1rem; color: #00F2FE;">⚡ EMI PLATFORM</div>
            <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px;">India EV Market Intelligence</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📊 Platform Status")
        st.markdown("""
        - **Domain**: Electric Vehicle (EV) Ecosystem
        - **Primary Geography**: India (36 States & UTs)
        - **Data Status**: <span class="badge-cached">Active Ingestion</span>
        - **ML Engine**: Scikit-Learn Ensemble
        - **Version**: 2.4 Enterprise
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🏛️ Official Sources")
        st.markdown("""
        - 🚙 [MoRTH VAHAN Dashboard](https://vahan.parivahan.gov.in/)
        - ⚡ [Bureau of Energy Efficiency (BEE)](https://beeindia.gov.in/)
        - 🌐 [IEA Global EV Outlook](https://www.iea.org/)
        - 📈 [FADA Research Portal](https://fada.in/)
        """)
        
        st.markdown("---")
        st.caption("Academic Technical Project & Capstone Defense\nAll Rights Reserved © 2026")

