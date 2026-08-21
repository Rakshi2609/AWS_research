"""
Unit tests for agricultural feature engineering calculations.
"""
import pytest
from app.features.vpd import calculate_vpd
from app.features.cwsi import calculate_cwsi
from app.features.vegetation import calculate_ndvi, calculate_ndre, estimate_spectral_bands
from app.features.fusion import extract_derived_features, to_feature_dict, to_feature_vector


def test_vpd_calculation():
    # At 30°C and 50% RH:
    # Saturation VP = 0.61078 * exp(17.27*30 / (30 + 237.3)) ~ 4.246 kPa
    # Actual VP = 4.246 * 0.5 ~ 2.123 kPa
    # VPD ~ 2.12 kPa
    vpd = calculate_vpd(30.0, 50.0)
    assert 2.0 < vpd < 2.3
    
    # 100% RH should give ~0.0 VPD
    assert calculate_vpd(25.0, 100.0) == 0.0
    
    # 0% RH should give full saturation pressure
    vpd_dry = calculate_vpd(25.0, 0.0)
    assert vpd_dry > 3.0


def test_cwsi_calculation():
    # Non-stressed crop: leaf is cooler than air under moderate VPD
    cwsi_low = calculate_cwsi(leaf_temperature=26.0, air_temperature=30.0, vpd=2.0)
    assert 0.0 <= cwsi_low <= 0.25
    
    # Severely stressed crop: leaf temperature is several degrees higher than air
    cwsi_high = calculate_cwsi(leaf_temperature=36.0, air_temperature=30.0, vpd=2.0)
    assert cwsi_high >= 0.70
    
    # Range boundary checks
    assert 0.0 <= calculate_cwsi(20.0, 40.0, 1.0) <= 1.0
    assert 0.0 <= calculate_cwsi(50.0, 20.0, 1.0) <= 1.0


def test_vegetation_indices():
    # Healthy canopy: high NIR (0.7), low Red (0.05) -> NDVI ~ 0.86
    ndvi = calculate_ndvi(nir=0.70, red=0.05)
    assert 0.80 < ndvi < 0.90
    
    # Stressed canopy: low NIR (0.4), high Red (0.2) -> NDVI ~ 0.33
    ndvi_stress = calculate_ndvi(nir=0.40, red=0.20)
    assert 0.25 < ndvi_stress < 0.40
    
    # NDRE calculation
    ndre = calculate_ndre(nir=0.70, red_edge=0.20)
    assert 0.50 < ndre < 0.60
    
    # Zero division safety
    assert calculate_ndvi(0.0, 0.0) == 0.0
    assert calculate_ndre(0.0, 0.0) == 0.0


def test_feature_fusion_pipeline():
    sample_data = {
        "air_temperature": 31.5,
        "relative_humidity": 55.0,
        "leaf_temperature": 34.0,
        "solar_radiation": 750.0,
        "soil_moisture_15": 14.2,
        "soil_moisture_30": 18.0,
        "soil_moisture_60": 22.0,
        "soil_temperature": 27.0,
        "electrical_conductivity": 1.4,
        "wind_speed": 2.5,
        "sap_flow": 0.22,
        "red": 0.12,
        "red_edge": 0.25,
        "nir": 0.50
    }
    
    derived = extract_derived_features(sample_data)
    assert "vpd" in derived
    assert "cwsi" in derived
    assert "ndvi" in derived
    assert "ndre" in derived
    
    f_dict = to_feature_dict(sample_data, derived)
    assert len(f_dict) == 15
    
    vector = to_feature_vector(f_dict)
    assert vector.shape == (1, 15)
