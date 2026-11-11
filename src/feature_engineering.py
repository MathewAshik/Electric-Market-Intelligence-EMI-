"""
ELECTRIC MARKET INTELLIGENCE (EMI)
Feature Engineering Pipeline
"""

import os
import sys
import pandas as pd
import numpy as np

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.database import load_dataframe, save_dataframe

def build_ml_feature_matrix(df_monthly: pd.DataFrame = None, df_econ: pd.DataFrame = None) -> pd.DataFrame:
    """
    Constructs a feature-rich tabular matrix for Machine Learning and forecasting models.
    Prevents data leakage by strictly computing backward-looking rolling and lag metrics.
    """
    if df_monthly is None:
        df_monthly = load_dataframe("cleaned_monthly_ev_registrations")
    if df_econ is None:
        df_econ = load_dataframe("cleaned_economic_data")
        
    df = df_monthly.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    
    # Merge macroeconomic indicators by Year
    if not df_econ.empty:
        econ_subset = df_econ[["Year", "Battery_Pack_USD_per_kWh", "Petrol_Price_INR_per_L", "Electricity_Cost_INR_per_kWh", "FAME_Subsidy_Outlay_Cr"]]
        df = pd.merge(df, econ_subset, on="Year", how="left")
        # Impute forward for recent months
        df["Battery_Pack_USD_per_kWh"] = df["Battery_Pack_USD_per_kWh"].ffill().bfill()
        df["Petrol_Price_INR_per_L"] = df["Petrol_Price_INR_per_L"].ffill().bfill()
        df["Electricity_Cost_INR_per_kWh"] = df["Electricity_Cost_INR_per_kWh"].ffill().bfill()
        df["FAME_Subsidy_Outlay_Cr"] = df["FAME_Subsidy_Outlay_Cr"].ffill().bfill()
        
    # 1. Cyclical calendar features
    df["Month_Sin"] = np.sin(2 * np.pi * df["Month"] / 12.0)
    df["Month_Cos"] = np.cos(2 * np.pi * df["Month"] / 12.0)
    df["Time_Index"] = np.arange(len(df))
    df["Time_Index_Squared"] = df["Time_Index"] ** 2
    
    # 2. Fiscal year quarter dummy flags
    for q in [1, 2, 3, 4]:
        df[f"Is_Q{q}"] = (df["Quarter"] == f"Q{q}").astype(int)
        
    # Festive season indicator (October-November)
    df["Is_Festive_Season"] = df["Month"].isin([10, 11]).astype(int)
    # Fiscal year end push (March)
    df["Is_Fiscal_Year_End"] = (df["Month"] == 3).astype(int)
    
    # 3. Lag features (Target: Total_EV_Sales)
    for lag in [1, 2, 3, 6, 12]:
        df[f"lag_{lag}m_Total_Sales"] = df["Total_EV_Sales"].shift(lag)
        df[f"lag_{lag}m_2W_Sales"] = df["Two_Wheeler"].shift(lag)
        df[f"lag_{lag}m_4W_Sales"] = df["Four_Wheeler"].shift(lag)
        
    # 4. Rolling statistics (Strictly backward looking to prevent lookahead leakage)
    df["rolling_mean_3m"] = df["Total_EV_Sales"].shift(1).rolling(window=3).mean()
    df["rolling_mean_6m"] = df["Total_EV_Sales"].shift(1).rolling(window=6).mean()
    df["rolling_std_3m"] = df["Total_EV_Sales"].shift(1).rolling(window=3).std().fillna(0)
    df["rolling_max_6m"] = df["Total_EV_Sales"].shift(1).rolling(window=6).max()
    df["rolling_min_6m"] = df["Total_EV_Sales"].shift(1).rolling(window=6).min()
    
    # 5. Economic interaction ratios
    if "Battery_Pack_USD_per_kWh" in df.columns and "Petrol_Price_INR_per_L" in df.columns:
        df["Battery_to_Petrol_Cost_Ratio"] = df["Battery_Pack_USD_per_kWh"] / df["Petrol_Price_INR_per_L"]
        
    # Drop initial rows with NaNs resulting from 12-month lag
    df_clean = df.dropna().reset_index(drop=True)
    
    save_dataframe("ml_feature_matrix", df_clean)
    return df_clean

if __name__ == "__main__":
    matrix = build_ml_feature_matrix()
    print(f"[SUCCESS] ML Feature Matrix created with shape: {matrix.shape}")

