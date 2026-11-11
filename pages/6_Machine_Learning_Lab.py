"""
PAGE 6: MACHINE LEARNING LAB
Supervised Regression Benchmarks, Feature Importances, Horizon Forecasting & What-If Simulator
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.ui_components import load_custom_css, render_header, render_sidebar_info
from src.database import load_dataframe
from src.forecasting import EVMarketPredictor
from src.visualization import plot_actual_vs_predicted, plot_future_forecast_fan, apply_chart_styling

st.set_page_config(page_title="Machine Learning Lab | EMI", page_icon="🤖", layout="wide")
load_custom_css()
render_sidebar_info()

render_header("Machine Learning Lab", "Supervised Regression Benchmarking, Time-Series Forecasting & What-If Simulation")

# Model Training Setup
st.subheader("⚙️ Supervised Model Training & Cross-Validation Setup")

c_p1, c_p2 = st.columns([2, 1])
with c_p1:
    target_var = st.selectbox("Select Target Variable for Predictive Modeling:", ["Total_EV_Sales", "Two_Wheeler", "Four_Wheeler"])
with c_p2:
    test_split = st.slider("Chronological Holdout Test Split Ratio:", min_value=0.15, max_value=0.30, value=0.20, step=0.05)

predictor = EVMarketPredictor(target_col=target_var)

with st.spinner("Training models on historical series and computing holdout test metrics..."):
    results_df = predictor.train_and_evaluate_all(test_size=test_split)

# Benchmark Table
st.subheader("🏆 Multi-Algorithm Hold-Out Benchmark Leaderboard")
st.dataframe(results_df, use_container_width=True, hide_index=True)

st.success(f"🌟 **Top Performing Model**: `{predictor.best_model_name}` selected based on lowest hold-out test RMSE.")

st.markdown("---")

# Visual Actual vs Predicted
st.subheader("📈 Actual vs Predicted Hold-Out Validation Plot")

model_choice = st.selectbox("Inspect Fit for Algorithm:", list(predictor.models.keys()), index=0)
eval_data = predictor.evaluation_results.get(model_choice)

if eval_data:
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("Hold-out R² Score", f"{eval_data['r2']}")
    with m_col2:
        st.metric("Mean Absolute Error (MAE)", f"{eval_data['mae']:,} units")
    with m_col3:
        st.metric("Root Mean Squared Error", f"{eval_data['rmse']:,} units")
    with m_col4:
        st.metric("Mean Abs. Percentage Error", f"{eval_data['mape']}%")
        
    fig_eval = plot_actual_vs_predicted(
        dates=eval_data["test_dates"],
        y_true=eval_data["y_test"],
        y_pred=eval_data["y_pred"],
        model_name=model_choice
    )
    st.plotly_chart(fig_eval, use_container_width=True)

st.markdown("---")

# Feature Importance Breakdown
st.subheader("🧠 Algorithmic Feature Importance & Weight Analysis")
col_imp1, col_imp2 = st.columns([3, 2])

with col_imp1:
    df_feat_imp = predictor.get_feature_importances(model_name=model_choice)
    if not df_feat_imp.empty:
        fig_feat = px.bar(
            df_feat_imp.head(10),
            x="Importance",
            y="Feature",
            orientation="h",
            title=f"<b>Top 10 Influential Predictive Signals ({model_choice})</b>",
            color="Importance",
            color_continuous_scale="Teal"
        )
        fig_feat.update_layout(yaxis=dict(autorange="reversed"))
        fig_feat = apply_chart_styling(fig_feat, height=380)
        st.plotly_chart(fig_feat, use_container_width=True)

with col_imp2:
    st.markdown("#### Feature Importance Table")
    if not df_feat_imp.empty:
        st.dataframe(df_feat_imp.head(8)[["Feature", "Relative_Weight_Pct"]], use_container_width=True, hide_index=True)
    st.caption("Backward-looking lag signals (1-month & 12-month YoY) and battery pack prices drive the majority of variance.")

st.markdown("---")

# Long-Horizon Forecasting Section
st.subheader("🔮 Forward Long-Horizon Forecasting (2025 - 2027)")
h_col1, h_col2 = st.columns([1, 3])

with h_col1:
    horizon = st.slider("Select Forecast Horizon (Months):", min_value=6, max_value=36, value=24, step=6)
    forecast_model = st.selectbox("Select Model for Extrapolation:", ["Linear Regression", "Ridge Regression"], index=0)
    
df_forecast = predictor.generate_future_forecast(horizon_months=horizon, model_name=forecast_model)
df_hist = load_dataframe("cleaned_monthly_ev_registrations")

with h_col2:
    fig_fan = plot_future_forecast_fan(df_hist, df_forecast)
    st.plotly_chart(fig_fan, use_container_width=True)

with st.expander("📄 View Future Monthly Projected Volume Table"):
    st.dataframe(df_forecast[["Date", "Forecast_Base_Case", "Forecast_Bull_Case", "Forecast_Bear_Case", "Projected_Battery_Cost_USD", "Projected_Petrol_Price_INR"]], use_container_width=True, hide_index=True)

st.markdown("---")

# Interactive What-If Scenario Simulator
st.subheader("🎛️ Interactive 'What-If' Policy & Economic Scenario Simulator")
st.markdown("Test hypothetical economic shocks and examine predicted single-month registration outcomes:")

sim_col1, sim_col2, sim_col3 = st.columns(3)

with sim_col1:
    sim_battery = st.slider("Hypothetical Battery Pack Price ($/kWh):", min_value=50.0, max_value=200.0, value=95.0, step=5.0)
with sim_col2:
    sim_petrol = st.slider("Hypothetical Petrol Price in India (₹/Litre):", min_value=80.0, max_value=140.0, value=105.0, step=2.5)
with sim_col3:
    sim_month = st.selectbox("Target Month for Prediction:", range(1, 13), format_func=lambda m: pd.to_datetime(f"2026-{m:02d}-01").strftime("%B"), index=2) # March

predicted_units = predictor.predict_single_scenario(
    battery_cost=sim_battery,
    petrol_price=sim_petrol,
    month=sim_month,
    horizon_step=6
)

st.markdown(f"""
<div style="background: linear-gradient(135deg, #151922, #1C2230); border: 1px solid #00F2FE; border-radius: 12px; padding: 22px; text-align: center; margin-top: 15px;">
    <div style="color: #94A3B8; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px;">Model Estimated Monthly EV Registration Volume</div>
    <div style="color: #00F2FE; font-size: 2.5rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; margin: 8px 0;">{predicted_units:,} Units</div>
    <div style="color: #00E676; font-size: 0.9rem;">Simulated under ${sim_battery}/kWh battery cost & ₹{sim_petrol}/L petrol price</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Academic Defense Notes
with st.expander("🎓 Academic Methodology & Modeling Defense Note"):
    st.markdown("""
    ### Machine Learning Architectural Rationale
    1. **Why Linear/Ridge Outperforms Tree Ensembles on Long Horizons**:
       - Tree-based regressors (Random Forest & Gradient Boosting) partition feature space using orthogonal cuts and predict constant leaf averages. Consequently, they **cannot extrapolate trends above the maximum value observed in the training split**.
       - In rapid growth markets like Indian EV adoption (exponential secular CAGR), linear and regularized polynomial basis models successfully extrapolate positive time trajectories.
    2. **Prevention of Data Leakage**:
       - Train-test splits strictly follow chronological ordering (`split_idx = int(len(df) * 0.8)`).
       - Rolling averages (`rolling_mean_3m`, `rolling_mean_6m`) are shifted by 1 period (`.shift(1)`), ensuring current month target values are never present in feature inputs.
    3. **Model Limitations**:
       - Unforeseen policy abrupt shifts (e.g., immediate elimination of subsidies or sudden raw lithium supply embargoes) cannot be captured solely from historical lag correlations.
    """)

