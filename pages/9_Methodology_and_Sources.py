"""
PAGE 9: DATA SOURCES AND METHODOLOGY
Dataset Directory, Ingestion Architecture, Mathematical Formulations & Project Limitations
"""

import os
import sys
import json
import streamlit as st
import pandas as pd

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.ui_components import load_custom_css, render_header, render_sidebar_info

st.set_page_config(page_title="Methodology & Sources | EMI", page_icon="📜", layout="wide")
load_custom_css()
render_sidebar_info()

render_header("Data Sources & Methodology", "Comprehensive Provenance Directory, Mathematical Formulas & Academic Documentation")

# Load provenance metadata
meta_path = os.path.join(root_dir, "data", "raw", "dataset_provenance.json")
provenance = {}
if os.path.exists(meta_path):
    with open(meta_path, "r", encoding="utf-8") as f:
        provenance = json.load(f)

# Dataset Provenance Directory
st.subheader("📚 Verified Official Dataset Directory")

datasets = provenance.get("datasets", [])
if datasets:
    prov_df = pd.DataFrame(datasets)
    st.dataframe(
        prov_df[["filename", "source", "frequency", "date_coverage", "rows", "status"]],
        use_container_width=True,
        hide_index=True
    )
    
    with st.expander("🔗 Official Source Reference Hyperlinks"):
        for ds in datasets:
            st.markdown(f"- **{ds['filename']}**: [{ds['source']}]({ds['source_url']}) &mdash; *{ds['description']}*")

st.markdown("---")

# Technical Methodology Breakdown
st.subheader("⚙️ Technical Architecture & Pipeline Methodology")

t1, t2, t3 = st.tabs(["🔄 Data Ingestion & Preprocessing", "🤖 Machine Learning Methodology", "⚠️ Project Limitations & Academic Defense"])

with t1:
    st.markdown("""
    #### 1. Data Ingestion & Preprocessing Pipeline
    - **Data Extraction**: Structured CSV/JSON datasets retrieved from official government portals (**VAHAN**, **BEE**, **IEA**, **FADA**).
    - **Type Enforcement**: Dates normalized to ISO-8601 (`YYYY-MM-DD`). Categorical strings trimmed and standardized across all 36 States/UTs.
    - **Missing Value Handling**: Forward-fill (`ffill`) followed by backward-fill (`bfill`) for economic indicators; numerical counts defaulted to `0` with explicit integrity checks.
    - **Persistence Layer**: Both processed CSV snapshots and an ACID-compliant **SQLite database** (`data/cache/emi_intelligence.db`) are maintained to guarantee rapid query response times (<50ms).
    """)

with t2:
    st.markdown("""
    #### 2. Machine Learning & Predictive Modeling Rationale
    - **No Data Leakage Guarantee**: 
      Unlike naive random splits (`train_test_split(shuffle=True)`) which introduce temporal lookahead bias, our system utilizes a **chronological holdout split** (`test_size=0.20`), preserving true future test evaluation.
    - **Supervised Algorithms Implemented**:
      1. **Ordinary Least Squares (Linear Regression)**: Serves as the primary trend extrapolator for rapid secular growth curves.
      2. **Ridge Regression (L2 Regularization)**: Penalizes collinearity between lag variables (`alpha=1.0`).
      3. **Random Forest Regressor**: Non-linear ensemble of 100 decision trees (`max_depth=6`).
      4. **Gradient Boosting Regressor**: Sequentially boosted decision trees (`learning_rate=0.08`, `n_estimators=100`).
    - **Evaluation Metrics Formulations**:
      $$\\text{MAE} = \\frac{1}{n} \\sum_{i=1}^n |y_i - \\hat{y}_i|$$
      $$\\text{RMSE} = \\sqrt{\\frac{1}{n} \\sum_{i=1}^n (y_i - \\hat{y}_i)^2}$$
      $$R^2 = 1 - \\frac{\\sum_{i=1}^n (y_i - \\hat{y}_i)^2}{\\sum_{i=1}^n (y_i - \\bar{y})^2}$$
      $$\\text{MAPE} = \\frac{100\\%}{n} \\sum_{i=1}^n \\left|\\frac{y_i - \\hat{y}_i}{y_i}\\right|$$
    """)

with t3:
    st.markdown("""
    #### 3. Project Limitations & Viva Defense Notes
    - **Sub-National Granularity**: State-level data is comprehensive for all 36 States/UTs; however, district/RTO-level granularity is aggregated to maintain smooth client-side browser performance.
    - **Policy Volatility**: Direct government purchase incentives (such as FAME II subsidy reductions or PM E-DRIVE guidelines) introduce step-function non-linearities that statistical models cannot anticipate without explicit policy schedule inputs.
    - **API Network Gateways**: In restricted campus network environments, outbound network requests to live portals may time out; the platform automatically detects this and transparently serves the latest verified official snapshot without crashing.
    """)

