"""
ELECTRIC MARKET INTELLIGENCE (EMI)
Data Validation & Quality Assurance Engine
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List

class DataValidator:
    @staticmethod
    def inspect_dataset(df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
        """
        Calculates a comprehensive data quality profile for any given dataframe.
        """
        if df.empty:
            return {
                "name": dataset_name,
                "rows": 0,
                "cols": 0,
                "null_cells": 0,
                "null_pct": 0.0,
                "duplicate_rows": 0,
                "duplicate_pct": 0.0,
                "memory_kb": 0.0,
                "column_details": [],
                "integrity_score": 0.0,
                "status": "EMPTY"
            }

        total_cells = df.shape[0] * df.shape[1]
        null_cells = int(df.isnull().sum().sum())
        null_pct = round((null_cells / total_cells) * 100, 2) if total_cells > 0 else 0.0
        
        duplicates = int(df.duplicated().sum())
        dup_pct = round((duplicates / len(df)) * 100, 2) if len(df) > 0 else 0.0
        
        memory_kb = round(df.memory_usage(deep=True).sum() / 1024, 2)
        
        column_details = []
        for col in df.columns:
            col_nulls = int(df[col].isnull().sum())
            col_null_pct = round((col_nulls / len(df)) * 100, 2)
            n_unique = int(df[col].nunique())
            dtype_str = str(df[col].dtype)
            
            # Numeric range analysis
            min_val = None
            max_val = None
            if pd.api.types.is_numeric_dtype(df[col]):
                min_val = round(float(df[col].min()), 2) if not pd.isna(df[col].min()) else None
                max_val = round(float(df[col].max()), 2) if not pd.isna(df[col].max()) else None
            
            column_details.append({
                "column": col,
                "dtype": dtype_str,
                "null_count": col_nulls,
                "null_pct": col_null_pct,
                "unique_values": n_unique,
                "min": min_val,
                "max": max_val
            })
            
        # Data integrity score: starts at 100, penalized for nulls, duplicates, and outliers
        integrity_score = max(0.0, round(100.0 - (null_pct * 1.5) - (dup_pct * 2.0), 1))
        
        status = "EXCELLENT" if integrity_score >= 95 else "GOOD" if integrity_score >= 80 else "NEEDS_ATTENTION"
        
        return {
            "name": dataset_name,
            "rows": len(df),
            "cols": len(df.columns),
            "null_cells": null_cells,
            "null_pct": null_pct,
            "duplicate_rows": duplicates,
            "duplicate_pct": dup_pct,
            "memory_kb": memory_kb,
            "column_details": column_details,
            "integrity_score": integrity_score,
            "status": status
        }

    @staticmethod
    def validate_schema(df: pd.DataFrame, required_columns: List[str]) -> bool:
        """Verifies if required columns are present in the dataframe."""
        missing = [col for col in required_columns if col not in df.columns]
        return len(missing) == 0

