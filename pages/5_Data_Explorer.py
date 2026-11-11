"""
PAGE 5: DATA EXPLORER & QUALITY LAB
Searchable Tables, Statistical Summaries, Schema Profiling & CSV Export
"""

import os
import sys
import streamlit as st
import pandas as pd

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.ui_components import load_custom_css, render_header, render_sidebar_info
from src.database import load_dataframe
from src.data_validation import DataValidator
from src.visualization import plot_correlation_heatmap
from src.analysis import compute_correlation_matrix

st.set_page_config(page_title="Data Explorer | EMI", page_icon="🔍", layout="wide")
load_custom_css()
render_sidebar_info()

render_header("Data Explorer & Quality Lab", "Granular Tabular Inspection, Missing Value Auditing & Data Profiling")

dataset_options = {
    "Cleaned Monthly EV Registrations (VAHAN)": "cleaned_monthly_ev_registrations",
    "State-wise EV Registrations & Charging (BEE)": "cleaned_statewise_ev_data",
    "OEM / Automaker Market Shares (FADA)": "cleaned_oem_market_share",
    "Global EV Outlook Benchmark (IEA)": "cleaned_global_ev_comparison",
    "Battery Pack Cost & Fuel Disparity": "cleaned_economic_data"
}

selected_label = st.selectbox("Select Target Dataset to Inspect:", list(dataset_options.keys()))
table_name = dataset_options[selected_label]
df = load_dataframe(table_name)

if df.empty:
    st.error("Selected dataset could not be retrieved from database.")
    st.stop()

# Data Quality Report
quality_report = DataValidator.inspect_dataset(df, selected_label)

st.subheader("🛡️ Automated Data Quality & Schema Report")
q1, q2, q3, q4, q5 = st.columns(5)
with q1:
    st.metric("Total Records", f"{quality_report['rows']:,}")
with q2:
    st.metric("Total Columns", f"{quality_report['cols']}")
with q3:
    st.metric("Missing Cells", f"{quality_report['null_cells']} ({quality_report['null_pct']}%)")
with q4:
    st.metric("Duplicate Rows", f"{quality_report['duplicate_rows']}")
with q5:
    st.metric("Integrity Score", f"{quality_report['integrity_score']} / 100", delta=quality_report["status"])

st.markdown("<br>", unsafe_allow_html=True)

# Granular Column Profile Expander
with st.expander("📋 Detailed Column Data Types & Value Ranges"):
    col_profile_df = pd.DataFrame(quality_report["column_details"])
    st.dataframe(col_profile_df, use_container_width=True, hide_index=True)

st.markdown("---")

# Searchable & Filterable Table
st.subheader("🔍 Searchable & Filterable Data Table")

col_search, col_sort, col_order = st.columns([2, 1, 1])
with col_search:
    search_query = st.text_input("Quick Search Keyword (across all text columns):", "")
with col_sort:
    sort_col = st.selectbox("Sort By Column:", df.columns.tolist())
with col_order:
    sort_asc = st.radio("Order:", ["Ascending", "Descending"], horizontal=True) == "Ascending"

# Apply Search
filtered_df = df.copy()
if search_query:
    mask = filtered_df.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)
    filtered_df = filtered_df[mask]

filtered_df = filtered_df.sort_values(sort_col, ascending=sort_asc)

st.dataframe(filtered_df, use_container_width=True, hide_index=True)

# Download Button
csv_data = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label=f"📥 Download Filtered {selected_label} (CSV)",
    data=csv_data,
    file_name=f"{table_name}_filtered.csv",
    mime="text/csv",
    use_container_width=True
)

st.markdown("---")

# Statistical Summaries & Correlation Matrix
st.subheader("📊 Descriptive Statistics & Pearson Correlation")
tab_stat1, tab_stat2 = st.tabs(["🔢 Numerical Descriptive Statistics", "🔥 Correlation Matrix"])

with tab_stat1:
    st.dataframe(df.describe().T.round(2), use_container_width=True)

with tab_stat2:
    corr_df = compute_correlation_matrix(df)
    if not corr_df.empty and corr_df.shape[0] > 1:
        fig_corr = plot_correlation_heatmap(corr_df)
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Insufficient numerical columns in this dataset to generate correlation matrix.")

