"""
ELECTRIC MARKET INTELLIGENCE (EMI)
Database Persistence Layer (SQLite & Parquet Cache)
"""

import os
import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cache", "emi_intelligence.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Audit log table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sync_audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        source_name TEXT NOT NULL,
        status TEXT NOT NULL,
        records_count INTEGER,
        details TEXT
    )
    """)
    
    # Model evaluation history log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS model_metrics_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        model_name TEXT NOT NULL,
        target_variable TEXT NOT NULL,
        r2_score REAL,
        mae REAL,
        rmse REAL,
        mape REAL
    )
    """)
    
    conn.commit()
    conn.close()

def save_dataframe(table_name: str, df: pd.DataFrame):
    conn = get_connection()
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()

def load_dataframe(table_name: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def log_sync_event(source_name: str, status: str, records_count: int = 0, details: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO sync_audit_log (timestamp, source_name, status, records_count, details)
    VALUES (?, ?, ?, ?, ?)
    """, (now_str, source_name, status, records_count, details))
    conn.commit()
    conn.close()

def get_recent_sync_events(limit: int = 10) -> pd.DataFrame:
    conn = get_connection()
    try:
        df = pd.read_sql_query(
            f"SELECT timestamp, source_name, status, records_count, details FROM sync_audit_log ORDER BY id DESC LIMIT {limit}",
            conn
        )
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def log_model_metrics(model_name: str, target: str, r2: float, mae: float, rmse: float, mape: float):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO model_metrics_log (timestamp, model_name, target_variable, r2_score, mae, rmse, mape)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (now_str, model_name, target, r2, mae, rmse, mape))
    conn.commit()
    conn.close()

def get_model_metrics_history() -> pd.DataFrame:
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM model_metrics_log ORDER BY id DESC", conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

