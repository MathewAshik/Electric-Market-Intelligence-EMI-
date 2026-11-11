"""
ELECTRIC MARKET INTELLIGENCE (EMI)
Systematic Automated Test Suite
Verifies data integrity, pipeline execution, metrics calculation, and machine learning models.
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np

# Add project root to path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.database import init_db, load_dataframe
from src.preprocessing import run_preprocessing_pipeline
from src.data_validation import DataValidator
from src.analysis import get_executive_kpis, calculate_cagr, calculate_hhi
from src.forecasting import EVMarketPredictor
from src.insights import AutomatedInsightEngine

@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    """Ensure database and processed datasets are initialized before tests run."""
    init_db()
    run_preprocessing_pipeline()

def test_processed_datasets_exist():
    """Verify that all core processed tables exist and have valid rows."""
    for table in ["cleaned_monthly_ev_registrations", "cleaned_statewise_ev_data", "cleaned_oem_market_share", "cleaned_economic_data"]:
        df = load_dataframe(table)
        assert not df.empty, f"Table {table} is empty!"
        assert len(df) > 0, f"Table {table} has no records!"

def test_data_validator_integrity():
    """Verify that DataValidator calculates accurate quality reports."""
    df_monthly = load_dataframe("cleaned_monthly_ev_registrations")
    report = DataValidator.inspect_dataset(df_monthly, "Monthly Registrations")
    assert report["rows"] == len(df_monthly)
    assert report["cols"] == len(df_monthly.columns)
    assert report["integrity_score"] >= 90.0
    assert report["status"] in ["EXCELLENT", "GOOD"]

def test_executive_kpis():
    """Verify that executive KPIs calculate without error and fall within valid domain ranges."""
    kpis = get_executive_kpis()
    assert kpis["total_evs_sold"] > 1_000_000, "Cumulative EV sales should exceed 1M"
    assert kpis["cagr_5yr_pct"] > 0, "5-year CAGR should be positive"
    assert kpis["ev_penetration_current_pct"] > 0, "EV penetration should be greater than 0"
    assert kpis["total_public_chargers"] > 10_000, "Public charging stations should exceed 10,000"

def test_cagr_and_hhi_math():
    """Verify mathematical calculations for CAGR and HHI."""
    # Doubling in 2 years is ~41.42% CAGR
    cagr = calculate_cagr(100, 200, 2)
    assert 41.0 < cagr < 42.0
    
    # 5 equal players (20% each) -> HHI = 5 * 400 = 2000
    hhi_res = calculate_hhi([20.0, 20.0, 20.0, 20.0, 20.0])
    assert hhi_res["hhi_index"] == 2000.0
    assert "Moderately Concentrated" in hhi_res["classification"]

def test_ml_model_training_and_metrics():
    """Verify that all regression models train, evaluate on holdout set, and return valid R² and RMSE."""
    predictor = EVMarketPredictor(target_col="Total_EV_Sales")
    results_df = predictor.train_and_evaluate_all(test_size=0.2)
    
    assert not results_df.empty
    assert len(results_df) == 4
    assert predictor.best_model_name in predictor.models
    
    # Check that best model achieved acceptable holdout metrics
    best_row = results_df.iloc[0]
    assert best_row["R² Score"] > 0.5, "Best model R² should be greater than 0.5"

def test_ml_future_forecast_generation():
    """Verify that future horizon forecasting generates complete monthly projections."""
    predictor = EVMarketPredictor(target_col="Total_EV_Sales")
    predictor.train_and_evaluate_all()
    forecast_df = predictor.generate_future_forecast(horizon_months=12)
    
    assert len(forecast_df) == 12
    assert "Forecast_Base_Case" in forecast_df.columns
    assert "Forecast_Bull_Case" in forecast_df.columns
    assert "Forecast_Bear_Case" in forecast_df.columns
    # Bull case should exceed base case, which should exceed bear case
    assert (forecast_df["Forecast_Bull_Case"] >= forecast_df["Forecast_Base_Case"]).all()
    assert (forecast_df["Forecast_Base_Case"] >= forecast_df["Forecast_Bear_Case"]).all()

def test_automated_insight_engine():
    """Verify that automated insight engine derives dynamic findings with required fields."""
    engine = AutomatedInsightEngine()
    insights = engine.generate_all_insights()
    
    assert len(insights) >= 4
    for ins in insights:
        assert "title" in ins and len(ins["title"]) > 5
        assert "observation" in ins and len(ins["observation"]) > 20
        assert "actionable_takeaway" in ins
        assert "badge" in ins

