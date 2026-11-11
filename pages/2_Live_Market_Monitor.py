"""
PAGE 2: LIVE MARKET MONITOR
Real-Time Ingestion, Feed Health, and Transparency Portal
"""

import os
import sys
import streamlit as st
import pandas as pd

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.ui_components import load_custom_css, render_header, render_kpi_card, render_sidebar_info
from src.data_collection import LiveDataCollector, DATA_SOURCES_CONFIG
from src.database import get_recent_sync_events

st.set_page_config(page_title="Live Market Monitor | EMI", page_icon="📡", layout="wide")
load_custom_css()
render_sidebar_info()

render_header("Live Market Monitor", "Real-Time Ingestion Channels, API Feeds & Source Transparency")

collector = LiveDataCollector()

# Refresh Control Bar
col_ctrl1, col_ctrl2 = st.columns([3, 1])
with col_ctrl1:
    st.markdown("""
    This monitor inspects live government portals and official data repositories.
    If official live APIs require authorization keys, the platform gracefully switches to the
    **verified latest published dataset snapshot** and records latency and status transparently.
    """)
with col_ctrl2:
    if st.button("🔄 Trigger Immediate Data Refresh", use_container_width=True):
        with st.spinner("Connecting to external endpoints and synchronizing registry..."):
            sync_result = collector.sync_all_sources()
            st.success("✅ Synchronization completed successfully!")
            st.rerun()

status_data = collector.get_latest_status()
last_sync_time = status_data.get("last_global_sync", "N/A")

st.markdown(f"**Global Feed Synchronization Timestamp**: `{last_sync_time}`")
st.markdown("<br>", unsafe_allow_html=True)

# Data Freshness & Source Status Grid
st.subheader("🌐 Data Provider Ingestion Channels")

sources = status_data.get("sources", [])

for src in sources:
    with st.container():
        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
        
        with c1:
            st.markdown(f"#### [{src['source_name']}]({src['url']})")
            st.caption(f"Portal URL: {src['url']}")
            
        with c2:
            st.markdown(f"**Classification**:")
            if src["status_category"] == "LIVE DATA":
                st.markdown('<span class="badge-live">● LIVE API FEED</span>', unsafe_allow_html=True)
            elif src["status_category"] == "LATEST PUBLISHED DATA":
                st.markdown('<span class="badge-cached">● LATEST PUBLISHED DATA</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="badge-warning">● HISTORICAL DATA</span>', unsafe_allow_html=True)
            st.caption(src["badge_text"])
            
        with c3:
            st.markdown(f"**Snapshot Records**: `{src['records']:,}`")
            st.caption(f"Network Latency: `{src['latency_ms']} ms`")
            
        with c4:
            st.markdown(f"**Last Sync**:")
            st.markdown(f"`{src['last_synced']}`")
            st.caption(src["details"][:40] + "..." if len(src["details"]) > 40 else src["details"])
            
        st.markdown("<hr style='margin: 10px 0; border-color: #252D3D;'>", unsafe_allow_html=True)

# SQLite Sync Audit Log
st.subheader("📋 SQLite Ingestion Audit Trail (Last 10 Sync Cycles)")
audit_df = get_recent_sync_events(limit=10)

if not audit_df.empty:
    st.dataframe(audit_df, use_container_width=True, hide_index=True)
else:
    st.info("No sync logs recorded yet in database.")

st.markdown("---")

# API Configuration Guide
with st.expander("🔑 How to Configure Real-World Production API Keys"):
    st.markdown("""
    ### Official Open Data API Setup
    To pull direct automated daily feeds from India's Open Government Data Portal:
    
    1. Register for an API token at [https://data.gov.in/](https://data.gov.in/).
    2. Create a `.env` file in the project root directory:
       ```env
       DATA_GOV_IN_API_KEY="your_api_key_here"
       BEE_API_KEY="your_bee_key_if_available"
       ```
    3. Restart the Streamlit application or click **Trigger Immediate Data Refresh**.
    4. The monitor will automatically detect the key, transition classification to **LIVE DATA**, and stream daily incremental registration records.
    """)

