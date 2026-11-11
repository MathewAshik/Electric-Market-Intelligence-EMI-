"""
ELECTRIC MARKET INTELLIGENCE (EMI)
Machine Learning Lab & Time-Series Predictive Intelligence Engine
"""

import os
import sys
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List

from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score, mean_absolute_percentage_error

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.feature_engineering import build_ml_feature_matrix
from src.database import log_model_metrics

class EVMarketPredictor:
    def __init__(self, target_col: str = "Total_EV_Sales"):
        self.target_col = target_col
        self.feature_cols = [
            "Time_Index", "Time_Index_Squared", "Month_Sin", "Month_Cos",
            "Is_Q1", "Is_Q2", "Is_Q3", "Is_Q4", "Is_Festive_Season", "Is_Fiscal_Year_End",
            "lag_1m_Total_Sales", "lag_2m_Total_Sales", "lag_3m_Total_Sales", "lag_12m_Total_Sales",
            "rolling_mean_3m", "rolling_mean_6m", "rolling_std_3m",
            "Battery_Pack_USD_per_kWh", "Petrol_Price_INR_per_L"
        ]
        self.models = {
            "Linear Regression": LinearRegression(),
            "Ridge Regression": Ridge(alpha=1.0),
            "Random Forest Regressor": RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42),
            "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=100, learning_rate=0.08, max_depth=4, random_state=42)
        }
        self.trained_models = {}
        self.evaluation_results = {}
        self.best_model_name = None
        self.train_df = None
        self.test_df = None

    def prepare_data(self, test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df = build_ml_feature_matrix()
        
        # Ensure selected feature columns exist
        available_features = [c for c in self.feature_cols if c in df.columns]
        self.feature_cols = available_features
        
        # Temporal chronological split (NO data leakage)
        split_idx = int(len(df) * (1 - test_size))
        self.train_df = df.iloc[:split_idx].copy()
        self.test_df = df.iloc[split_idx:].copy()
        
        return self.train_df, self.test_df

    def train_and_evaluate_all(self, test_size: float = 0.2) -> pd.DataFrame:
        """Trains all candidate models, evaluates on the hold-out test set, and logs metrics."""
        self.prepare_data(test_size=test_size)
        
        X_train = self.train_df[self.feature_cols]
        y_train = self.train_df[self.target_col]
        X_test = self.test_df[self.feature_cols]
        y_test = self.test_df[self.target_col]
        
        results = []
        best_rmse = float("inf")
        
        for name, model in self.models.items():
            model.fit(X_train, y_train)
            self.trained_models[name] = model
            
            y_pred = model.predict(X_test)
            # Clip negative predictions if any
            y_pred = np.clip(y_pred, a_min=0, a_max=None)
            
            mae = float(mean_absolute_error(y_test, y_pred))
            rmse = float(root_mean_squared_error(y_test, y_pred))
            r2 = float(r2_score(y_test, y_pred))
            mape = float(mean_absolute_percentage_error(y_test, y_pred) * 100)
            
            self.evaluation_results[name] = {
                "mae": round(mae, 1),
                "rmse": round(rmse, 1),
                "r2": round(r2, 4),
                "mape": round(mape, 2),
                "y_pred": y_pred,
                "y_test": y_test.values,
                "test_dates": self.test_df["Date"].values
            }
            
            # Log to SQLite
            log_model_metrics(name, self.target_col, r2, mae, rmse, mape)
            
            if rmse < best_rmse:
                best_rmse = rmse
                self.best_model_name = name
                
            results.append({
                "Algorithm": name,
                "R² Score": round(r2, 4),
                "MAE (Units)": f"{int(mae):,}",
                "RMSE (Units)": f"{int(rmse):,}",
                "MAPE (%)": f"{round(mape, 2)}%",
                "Rank": 0
            })
            
        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values("R² Score", ascending=False).reset_index(drop=True)
        df_results["Rank"] = [f"#{i+1}" for i in range(len(df_results))]
        
        return df_results

    def get_feature_importances(self, model_name: str = None) -> pd.DataFrame:
        """Returns sorted feature importance or coefficients."""
        if not model_name:
            model_name = self.best_model_name or "Random Forest Regressor"
            
        model = self.trained_models.get(model_name)
        if model is None:
            return pd.DataFrame()
            
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            metric_type = "Gini Importance"
        elif hasattr(model, "coef_"):
            importances = np.abs(model.coef_)
            metric_type = "Absolute Coefficient"
        else:
            return pd.DataFrame()
            
        df_imp = pd.DataFrame({
            "Feature": self.feature_cols,
            "Importance": importances
        }).sort_values("Importance", ascending=False).reset_index(drop=True)
        df_imp["Relative_Weight_Pct"] = round((df_imp["Importance"] / df_imp["Importance"].sum()) * 100, 2)
        return df_imp

    def generate_future_forecast(self, horizon_months: int = 24, model_name: str = None) -> pd.DataFrame:
        """
        Performs iterative multi-step forward forecasting across user-specified horizon.
        Includes Base, Bull (+15%), and Bear (-15%) scenarios.
        """
        if not model_name:
            model_name = self.best_model_name or "Gradient Boosting Regressor"
        model = self.trained_models.get(model_name)
        
        df = build_ml_feature_matrix()
        last_date = pd.to_datetime(df["Date"].iloc[-1])
        last_idx = df["Time_Index"].iloc[-1]
        
        current_battery_cost = float(df["Battery_Pack_USD_per_kWh"].iloc[-1])
        current_petrol_price = float(df["Petrol_Price_INR_per_L"].iloc[-1])
        
        forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=horizon_months, freq="MS")
        
        # Rolling buffers
        recent_sales = list(df["Total_EV_Sales"].values)
        
        forecasts = []
        for i, dt in enumerate(forecast_dates):
            t_idx = last_idx + i + 1
            month = dt.month
            quarter = f"Q{(month-1)//3 + 1}"
            
            # Projected gradual battery pack cost decline (~5% per year)
            proj_battery_cost = max(65.0, current_battery_cost * (0.95 ** ((i + 1) / 12.0)))
            # Projected moderate petrol inflation (~2% per year)
            proj_petrol = current_petrol_price * (1.02 ** ((i + 1) / 12.0))
            
            row_features = {
                "Time_Index": t_idx,
                "Time_Index_Squared": t_idx ** 2,
                "Month_Sin": np.sin(2 * np.pi * month / 12.0),
                "Month_Cos": np.cos(2 * np.pi * month / 12.0),
                "Is_Q1": 1 if quarter == "Q1" else 0,
                "Is_Q2": 1 if quarter == "Q2" else 0,
                "Is_Q3": 1 if quarter == "Q3" else 0,
                "Is_Q4": 1 if quarter == "Q4" else 0,
                "Is_Festive_Season": 1 if month in [10, 11] else 0,
                "Is_Fiscal_Year_End": 1 if month == 3 else 0,
                "lag_1m_Total_Sales": recent_sales[-1],
                "lag_2m_Total_Sales": recent_sales[-2],
                "lag_3m_Total_Sales": recent_sales[-3],
                "lag_12m_Total_Sales": recent_sales[-12] if len(recent_sales) >= 12 else recent_sales[-1],
                "rolling_mean_3m": np.mean(recent_sales[-3:]),
                "rolling_mean_6m": np.mean(recent_sales[-6:]),
                "rolling_std_3m": np.std(recent_sales[-3:]),
                "Battery_Pack_USD_per_kWh": proj_battery_cost,
                "Petrol_Price_INR_per_L": proj_petrol
            }
            
            feat_df = pd.DataFrame([row_features])[self.feature_cols]
            pred_base = float(model.predict(feat_df)[0])
            pred_base = max(1000, pred_base)
            
            # Scenarios
            pred_bull = int(pred_base * 1.15)
            pred_bear = int(pred_base * 0.85)
            pred_base = int(pred_base)
            
            recent_sales.append(pred_base)
            
            forecasts.append({
                "Date": dt.strftime("%Y-%m-%d"),
                "Year": dt.year,
                "Month": month,
                "Month_Name": dt.strftime("%b"),
                "Forecast_Base_Case": pred_base,
                "Forecast_Bull_Case": pred_bull,
                "Forecast_Bear_Case": pred_bear,
                "Projected_Battery_Cost_USD": round(proj_battery_cost, 1),
                "Projected_Petrol_Price_INR": round(proj_petrol, 1)
            })
            
        return pd.DataFrame(forecasts)

    def predict_single_scenario(self, battery_cost: float, petrol_price: float, month: int, horizon_step: int = 1) -> int:
        """Interactive prediction helper for user custom slider inputs."""
        model = self.trained_models.get(self.best_model_name or "Random Forest Regressor")
        if model is None:
            self.train_and_evaluate_all()
            model = self.trained_models[self.best_model_name]
            
        df = build_ml_feature_matrix()
        recent_sales = list(df["Total_EV_Sales"].values)
        t_idx = df["Time_Index"].iloc[-1] + horizon_step
        quarter = f"Q{(month-1)//3 + 1}"
        
        features = {
            "Time_Index": t_idx,
            "Time_Index_Squared": t_idx ** 2,
            "Month_Sin": np.sin(2 * np.pi * month / 12.0),
            "Month_Cos": np.cos(2 * np.pi * month / 12.0),
            "Is_Q1": 1 if quarter == "Q1" else 0,
            "Is_Q2": 1 if quarter == "Q2" else 0,
            "Is_Q3": 1 if quarter == "Q3" else 0,
            "Is_Q4": 1 if quarter == "Q4" else 0,
            "Is_Festive_Season": 1 if month in [10, 11] else 0,
            "Is_Fiscal_Year_End": 1 if month == 3 else 0,
            "lag_1m_Total_Sales": recent_sales[-1],
            "lag_2m_Total_Sales": recent_sales[-2],
            "lag_3m_Total_Sales": recent_sales[-3],
            "lag_12m_Total_Sales": recent_sales[-12],
            "rolling_mean_3m": np.mean(recent_sales[-3:]),
            "rolling_mean_6m": np.mean(recent_sales[-6:]),
            "rolling_std_3m": np.std(recent_sales[-3:]),
            "Battery_Pack_USD_per_kWh": battery_cost,
            "Petrol_Price_INR_per_L": petrol_price
        }
        
        feat_df = pd.DataFrame([features])[self.feature_cols]
        pred = model.predict(feat_df)[0]
        return int(max(0, pred))

if __name__ == "__main__":
    predictor = EVMarketPredictor()
    results = predictor.train_and_evaluate_all()
    print("[SUCCESS] Machine Learning Benchmark Results:")
    print(results.to_string())
    print(f"\nBest Performing Model: {predictor.best_model_name}")
    
    # Test future forecast
    forecast_df = predictor.generate_future_forecast(horizon_months=12)
    print("\n[SUCCESS] 12-Month Future Forecast Snapshot:")
    print(forecast_df[["Date", "Forecast_Base_Case", "Forecast_Bull_Case", "Forecast_Bear_Case"]].head())
