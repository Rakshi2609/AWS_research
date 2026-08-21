"""
Integration tests for FastAPI endpoints.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "online"
    assert "endpoints" in data


def test_sensor_ingestion_api():
    payload = {
        "timestamp": "2026-08-21T10:15:00",
        "node_id": "NODE_001",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "grid_id": "A1",
        "soil_moisture_15": 31.4,
        "soil_moisture_30": 34.1,
        "soil_moisture_60": 37.8,
        "soil_temperature": 25.5,
        "electrical_conductivity": 1.25,
        "air_temperature": 29.2,
        "relative_humidity": 62.4,
        "solar_radiation": 700.0,
        "wind_speed": 2.2,
        "leaf_temperature": 28.1,
        "sap_flow": 0.92,
        "source": "hardware"
    }
    resp = client.post("/api/sensor-data", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["grid_id"] == "A1"
    assert data["current_stress"] == "Healthy"
    assert "derived_features" in data
    assert "recommendation" in data


def test_field_grid_api():
    resp = client.get("/api/field/grid")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_zones"] == 15
    assert len(data["cells"]) == 15
    assert "healthy_count" in data


def test_prediction_api():
    payload = {
        "sensor_data": {
            "timestamp": "2026-08-21T10:15:00",
            "node_id": "NODE_003",
            "latitude": 13.0827,
            "longitude": 80.2737,
            "grid_id": "A3",
            "soil_moisture_15": 11.2,
            "soil_moisture_30": 14.1,
            "soil_moisture_60": 17.8,
            "soil_temperature": 28.5,
            "electrical_conductivity": 1.64,
            "air_temperature": 33.2,
            "relative_humidity": 45.4,
            "solar_radiation": 850.0,
            "wind_speed": 2.8,
            "leaf_temperature": 37.1,
            "sap_flow": 0.12
        }
    }
    resp = client.post("/api/predict", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["prediction"] == "Water Stress"
    assert data["confidence"] >= 0.70
    assert "probabilities" in data
    assert "features" in data


def test_irrigation_control_api():
    # Toggle manual override
    resp = client.post("/api/irrigation/control", json={"zone": "A3", "action": "OPEN"})
    assert resp.status_code == 200
    
    # Check status
    status_resp = client.get("/api/irrigation/status")
    assert status_resp.status_code == 200
    assert "A3" in status_resp.json()["active_valves"]


def test_multispectral_api():
    payload = {
        "red": 0.06,
        "red_edge": 0.22,
        "nir": 0.75
    }
    resp = client.post("/api/multispectral/process", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["ndvi"] > 0.80
    assert data["ndre"] > 0.50


def test_ml_metrics_api():
    resp = client.get("/api/ml/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "accuracy" in data
    assert "feature_importance" in data
    assert len(data["class_names"]) == 4
