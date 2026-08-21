"""
Unit tests for Stress Decision Engine rules, thresholding, and cooldowns.
"""
from datetime import datetime, timedelta
import pytest
from app.services.stress_engine import StressDecisionEngine


def test_consecutive_readings_irrigation_trigger():
    engine = StressDecisionEngine(
        water_stress_threshold=0.75,
        consecutive_required=3,
        cooldown_seconds=300
    )
    
    zone = "A3"
    sensors = {"soil_moisture_15": 12.0, "electrical_conductivity": 1.4, "sap_flow": 0.15}
    derived = {"cwsi": 0.82, "vpd": 2.2, "ndvi": 0.55, "ndre": 0.32}
    probs = {"Healthy": 0.05, "Water Stress": 0.88, "Nutrient Stress": 0.04, "Disease Stress": 0.03}
    
    # Reading 1: should not trigger irrigation yet
    rec1 = engine.evaluate(zone, "Water Stress", 0.88, probs, sensors, derived)
    assert rec1.recommendation == "MONITORING_WATER_DEFICIT"
    assert rec1.consecutive_hits == 1
    assert rec1.valve_action == "HOLD"
    
    # Reading 2: still monitoring
    rec2 = engine.evaluate(zone, "Water Stress", 0.85, probs, sensors, derived)
    assert rec2.recommendation == "MONITORING_WATER_DEFICIT"
    assert rec2.consecutive_hits == 2
    
    # Reading 3: threshold met -> triggers IRRIGATE
    rec3 = engine.evaluate(zone, "Water Stress", 0.89, probs, sensors, derived)
    assert rec3.recommendation == "IRRIGATE"
    assert rec3.consecutive_hits == 3
    assert rec3.valve_action == "OPEN"
    assert engine.zone_valve_states[zone] == "OPEN"


def test_irrigation_cooldown():
    engine = StressDecisionEngine(
        water_stress_threshold=0.75,
        consecutive_required=3,
        cooldown_seconds=300
    )
    zone = "B1"
    sensors = {"soil_moisture_15": 10.0}
    derived = {"cwsi": 0.85}
    probs = {"Water Stress": 0.90}
    
    t0 = datetime(2026, 8, 21, 10, 0, 0)
    
    # Fire 3 readings to trigger
    engine.evaluate(zone, "Water Stress", 0.90, probs, sensors, derived, timestamp=t0)
    engine.evaluate(zone, "Water Stress", 0.90, probs, sensors, derived, timestamp=t0)
    rec = engine.evaluate(zone, "Water Stress", 0.90, probs, sensors, derived, timestamp=t0)
    assert rec.recommendation == "IRRIGATE"
    
    # 60 seconds later (still in 300s cooldown)
    t1 = t0 + timedelta(seconds=60)
    rec_cooldown = engine.evaluate(zone, "Water Stress", 0.90, probs, sensors, derived, timestamp=t1)
    assert rec_cooldown.recommendation == "IRRIGATION_COOLDOWN"
    assert rec_cooldown.valve_action == "HOLD"


def test_nutrient_and_disease_recommendations():
    engine = StressDecisionEngine()
    
    # Nutrient Stress
    rec_nutr = engine.evaluate(
        "A5", "Nutrient Stress", 0.82,
        {"Nutrient Stress": 0.82},
        {"electrical_conductivity": 0.40, "soil_moisture_15": 30.0},
        {"ndre": 0.18, "cwsi": 0.25}
    )
    assert rec_nutr.recommendation == "FERTILIZE_CHECK"
    
    # Disease Stress
    rec_dis = engine.evaluate(
        "C4", "Disease Stress", 0.84,
        {"Disease Stress": 0.84},
        {"sap_flow": 0.14, "soil_moisture_15": 34.0},
        {"cwsi": 0.60, "ndvi": 0.48}
    )
    assert rec_dis.recommendation == "FUNGICIDE_INSPECT"
