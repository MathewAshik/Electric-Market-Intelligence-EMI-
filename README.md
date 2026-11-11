# ⚡ ELECTRIC MARKET INTELLIGENCE (EMI)
> **Discover Trends. Analyze Markets. Predict the Future.**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Streamlit 1.35+](https://img.shields.io/badge/Streamlit-Enterprise%20BI-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Ensemble%20ML-orange.svg)](https://scikit-learn.org/)
[![Database](https://img.shields.io/badge/SQLite3-ACID%20Persistence-003B57.svg)](https://sqlite.org/)
[![Build Status](https://img.shields.io/badge/Tests-7%20Passed%20(100%25)-00E676.svg)](tests/)

---

## 🌟 Executive Project Overview

**Electric Market Intelligence (EMI)** is an advanced, production-grade Data Science and Machine Learning web platform architected for deep surveillance, spatial intelligence, and predictive forecasting of **India's Electric Vehicle (EV) Ecosystem**.

Developed as an autonomous, full-stack analytical platform, EMI synthesizes verified datasets from official government registries (**MoRTH VAHAN**, **Bureau of Energy Efficiency (BEE)**, **Ministry of Heavy Industries**, **NITI Aayog**, and the **International Energy Agency**). It couples statistical rigor with multi-algorithm supervised machine learning, dynamic scenario simulation, and an automated data-driven insight engine.

---

## 🏛️ System Architecture Blueprint

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DATA ACQUISITION LAYER                          │
│   MoRTH VAHAN (90 mo) │ BEE Chargers (36 states) │ IEA Global │ FADA   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  DATA INGESTION & QUALITY PIPELINE                     │
│   • Live Connectivity Check & Latency Probing                          │
│   • Fallback Snapshot Routing (Transparent Ingestion Classification)   │
│   • DataValidator: Null Auditing, Range Checks, Integrity Scoring      │
│   • ACID-Compliant SQLite Persistence (emi_intelligence.db)            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                FEATURE ENGINEERING & STATISTICAL ENGINE                │
│   • Backward Lags (1m, 2m, 3m, 12m) & Shifted Rolling Averages         │
│   • Cyclical Trigonometric Calendar Signals (Sin/Cos Encodings)        │
│   • Economic Interaction Ratios (Battery Cost vs Petrol Disparity)     │
│   • Herfindahl-Hirschman Index (HHI) Market Concentration              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      MACHINE LEARNING PREDICTIVE LAB                   │
│   • Temporal Chronological Hold-Out Train-Test Split (No Data Leakage) │
│   • Multi-Model Suite: Linear, Ridge, Random Forest, Gradient Boost    │
│   • Forward Horizon Forecasting (Base, Bull +15%, Bear -15% Scenarios) │
│   • Interactive What-If Simulator (Battery $/kWh vs Petrol ₹/L)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 STREAMLIT MULTI-PAGE ENTERPRISE PORTAL                 │
│   1. Executive Dashboard          6. Machine Learning Lab              │
│   2. Live Market Monitor          7. Real-World Case Studies           │
│   3. Market Analytics             8. Automated Market Insights         │
│   4. Geographical Intelligence    9. Data Sources & Methodology        │
│   5. Data Explorer & CSV Export                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart & Application Launch

### 1. Prerequisites & Installation
Ensure Python 3.10 or higher is installed. Open your terminal in the workspace:

```powershell
# Navigate to the workspace root
cd c:\Users\mathe\OneDrive\Documents\Desktop\EVision

# Install required dependencies
pip install -r requirements.txt
```

### 2. Application Launch Command
To launch the complete interactive multi-page web application:

```powershell
streamlit run app.py
```
> The application will automatically initialize the local SQLite database, populate processed data, and open in your default browser at `http://localhost:8501`.

---

## 📊 Complete Multi-Page Modules

| Page | Module Title | Primary Capabilities |
| :--- | :--- | :--- |
| **Home** | `app.py` | Executive Gateway, high-level KPIs, system status, and architectural routing. |
| **Page 1** | `1_Executive_Dashboard.py` | Total market indicators, registration trends, segment mix, and fuel disparity. |
| **Page 2** | `2_Live_Market_Monitor.py` | Real-time endpoint pings, latency tracking, SQLite audit log, and fallback routing. |
| **Page 3** | `3_Market_Analytics.py` | 5-Year CAGR calculation, OEM competitive dynamics, and HHI market concentration. |
| **Page 4** | `4_Geographical_Intelligence.py` | Interactive India bubble map, state rankings, and charging density bottlenecks. |
| **Page 5** | `5_Data_Explorer.py` | Searchable tables, null auditing, descriptive statistics, and one-click CSV export. |
| **Page 6** | `6_Machine_Learning_Lab.py` | Multi-algorithm holdout benchmarks, feature importances, and What-If simulator. |
| **Page 7** | `7_Case_Studies.py` | 3 empirical case studies with research questions, methodology, and recommendations. |
| **Page 8** | `8_Market_Insights.py` | Dynamic automated heuristic insights derived directly from data (Zero Hardcoding). |
| **Page 9** | `9_Methodology_and_Sources.py` | Dataset provenance catalog, mathematical formulations, and project limitations. |

---

## 🤖 Machine Learning Benchmark Results

Models were evaluated using a strict **chronological hold-out test split (20%)** on monthly Indian EV registration series:

| Algorithm | R² Score | MAE (Units) | RMSE (Units) | MAPE (%) | Model Ranking |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Linear Regression** | **0.6715** | **11,737** | **16,710** | **5.40%** | 🥇 **Rank #1 (Best)** |
| **Ridge Regression** | **0.6112** | **13,380** | **18,177** | **6.20%** | 🥈 **Rank #2** |
| **Gradient Boosting Regressor** | -0.8564 | 33,916 | 39,721 | 15.86% | 🥉 **Rank #3** |
| **Random Forest Regressor** | -1.4118 | 38,492 | 45,275 | 17.88% | 🏅 **Rank #4** |

### 🎓 Academic Defense Note: Why Linear Models Excel Here
> **Professor Question**: *"Why does Linear Regression outperform Random Forest and Gradient Boosting on this time series?"*  
> **Answer**: Decision trees partition feature space using orthogonal cuts and predict constant leaf averages; they **cannot extrapolate trends above the maximum value observed in training data**. In secular growth markets with strong positive momentum (Indian EV adoption has a 62% 5-year CAGR), tree models flatten out at the training ceiling, whereas linear models properly extrapolate the growth slope.

---

## 🧪 Automated Testing & Verification

Run the comprehensive automated test suite with pytest:

```powershell
pytest tests/test_pipeline.py -v
```

### Verified Test Cases:
- `test_processed_datasets_exist`: Confirms all 4 core processed database tables exist and are populated.
- `test_data_validator_integrity`: Confirms automated schema profiling and integrity scoring (>90%).
- `test_executive_kpis`: Validates cumulative sales (>1M units), positive CAGR, and charger counts.
- `test_cagr_and_hhi_math`: Mathematically checks compound growth and HHI concentration formulas.
- `test_ml_model_training_and_metrics`: Validates holdout train-test split, RMSE, MAE, and R² logging.
- `test_ml_future_forecast_generation`: Confirms 12-month multi-step forward forecasting across Bull, Base, and Bear corridors.
- `test_automated_insight_engine`: Confirms dynamic text generation with actionable takeaways.

---

## 📂 Project Directory Structure

```
EVision/
│
├── app.py                         # Main Executive Gateway & Dashboard Home
├── requirements.txt               # Production Python dependencies
├── README.md                      # Comprehensive Technical Documentation
├── .env.example                   # API Token Configuration Template
│
├── data/
│   ├── raw/                       # Genuine CSV datasets & provenance metadata
│   │   ├── vahan_monthly_ev_registrations.csv
│   │   ├── vahan_statewise_ev_data.csv
│   │   ├── ev_oem_market_share.csv
│   │   ├── global_ev_comparison_iea.csv
│   │   ├── battery_cost_and_fuel_economics.csv
│   │   └── dataset_provenance.json
│   ├── processed/                 # Enriched, cleaned datasets
│   └── cache/                     # SQLite persistence (emi_intelligence.db)
│
├── src/
│   ├── __init__.py
│   ├── database.py                # SQLite persistence, audit logging, metrics tracking
│   ├── data_collection.py         # Live ingestion, ping check, fallback engine
│   ├── data_validation.py         # Data quality profiling & schema validation
│   ├── preprocessing.py           # Cleaning, normalization, and metrics enrichment
│   ├── feature_engineering.py     # Backward lags, rolling windows, cyclical encodings
│   ├── analysis.py                # Statistical KPI calculations, CAGR, and HHI
│   ├── forecasting.py             # ML models, holdout benchmarking, horizon forecasts
│   ├── insights.py                # Automated dynamic data-driven insight engine
│   ├── visualization.py           # Reusable dark-mode Plotly chart builders
│   └── ui_components.py           # CSS injection, metric cards, shared sidebar
│
├── pages/
│   ├── 1_Executive_Dashboard.py
│   ├── 2_Live_Market_Monitor.py
│   ├── 3_Market_Analytics.py
│   ├── 4_Geographical_Intelligence.py
│   ├── 5_Data_Explorer.py
│   ├── 6_Machine_Learning_Lab.py
│   ├── 7_Case_Studies.py
│   ├── 8_Market_Insights.py
│   └── 9_Methodology_and_Sources.py
│
├── assets/
│   └── custom.css                 # Enterprise dark-theme CSS styling
│
└── tests/
    ├── test_pipeline.py           # Pytest automated test suite
    └── verify_all_pages.py        # Top-to-bottom runpy verification script
```

---

## 🎓 Viva Voce & Presentation Defense Guide

### 1. Problem Statement & Motivation
India is experiencing a massive mobility transition driven by high fuel costs, national decarbonization commitments (Net Zero 2070), and central subsidies (FAME II / PM E-DRIVE). However, stakeholders (automakers, investors, DISCOMs) lack a unified intelligence platform that merges real-world registration records with predictive machine learning and spatial charging infrastructure analysis.

### 2. Real Data Authenticity
All datasets are compiled directly from official sources:
- **MoRTH VAHAN Registry**: 90 consecutive monthly observations (2018–2025) categorized across Two-Wheelers, Three-Wheelers, Four-Wheelers, and Buses.
- **Bureau of Energy Efficiency (BEE)**: 36 States & UTs with operational public charging stations (PCS) and spatial coordinates.
- **FADA**: Retail market shares for leading OEMs (Tata Motors, MG, Mahindra, Ola, TVS, Bajaj).
- **BloombergNEF / IEA**: Historical lithium-ion battery pack prices ($181 to $98/kWh).

### 3. Dynamic Insight Generation (Zero Hardcoding)
The insight engine computes observations directly from the loaded dataframe at runtime:
- Identifies the dominant category (Two-Wheelers at 53.1%).
- Flags state-level charging bottlenecks (Uttar Pradesh at 675 EVs per public charger).
- Evaluates four-wheeler market concentration (Tata Motors 67.2% share yielding HHI > 4,900).
- Calculates commuter financial arbitrage (₹2.10/km operational savings for 2W commuters).

---
*Electric Market Intelligence (EMI) — Developed for Academic Capstone & Technical Viva Presentation.*

