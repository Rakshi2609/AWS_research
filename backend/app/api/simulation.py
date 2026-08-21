"""
Simulation Control and Step API.
"""
import asyncio
import random
from datetime import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from app.models.schemas import SensorReading
from app.services.grid_service import grid_service
from app.simulator.sensor_generator import SensorDataSimulator, GRID_MAP

router = APIRouter(prefix="", tags=["Simulation Control"])

simulator = SensorDataSimulator(random_seed=None)
_simulation_task = None
_simulation_running = False

# Stateful condition distribution for realistic field dynamics
zone_conditions: Dict[str, str] = {
    "A1": "Healthy",
    "A2": "Healthy",
    "A3": "Water Stress",      # Persistent water stress zone
    "A4": "Healthy",
    "A5": "Nutrient Stress",   # Nutrient deficit zone
    "B1": "Healthy",
    "B2": "Disease Stress",    # Localized disease zone
    "B3": "Water Stress",      # Water stress zone
    "B4": "Healthy",
    "B5": "Healthy",
    "C1": "Nutrient Stress",
    "C2": "Healthy",
    "C3": "Healthy",
    "C4": "Disease Stress",
    "C5": "Healthy"
}


class SimulationToggleRequest(BaseModel):
    enabled: bool
    interval_seconds: float = 3.0


def step_simulation_iteration() -> List[Dict[str, Any]]:
    """
    Execute one full simulation step across all field zones and ingest telemetry.
    """
    now = datetime.now()
    results = []

    for grid_info in GRID_MAP:
        grid_id = grid_info[0]
        # Occasionally transition zones (10% chance)
        if random.random() < 0.05:
            zone_conditions[grid_id] = random.choice([
                "Healthy", "Healthy", "Water Stress", "Nutrient Stress", "Disease Stress"
            ])
            
        current_cond = zone_conditions.get(grid_id, "Healthy")
        
        # Generate correlated reading
        raw_reading = simulator.generate_reading_for_condition(
            stress_class=current_cond,
            grid_info=grid_info,
            timestamp=now,
            inject_missing=False
        )
        
        # Ingest through canonical schema
        reading_model = SensorReading(
            timestamp=raw_reading["timestamp"],
            node_id=raw_reading["node_id"],
            latitude=raw_reading["latitude"],
            longitude=raw_reading["longitude"],
            grid_id=raw_reading["grid_id"],
            soil_moisture_15=raw_reading["soil_moisture_15"],
            soil_moisture_30=raw_reading["soil_moisture_30"],
            soil_moisture_60=raw_reading["soil_moisture_60"],
            soil_temperature=raw_reading["soil_temperature"],
            electrical_conductivity=raw_reading["electrical_conductivity"],
            air_temperature=raw_reading["air_temperature"],
            relative_humidity=raw_reading["relative_humidity"],
            solar_radiation=raw_reading["solar_radiation"],
            wind_speed=raw_reading["wind_speed"],
            leaf_temperature=raw_reading["leaf_temperature"],
            sap_flow=raw_reading["sap_flow"],
            red=raw_reading.get("red"),
            red_edge=raw_reading.get("red_edge"),
            nir=raw_reading.get("nir"),
            source="simulation"
        )
        
        updated_cell = grid_service.ingest_sensor_reading(reading_model)
        results.append(updated_cell.model_dump())

    return results


async def background_simulation_worker(interval: float = 3.0):
    """Continuous background loop while simulation is enabled."""
    global _simulation_running
    while _simulation_running:
        try:
            step_simulation_iteration()
        except Exception as e:
            print(f"Error in background simulation worker: {e}")
        await asyncio.sleep(interval)


@router.post(
    "/simulation/toggle",
    summary="Start or stop automatic simulation stream"
)
async def toggle_simulation(req: SimulationToggleRequest):
    """
    Toggle continuous multi-node sensor stream simulation.
    """
    global _simulation_running, _simulation_task
    _simulation_running = req.enabled
    grid_service.simulation_active = req.enabled

    if req.enabled:
        if _simulation_task is None or _simulation_task.done():
            _simulation_task = asyncio.create_task(
                background_simulation_worker(req.interval_seconds)
            )
    else:
        if _simulation_task and not _simulation_task.done():
            _simulation_task.cancel()
            _simulation_task = None

    return {
        "status": "success",
        "simulation_active": _simulation_running,
        "interval_seconds": req.interval_seconds
    }


@router.post(
    "/simulation/step",
    summary="Trigger a single manual simulation step across all grid zones"
)
async def manual_simulation_step():
    """
    Simulate one synchronized reading cycle for all 15 nodes and update the field grid.
    """
    results = step_simulation_iteration()
    return {
        "status": "success",
        "zones_updated": len(results),
        "timestamp": datetime.now().isoformat()
    }


@router.get(
    "/simulation/status",
    summary="Get current simulation status"
)
async def get_simulation_status():
    """Get active state of continuous simulation."""
    return {
        "simulation_active": _simulation_running,
        "total_zones": len(GRID_MAP),
        "zone_assignments": zone_conditions
    }
