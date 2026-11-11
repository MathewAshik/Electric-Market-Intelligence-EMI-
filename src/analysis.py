"""
ELECTRIC MARKET INTELLIGENCE (EMI)
Advanced Statistical and Market Analytics Engine
"""

import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, Any, List

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.database import load_dataframe

def calculate_cagr(start_value: float, end_value: float, periods: float) -> float:
    """Calculates Compound Annual Growth Rate (%)"""
    if start_value <= 0 or periods <= 0:
        return 0.0
    return round((((end_value / start_value) ** (1.0 / periods)) - 1.0) * 100, 2)

def calculate_hhi(market_shares: List[float]) -> Dict[str, Any]:
    """
    Computes Herfindahl-Hirschman Index (HHI) for market concentration.
    HHI = sum(market_share_pct ^ 2)
    """
    clean_shares = [s for s in market_shares if s > 0]
    hhi = round(sum([s ** 2 for s in clean_shares]), 1)
    
    if hhi > 2500:
        classification = "Highly Concentrated (Dominant Monopolistic / Duopolistic Control)"
        risk = "HIGH"
    elif hhi >= 1500:
        classification = "Moderately Concentrated (Competitive Oligopoly)"
        risk = "MEDIUM"
    else:
        classification = "Unconcentrated (Highly Competitive Fragmented Market)"
        risk = "LOW"
        
    return {
        "hhi_index": hhi,
        "classification": classification,
        "concentration_risk": risk
    }

def get_executive_kpis(df_monthly: pd.DataFrame = None, df_states: pd.DataFrame = None) -> Dict[str, Any]:
    """Calculates top-level executive KPIs for the market dashboard."""
    if df_monthly is None or df_monthly.empty:
        df_monthly = load_dataframe("cleaned_monthly_ev_registrations")
    if df_states is None or df_states.empty:
        df_states = load_dataframe("cleaned_statewise_ev_data")

    total_evs_sold = int(df_monthly["Total_EV_Sales"].sum())
    total_2w = int(df_monthly["Two_Wheeler"].sum())
    total_4w = int(df_monthly["Four_Wheeler"].sum())
    
    latest_row = df_monthly.iloc[-1]
    prev_month_row = df_monthly.iloc[-2] if len(df_monthly) > 1 else latest_row
    prev_year_row = df_monthly.iloc[-13] if len(df_monthly) >= 13 else latest_row
    
    latest_monthly_sales = int(latest_row["Total_EV_Sales"])
    mom_growth = round(((latest_monthly_sales - prev_month_row["Total_EV_Sales"]) / prev_month_row["Total_EV_Sales"]) * 100, 2)
    yoy_growth = round(((latest_monthly_sales - prev_year_row["Total_EV_Sales"]) / prev_year_row["Total_EV_Sales"]) * 100, 2)
    
    ev_penetration_current = round(float(latest_row["EV_Penetration_Rate_Pct"]), 2)
    
    # Infrastructure & Environmental stats
    total_chargers = int(df_states["Public_Charging_Stations"].sum()) if not df_states.empty else 28500
    national_ev_to_charger_ratio = round(total_evs_sold / max(1, total_chargers), 1)
    
    # CO2 calculation: ~1.8 kg CO2 saved per liter petrol displaced
    # Avg EV travels 10,000 km/yr, replacing ~250-400L of fossil fuel
    # Fleet cumulative CO2 emissions avoided in Metric Tons:
    total_co2_saved_mt = round((total_evs_sold * 0.85) / 1000.0, 2)
    
    # 5-Year CAGR (2019 to 2024 annual total)
    sales_2019 = df_monthly[df_monthly["Year"] == 2019]["Total_EV_Sales"].sum()
    sales_2024 = df_monthly[df_monthly["Year"] == 2024]["Total_EV_Sales"].sum()
    cagr_5yr = calculate_cagr(sales_2019, sales_2024, 5)

    return {
        "total_evs_sold": total_evs_sold,
        "total_2w": total_2w,
        "total_4w": total_4w,
        "latest_month_sales": latest_monthly_sales,
        "latest_month_name": f"{latest_row['Month_Name']} {latest_row['Year']}",
        "mom_growth_pct": mom_growth,
        "yoy_growth_pct": yoy_growth,
        "ev_penetration_current_pct": ev_penetration_current,
        "total_public_chargers": total_chargers,
        "national_ev_to_charger_ratio": national_ev_to_charger_ratio,
        "total_co2_saved_mt": total_co2_saved_mt,
        "cagr_5yr_pct": cagr_5yr
    }

def get_state_analytics(df_states: pd.DataFrame = None) -> Dict[str, Any]:
    """Generates ranking and geographical analytics."""
    if df_states is None or df_states.empty:
        df_states = load_dataframe("cleaned_statewise_ev_data")
        
    top_volume_states = df_states.sort_values("Total_EV_Registrations", ascending=False).head(10)
    top_penetration_states = df_states.sort_values("EV_Penetration_Pct", ascending=False).head(10)
    charging_bottlenecks = df_states.sort_values("EVs_Per_Public_Charger", ascending=False).head(10)
    
    region_summary = df_states.groupby("Region").agg({
        "Total_EV_Registrations": "sum",
        "Public_Charging_Stations": "sum",
        "Population_M": "sum"
    }).reset_index()
    region_summary["Regional_EV_Share_Pct"] = round(
        (region_summary["Total_EV_Registrations"] / region_summary["Total_EV_Registrations"].sum()) * 100, 2
    )
    region_summary["Regional_EVs_Per_Charger"] = round(
        region_summary["Total_EV_Registrations"] / region_summary["Public_Charging_Stations"], 1
    )
    
    return {
        "top_volume_states": top_volume_states,
        "top_penetration_states": top_penetration_states,
        "charging_bottlenecks": charging_bottlenecks,
        "region_summary": region_summary
    }

def compute_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Computes correlation across relevant numerical parameters."""
    cols = [
        "Total_EV_Sales", "Two_Wheeler", "Four_Wheeler", "EV_Penetration_Rate_Pct",
        "Battery_Pack_USD_per_kWh", "Petrol_Price_INR_per_L", "Electricity_Cost_INR_per_kWh"
    ]
    available_cols = [c for c in cols if c in df.columns]
    corr_df = df[available_cols].corr().round(3)
    return corr_df

if __name__ == "__main__":
    kpis = get_executive_kpis()
    print("[SUCCESS] Calculated Executive KPIs:")
    for k, v in kpis.items():
        print(f"  {k}: {v}")

