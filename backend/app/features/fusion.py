"""
Sensor Fusion and Feature Extraction Pipeline.

Fuses 11 raw environmental/plant measurements with 4 calculated agronomic indices
into the 15-feature standard vector for ML inference.
"""
from typing import Dict, Any, List, Union, Optional
import numpy as np
from app.features.vpd import calculate_vpd
from app.features.cwsi import calculate_cwsi
from app.features.vegetation import calculate_ndvi, calculate_ndre, estimate_spectral_bands


FEATURE_COLUMNS = [
    "soil_moisture_15",
    "soil_moisture_30",
    "soil_moisture_60",
    "soil_temperature",
    "electrical_conductivity",
    "air_temperature",
    "relative_humidity",
    "solar_radiation",
    "wind_speed",
    "leaf_temperature",
    "sap_flow",
    "vpd",
    "cwsi",
    "ndvi",
    "ndre"
]

TARGET_CLASSES = [
    "Healthy",
    "Water Stress",
    "Nutrient Stress",
    "Disease Stress"
]


def get_feature_names() -> List[str]:
    """Return canonical list of model features."""
    return list(FEATURE_COLUMNS)


def get_target_classes() -> List[str]:
    """Return target classification labels."""
    return list(TARGET_CLASSES)


def extract_derived_features(data: Union[Dict[str, Any], Any]) -> Dict[str, float]:
    """
    Extract all 4 derived features (VPD, CWSI, NDVI, NDRE) from raw sensor readings.
    """
    if hasattr(data, "model_dump"):
        d = data.model_dump()
    elif isinstance(data, dict):
        d = data
    else:
        d = vars(data)

    air_temp = float(d.get("air_temperature", 25.0))
    rel_hum = float(d.get("relative_humidity", 60.0))
    leaf_temp = float(d.get("leaf_temperature", air_temp))
    solar_rad = float(d.get("solar_radiation", 500.0))
    
    # 1. VPD
    vpd = calculate_vpd(air_temp, rel_hum)
    
    # 2. CWSI
    cwsi = calculate_cwsi(leaf_temp, air_temp, vpd, solar_rad)
    
    # 3 & 4. NDVI and NDRE
    red = d.get("red")
    red_edge = d.get("red_edge")
    nir = d.get("nir")
    
    if red is not None and nir is not None:
        ndvi = calculate_ndvi(nir, red)
    else:
        ndvi = float(d.get("ndvi", 0.72))
        
    if red_edge is not None and nir is not None:
        ndre = calculate_ndre(nir, red_edge)
    else:
        ndre = float(d.get("ndre", 0.48))
        
    return {
        "vpd": vpd,
        "cwsi": cwsi,
        "ndvi": round(ndvi, 4),
        "ndre": round(ndre, 4)
    }


def to_feature_dict(sensor_data: Union[Dict[str, Any], Any], derived: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """
    Combines raw sensor data with derived features into a complete 15-feature dictionary.
    """
    if hasattr(sensor_data, "model_dump"):
        d = sensor_data.model_dump()
    elif isinstance(sensor_data, dict):
        d = sensor_data
    else:
        d = vars(sensor_data)
        
    if derived is None:
        derived = extract_derived_features(d)
        
    return {
        "soil_moisture_15": float(d.get("soil_moisture_15", 25.0)),
        "soil_moisture_30": float(d.get("soil_moisture_30", 28.0)),
        "soil_moisture_60": float(d.get("soil_moisture_60", 30.0)),
        "soil_temperature": float(d.get("soil_temperature", 24.0)),
        "electrical_conductivity": float(d.get("electrical_conductivity", 1.2)),
        "air_temperature": float(d.get("air_temperature", 28.0)),
        "relative_humidity": float(d.get("relative_humidity", 60.0)),
        "solar_radiation": float(d.get("solar_radiation", 600.0)),
        "wind_speed": float(d.get("wind_speed", 2.0)),
        "leaf_temperature": float(d.get("leaf_temperature", 28.0)),
        "sap_flow": float(d.get("sap_flow", 0.8)),
        "vpd": float(derived["vpd"]),
        "cwsi": float(derived["cwsi"]),
        "ndvi": float(derived["ndvi"]),
        "ndre": float(derived["ndre"])
    }


def to_feature_vector(feature_dict: Dict[str, float]) -> np.ndarray:
    """
    Convert feature dictionary to a 2D numpy array in exact feature column order for sklearn.
    """
    vector = [float(feature_dict[col]) for col in FEATURE_COLUMNS]
    return np.array(vector).reshape(1, -1)
