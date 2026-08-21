#!/usr/bin/env python3
"""
Standalone Real-Time Simulation Script.
Streams simulated ESP32 LoRaWAN sensor packets to the FastAPI backend.
"""
import sys
import time
import requests
import json
from pathlib import Path
from datetime import datetime

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.simulator.sensor_generator import SensorDataSimulator, GRID_MAP


def run_standalone_simulation(api_url: str = "http://127.0.0.1:8000/api/sensor-data", interval: float = 3.0, iterations: int = 50):
    print("=" * 65)
    print("🌾 IOT SENSOR SIMULATOR -> FASTAPI INGESTION STREAM")
    print(f"Target Endpoint: {api_url}")
    print(f"Broadcasting from 15 Grid Nodes (A1..A5, B1..B5, C1..C5)")
    print("=" * 65)

    simulator = SensorDataSimulator()
    step = 0

    # Stress assignments per node to demonstrate diverse field conditions
    zone_profiles = {
        "A1": "Healthy", "A2": "Healthy", "A3": "Water Stress", "A4": "Healthy", "A5": "Nutrient Stress",
        "B1": "Healthy", "B2": "Disease Stress", "B3": "Water Stress", "B4": "Healthy", "B5": "Healthy",
        "C1": "Nutrient Stress", "C2": "Healthy", "C3": "Healthy", "C4": "Disease Stress", "C5": "Healthy"
    }

    try:
        while iterations <= 0 or step < iterations:
            step += 1
            now = datetime.now()
            print(f"\n⏱ [Iteration #{step}] Telemetry Packet Timestamp: {now.strftime('%H:%M:%S')}")
            
            for grid_info in GRID_MAP:
                grid_id = grid_info[0]
                cond = zone_profiles.get(grid_id, "Healthy")
                
                # Generate reading with canonical schema
                reading = simulator.generate_reading_for_condition(
                    stress_class=cond,
                    grid_info=grid_info,
                    timestamp=now
                )
                
                payload = {
                    "timestamp": reading["timestamp"],
                    "node_id": reading["node_id"],
                    "latitude": reading["latitude"],
                    "longitude": reading["longitude"],
                    "grid_id": reading["grid_id"],
                    "soil_moisture_15": reading["soil_moisture_15"],
                    "soil_moisture_30": reading["soil_moisture_30"],
                    "soil_moisture_60": reading["soil_moisture_60"],
                    "soil_temperature": reading["soil_temperature"],
                    "electrical_conductivity": reading["electrical_conductivity"],
                    "air_temperature": reading["air_temperature"],
                    "relative_humidity": reading["relative_humidity"],
                    "solar_radiation": reading["solar_radiation"],
                    "wind_speed": reading["wind_speed"],
                    "leaf_temperature": reading["leaf_temperature"],
                    "sap_flow": reading["sap_flow"],
                    "red": reading.get("red"),
                    "red_edge": reading.get("red_edge"),
                    "nir": reading.get("nir"),
                    "source": "simulation"
                }

                try:
                    resp = requests.post(api_url, json=payload, timeout=2.0)
                    if resp.status_code == 200:
                        data = resp.json()
                        pred = data.get("current_stress", "N/A")
                        conf = data.get("confidence", 0.0)
                        rec = data.get("recommendation", {}).get("recommendation", "HOLD")
                        print(f"  📡 Node {reading['node_id']:<8} | Zone {grid_id}: {pred:<15} ({conf*100:4.1f}%) -> {rec}")
                    else:
                        print(f"  ❌ Error HTTP {resp.status_code} on Zone {grid_id}")
                except requests.exceptions.ConnectionError:
                    print(f"  ⚠️ Could not connect to {api_url}. Is FastAPI running? (uvicorn app.main:app)")
                    break

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n🛑 Simulation stopped by user.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Stream sensor simulation to FastAPI")
    parser.add_argument("--url", type=str, default="http://127.0.0.1:8000/api/sensor-data", help="Ingestion URL")
    parser.add_argument("--interval", type=float, default=3.0, help="Interval between cycles (seconds)")
    parser.add_argument("--count", type=int, default=10, help="Number of cycles (0 for infinite)")
    args = parser.parse_args()
    
    run_standalone_simulation(api_url=args.url, interval=args.interval, iterations=args.count)
