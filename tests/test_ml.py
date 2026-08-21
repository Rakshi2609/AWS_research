"""
Unit tests for ML preprocessing, model inference, and explainability.
"""
import pytest
import numpy as np
from app.ml.preprocessing import preprocess_reading_dict
from app.ml.predict import predictor
from app.features.fusion import TARGET_CLASSES


def test_preprocessing_imputation():
    # Reading with missing fields and NaN
    incomplete_reading = {
        "air_temperature": 30.0,
        "relative_humidity": float("nan"),
        "soil_moisture_15": None,
    }
    cleaned = preprocess_reading_dict(incomplete_reading)
    assert cleaned["relative_humidity"] == 60.0  # Default imputed
    assert cleaned["soil_moisture_15"] == 28.0   # Default imputed
    assert "vpd" in cleaned
    assert "cwsi" in cleaned


def test_predictor_inference():
    predictor.load_model()
    
    # Healthy profile
    healthy_reading = {
        "air_temperature": 28.0,
        "relative_humidity": 65.0,
        "leaf_temperature": 26.5,
        "solar_radiation": 600.0,
        "soil_moisture_15": 34.0,
        "soil_moisture_30": 36.0,
        "soil_moisture_60": 38.0,
        "soil_temperature": 24.0,
        "electrical_conductivity": 1.4,
        "wind_speed": 2.0,
        "sap_flow": 0.95,
        "red": 0.05,
        "red_edge": 0.20,
        "nir": 0.75
    }
    res = predictor.predict(healthy_reading)
    assert res["prediction"] in TARGET_CLASSES
    assert 0.0 <= res["confidence"] <= 1.0
    assert sum(res["probabilities"].values()) == pytest.approx(1.0, abs=0.01)
    assert len(res["contributing_signals"]) > 0
    assert res["features"]["vpd"] > 0.0


def test_water_stress_prediction():
    predictor.load_model()
    
    # Water stress profile (low moisture, high leaf temp, low sap flow)
    water_stress_reading = {
        "air_temperature": 32.0,
        "relative_humidity": 45.0,
        "leaf_temperature": 36.5,
        "solar_radiation": 800.0,
        "soil_moisture_15": 11.0,
        "soil_moisture_30": 14.0,
        "soil_moisture_60": 17.0,
        "soil_temperature": 29.0,
        "electrical_conductivity": 1.6,
        "wind_speed": 2.5,
        "sap_flow": 0.12,
        "red": 0.14,
        "red_edge": 0.28,
        "nir": 0.45
    }
    res = predictor.predict(water_stress_reading)
    assert res["prediction"] == "Water Stress"
    assert res["probabilities"]["Water Stress"] >= 0.70
