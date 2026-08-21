"""
End-to-End Pipeline Integration Test.
Simulator -> API Ingestion -> Feature Extraction -> Random Forest ML -> Stress Engine -> Grid State -> Dashboard API.
"""
from fastapi.testclient import TestClient
from app.main import app
from app.simulator.sensor_generator import SensorDataSimulator, GRID_MAP
from datetime import datetime

client = TestClient(app)


def test_full_pipeline_e2e():
    simulator = SensorDataSimulator(random_seed=123)
    now = datetime.now()
    
    # Step 1: Simulate water stress on Zone A3 for 3 cycles
    grid_a3 = [g for g in GRID_MAP if g[0] == "A3"][0]
    
    for i in range(3):
        raw = simulator.generate_reading_for_condition(
            stress_class="Water Stress",
            grid_info=grid_a3,
            timestamp=now
        )
        resp = client.post("/api/sensor-data", json=raw)
        assert resp.status_code == 200
        cell_data = resp.json()
        assert cell_data["grid_id"] == "A3"
        assert cell_data["current_stress"] == "Water Stress"
        
    # After 3 consecutive water stress readings, decision engine should recommend IRRIGATE
    assert cell_data["recommendation"]["recommendation"] == "IRRIGATE"
    assert cell_data["valve_state"] == "OPEN"
    
    # Step 2: Verify Field Grid reflection
    grid_resp = client.get("/api/field/grid")
    assert grid_resp.status_code == 200
    grid_state = grid_resp.json()
    assert grid_state["water_stress_count"] >= 1
    assert grid_state["active_valves_count"] >= 1
    
    # Step 3: Check cell history
    detail_resp = client.get("/api/field/cell/A3")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert len(detail["history"]) >= 3
    
    # Step 4: Check alerts
    alerts_resp = client.get("/api/alerts")
    assert alerts_resp.status_code == 200
    alerts = alerts_resp.json()
    assert len(alerts) > 0
    assert any(a["grid_id"] == "A3" and a["stress_type"] == "Water Stress" for a in alerts)
