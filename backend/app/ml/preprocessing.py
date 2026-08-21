"""
Data preprocessing, feature validation, and imputation routines.
"""
from typing import Dict, Any, List, Union
import numpy as np
import pandas as pd
from app.features.fusion import FEATURE_COLUMNS, extract_derived_features


DEFAULT_IMPUTATIONS = {
    "soil_moisture_15": 28.0,
    "soil_moisture_30": 30.0,
    "soil_moisture_60": 32.0,
    "soil_temperature": 25.0,
    "electrical_conductivity": 1.2,
    "air_temperature": 28.0,
    "relative_humidity": 60.0,
    "solar_radiation": 500.0,
    "wind_speed": 2.0,
    "leaf_temperature": 28.0,
    "sap_flow": 0.7,
    "vpd": 1.5,
    "cwsi": 0.2,
    "ndvi": 0.70,
    "ndre": 0.45
}


def preprocess_reading_dict(data: Dict[str, Any]) -> Dict[str, float]:
    """
    Sanitize, impute missing values, compute derived features, and ensure valid bounds.
    """
    clean: Dict[str, float] = {}

    # Extract or fallback for raw features
    for col in ["soil_moisture_15", "soil_moisture_30", "soil_moisture_60",
                "soil_temperature", "electrical_conductivity", "air_temperature",
                "relative_humidity", "solar_radiation", "wind_speed",
                "leaf_temperature", "sap_flow"]:
        val = data.get(col)
        if val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
            val = DEFAULT_IMPUTATIONS[col]
        clean[col] = float(val)

    # Compute derived features if not present
    derived = extract_derived_features(data)
    for col in ["vpd", "cwsi", "ndvi", "ndre"]:
        val = data.get(col)
        if val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
            val = derived[col]
        clean[col] = float(val)

    return clean


def prepare_dataset_for_training(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Ensure all required feature columns exist, impute missing values, and extract target.
    """
    df_clean = df.copy()

    # If derived features aren't present in the DataFrame, compute them row-wise
    if "vpd" not in df_clean.columns or "cwsi" not in df_clean.columns:
        derived_records = [extract_derived_features(row.to_dict()) for _, row in df_clean.iterrows()]
        derived_df = pd.DataFrame(derived_records)
        for col in ["vpd", "cwsi", "ndvi", "ndre"]:
            df_clean[col] = derived_df[col]

    # Impute missing values with column medians or agronomic defaults
    for col in FEATURE_COLUMNS:
        if col not in df_clean.columns:
            df_clean[col] = DEFAULT_IMPUTATIONS[col]
        else:
            df_clean[col] = df_clean[col].fillna(DEFAULT_IMPUTATIONS[col])

    X = df_clean[FEATURE_COLUMNS]
    y = df_clean["stress_class"]

    return X, y
