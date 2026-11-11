"""
ELECTRIC MARKET INTELLIGENCE (EMI)
Data Cleaning & Preprocessing Pipeline
"""

import os
import sys
import pandas as pd
import numpy as np

# Ensure root directory is on path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.database import save_dataframe, log_sync_event

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROC_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

def clean_monthly_registrations() -> pd.DataFrame:
    raw_path = os.path.join(RAW_DIR, "vahan_monthly_ev_registrations.csv")
    if not os.path.exists(raw_path):
        from src.generate_authentic_datasets import generate_datasets
        generate_datasets()
        
    df = pd.read_csv(raw_path)
    
    # Date formatting & type normalization
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    
    # Ensure numeric types
    num_cols = ["Two_Wheeler", "Three_Wheeler", "Four_Wheeler", "Bus", "Commercial_Others", "Total_EV_Sales", "Total_Vehicle_Sales"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        
    # Re-calculate totals and percentages for precision
    df["Total_EV_Sales"] = df["Two_Wheeler"] + df["Three_Wheeler"] + df["Four_Wheeler"] + df["Bus"] + df["Commercial_Others"]
    df["EV_Penetration_Rate_Pct"] = round((df["Total_EV_Sales"] / df["Total_Vehicle_Sales"]) * 100, 3)
    
    # Category share breakdowns
    df["2W_Share_Pct"] = round((df["Two_Wheeler"] / df["Total_EV_Sales"]) * 100, 2)
    df["3W_Share_Pct"] = round((df["Three_Wheeler"] / df["Total_EV_Sales"]) * 100, 2)
    df["4W_Share_Pct"] = round((df["Four_Wheeler"] / df["Total_EV_Sales"]) * 100, 2)
    df["Bus_Share_Pct"] = round((df["Bus"] / df["Total_EV_Sales"]) * 100, 2)
    
    # Cumulative adoptions
    df["Cumulative_EV_Sales"] = df["Total_EV_Sales"].cumsum()
    df["Cumulative_2W"] = df["Two_Wheeler"].cumsum()
    df["Cumulative_4W"] = df["Four_Wheeler"].cumsum()
    
    # MoM and YoY calculations
    df["MoM_Growth_Pct"] = round(df["Total_EV_Sales"].pct_change() * 100, 2).fillna(0.0)
    df["YoY_Growth_Pct"] = round(df["Total_EV_Sales"].pct_change(12) * 100, 2).fillna(0.0)
    
    # Save to processed and database
    out_path = os.path.join(PROC_DIR, "cleaned_monthly_ev_registrations.csv")
    os.makedirs(PROC_DIR, exist_ok=True)
    df.to_csv(out_path, index=False)
    save_dataframe("cleaned_monthly_ev_registrations", df)
    log_sync_event("cleaned_monthly_ev_registrations", "PROCESSED", len(df), "Cleaned and enriched time series")
    
    return df

def clean_statewise_data() -> pd.DataFrame:
    raw_path = os.path.join(RAW_DIR, "vahan_statewise_ev_data.csv")
    df = pd.read_csv(raw_path)
    
    # Standardize string fields
    df["State"] = df["State"].str.strip()
    df["State_Code"] = df["State_Code"].str.strip().str.upper()
    df["Region"] = df["Region"].str.strip()
    
    # Numeric sanitization
    num_cols = ["Two_Wheeler", "Three_Wheeler", "Four_Wheeler", "Bus", "Public_Charging_Stations", "Population_M"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        
    df["Total_EV_Registrations"] = df["Two_Wheeler"] + df["Three_Wheeler"] + df["Four_Wheeler"] + df["Bus"]
    df["EVs_Per_Public_Charger"] = round(df["Total_EV_Registrations"] / df["Public_Charging_Stations"].replace(0, 1), 1)
    df["National_Share_Pct"] = round((df["Total_EV_Registrations"] / df["Total_EV_Registrations"].sum()) * 100, 2)
    
    # Charging Infrastructure Adequacy Score (1-10)
    # Target benchmark: 1 public charger per 20 EVs
    df["Charging_Adequacy_Score"] = round(np.clip(10.0 - (df["EVs_Per_Public_Charger"] / 30.0), 1.0, 10.0), 1)
    
    out_path = os.path.join(PROC_DIR, "cleaned_statewise_ev_data.csv")
    df.to_csv(out_path, index=False)
    save_dataframe("cleaned_statewise_ev_data", df)
    log_sync_event("cleaned_statewise_ev_data", "PROCESSED", len(df), "Cleaned statewise registrations and infrastructure")
    return df

def clean_oem_data() -> pd.DataFrame:
    raw_path = os.path.join(RAW_DIR, "ev_oem_market_share.csv")
    df = pd.read_csv(raw_path)
    
    df["Segment"] = df["Segment"].str.strip()
    df["OEM"] = df["OEM"].str.strip()
    df["Sales_Units"] = pd.to_numeric(df["Sales_Units"], errors="coerce").fillna(0).astype(int)
    df["Market_Share_Pct"] = pd.to_numeric(df["Market_Share_Pct"], errors="coerce").fillna(0.0)
    
    out_path = os.path.join(PROC_DIR, "cleaned_oem_market_share.csv")
    df.to_csv(out_path, index=False)
    save_dataframe("cleaned_oem_market_share", df)
    log_sync_event("cleaned_oem_market_share", "PROCESSED", len(df), "Cleaned OEM market shares")
    return df

def clean_global_data() -> pd.DataFrame:
    raw_path = os.path.join(RAW_DIR, "global_ev_comparison_iea.csv")
    df = pd.read_csv(raw_path)
    out_path = os.path.join(PROC_DIR, "cleaned_global_ev_comparison.csv")
    df.to_csv(out_path, index=False)
    save_dataframe("cleaned_global_ev_comparison", df)
    return df

def clean_economic_data() -> pd.DataFrame:
    raw_path = os.path.join(RAW_DIR, "battery_cost_and_fuel_economics.csv")
    df = pd.read_csv(raw_path)
    
    # Running cost comparison calculations
    # 2W ICE: 40 km/l @ petrol price -> cost/km = petrol_price / 40
    # 2W EV: 3 kWh/100 km @ electricity tariff -> cost/km = 0.03 * electricity_cost
    df["2W_ICE_Cost_Per_Km_INR"] = round(df["Petrol_Price_INR_per_L"] / 45.0, 2)
    df["2W_EV_Cost_Per_Km_INR"] = round((3.0 / 100.0) * df["Electricity_Cost_INR_per_kWh"], 2)
    df["2W_Savings_Per_Km_INR"] = round(df["2W_ICE_Cost_Per_Km_INR"] - df["2W_EV_Cost_Per_Km_INR"], 2)
    
    # 4W ICE: 14 km/l
    # 4W EV: 16 kWh/100 km
    df["4W_ICE_Cost_Per_Km_INR"] = round(df["Petrol_Price_INR_per_L"] / 14.0, 2)
    df["4W_EV_Cost_Per_Km_INR"] = round((16.0 / 100.0) * df["Electricity_Cost_INR_per_kWh"], 2)
    df["4W_Savings_Per_Km_INR"] = round(df["4W_ICE_Cost_Per_Km_INR"] - df["4W_EV_Cost_Per_Km_INR"], 2)
    
    out_path = os.path.join(PROC_DIR, "cleaned_economic_data.csv")
    df.to_csv(out_path, index=False)
    save_dataframe("cleaned_economic_data", df)
    return df

def run_preprocessing_pipeline():
    print("[INFO] Executing complete preprocessing pipeline...")
    df_m = clean_monthly_registrations()
    df_s = clean_statewise_data()
    df_o = clean_oem_data()
    df_g = clean_global_data()
    df_e = clean_economic_data()
    print("[SUCCESS] All datasets processed and loaded into SQLite persistent store.")
    return df_m, df_s, df_o, df_g, df_e

if __name__ == "__main__":
    from src.database import init_db
    init_db()
    run_preprocessing_pipeline()
