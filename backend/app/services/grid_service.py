"""
Field Grid State and Telemetry Ingestion Service.

Maintains in-memory and persisted states of all field nodes,
derives indices, triggers inference, and logs stress alerts.
"""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

from app.core.config import settings
from app.models.schemas import (
    SensorReading,
    DerivedFeatures,
    GridCellState,
    FieldGridResponse,
    IrrigationRecommendation,
    AlertItem
)
from app.features.fusion import extract_derived_features
from app.ml.predict import predictor
from app.services.stress_engine import stress_engine
from app.simulator.sensor_generator import GRID_MAP


class FieldGridService:
    """
    Manages telemetry for all field grid cells (A1..A5, B1..B5, C1..C5).
    """

    def __init__(self):
        self.grid_cells: Dict[str, GridCellState] = {}
        self.cell_history: Dict[str, List[Dict[str, Any]]] = {}
        self.alerts: List[AlertItem] = []
        self.max_history_per_cell: int = 50
        self.max_alerts: int = 100
        self.simulation_active: bool = False
        self.initialize_grid()

    def initialize_grid(self) -> None:
        """Initialize all default 15 grid zones with baseline healthy telemetry."""
        now = datetime.now().isoformat()
        
        for grid_id, lat, lon, node_id in GRID_MAP:
            row = grid_id[0]
            col = int(grid_id[1])
            
            default_sensors = {
                "soil_moisture_15": 32.5,
                "soil_moisture_30": 35.0,
                "soil_moisture_60": 38.2,
                "soil_temperature": 24.8,
                "electrical_conductivity": 1.35,
                "air_temperature": 28.5,
                "relative_humidity": 62.0,
                "solar_radiation": 650.0,
                "wind_speed": 2.1,
                "leaf_temperature": 27.2,
                "sap_flow": 0.88,
            }
            
            derived = DerivedFeatures(
                vpd=1.48,
                cwsi=0.12,
                ndvi=0.76,
                ndre=0.52
            )
            
            rec = IrrigationRecommendation(
                zone=grid_id,
                stress="Healthy",
                confidence=0.95,
                recommendation="NORMAL_MONITOR",
                reason="Initial baseline status: optimal physiological hydration.",
                consecutive_hits=0,
                valve_action="HOLD"
            )
            
            self.grid_cells[grid_id] = GridCellState(
                grid_id=grid_id,
                row=row,
                col=col,
                latitude=lat,
                longitude=lon,
                node_id=node_id,
                current_stress="Healthy",
                confidence=0.95,
                probabilities={"Healthy": 0.95, "Water Stress": 0.02, "Nutrient Stress": 0.02, "Disease Stress": 0.01},
                sensor_values=default_sensors,
                derived_features=derived,
                recommendation=rec,
                valve_state="CLOSED",
                last_updated=now,
                consecutive_water_stress_count=0
            )
            self.cell_history[grid_id] = []

    def ingest_sensor_reading(self, reading: SensorReading) -> GridCellState:
        """
        Process incoming reading from ESP32, LoRaWAN gateway, or Simulator.
        1. Extract derived features (VPD, CWSI, NDVI, NDRE)
        2. Run ML Sensor Fusion Inference
        3. Pass to Stress Decision Engine
        4. Update Grid State & Log Alerts
        """
        grid_id = reading.grid_id
        timestamp_str = reading.timestamp or datetime.now().isoformat()
        
        # 1. Feature Engineering
        raw_dict = reading.model_dump()
        derived_dict = extract_derived_features(raw_dict)
        derived = DerivedFeatures(**derived_dict)
        
        # 2. ML Inference
        prediction_result = predictor.predict(raw_dict, derived_dict)
        pred_class = prediction_result["prediction"]
        confidence = prediction_result["confidence"]
        probabilities = prediction_result["probabilities"]
        
        sensor_values = {
            "soil_moisture_15": reading.soil_moisture_15,
            "soil_moisture_30": reading.soil_moisture_30,
            "soil_moisture_60": reading.soil_moisture_60,
            "soil_temperature": reading.soil_temperature,
            "electrical_conductivity": reading.electrical_conductivity,
            "air_temperature": reading.air_temperature,
            "relative_humidity": reading.relative_humidity,
            "solar_radiation": reading.solar_radiation,
            "wind_speed": reading.wind_speed,
            "leaf_temperature": reading.leaf_temperature,
            "sap_flow": reading.sap_flow,
        }
        
        # 3. Decision Engine
        rec = stress_engine.evaluate(
            grid_id=grid_id,
            prediction=pred_class,
            confidence=confidence,
            probabilities=probabilities,
            sensor_values=sensor_values,
            derived_features=derived_dict
        )
        
        valve_state = stress_engine.zone_valve_states.get(grid_id, "CLOSED")
        
        # 4. Update cell state
        if grid_id in self.grid_cells:
            cell = self.grid_cells[grid_id]
            cell.current_stress = pred_class
            cell.confidence = confidence
            cell.probabilities = probabilities
            cell.sensor_values = sensor_values
            cell.derived_features = derived
            cell.recommendation = rec
            cell.valve_state = valve_state
            cell.last_updated = timestamp_str
            cell.consecutive_water_stress_count = rec.consecutive_hits
        else:
            row = grid_id[0] if len(grid_id) > 0 else "A"
            col = int(grid_id[1:]) if len(grid_id) > 1 and grid_id[1:].isdigit() else 1
            cell = GridCellState(
                grid_id=grid_id,
                row=row,
                col=col,
                latitude=reading.latitude,
                longitude=reading.longitude,
                node_id=reading.node_id,
                current_stress=pred_class,
                confidence=confidence,
                probabilities=probabilities,
                sensor_values=sensor_values,
                derived_features=derived,
                recommendation=rec,
                valve_state=valve_state,
                last_updated=timestamp_str,
                consecutive_water_stress_count=rec.consecutive_hits
            )
            self.grid_cells[grid_id] = cell
            
        # Store in cell history
        if grid_id not in self.cell_history:
            self.cell_history[grid_id] = []
        self.cell_history[grid_id].append({
            "timestamp": timestamp_str,
            "stress": pred_class,
            "confidence": confidence,
            "sensor_values": sensor_values,
            "derived_features": derived_dict,
            "recommendation": rec.recommendation
        })
        if len(self.cell_history[grid_id]) > self.max_history_per_cell:
            self.cell_history[grid_id].pop(0)

        # Trigger alert if critical stress condition detected
        if pred_class != "Healthy" and confidence >= 0.70:
            severity = "HIGH" if pred_class == "Water Stress" and rec.consecutive_hits >= 3 else "MEDIUM"
            alert = AlertItem(
                id=str(uuid.uuid4())[:8],
                timestamp=timestamp_str,
                grid_id=grid_id,
                stress_type=pred_class,
                confidence=confidence,
                severity=severity,
                message=f"{pred_class.upper()} DETECTED in Zone {grid_id} (Confidence: {int(confidence*100)}%). {rec.reason}",
                action_taken=f"Recommendation: {rec.recommendation} | Valve Action: {rec.valve_action or 'NONE'}"
            )
            self.alerts.insert(0, alert)
            if len(self.alerts) > self.max_alerts:
                self.alerts.pop()

        return cell

    def get_grid_state(self) -> FieldGridResponse:
        """Return aggregate field grid state and summary statistics."""
        cells = list(self.grid_cells.values())
        
        healthy = sum(1 for c in cells if c.current_stress == "Healthy")
        water = sum(1 for c in cells if c.current_stress == "Water Stress")
        nutrient = sum(1 for c in cells if c.current_stress == "Nutrient Stress")
        disease = sum(1 for c in cells if c.current_stress == "Disease Stress")
        active_valves = sum(1 for c in cells if c.valve_state == "OPEN")

        return FieldGridResponse(
            cells=cells,
            total_zones=len(cells),
            healthy_count=healthy,
            water_stress_count=water,
            nutrient_stress_count=nutrient,
            disease_stress_count=disease,
            active_valves_count=active_valves,
            system_mode=stress_engine.system_mode,
            simulation_active=self.simulation_active,
            timestamp=datetime.now().isoformat()
        )

    def get_cell_detail(self, grid_id: str) -> Optional[Dict[str, Any]]:
        """Return current state and historical telemetry for a specific cell."""
        if grid_id not in self.grid_cells:
            return None
        return {
            "current": self.grid_cells[grid_id].model_dump(),
            "history": self.cell_history.get(grid_id, [])
        }

    def get_alerts(self, limit: int = 50) -> List[AlertItem]:
        """Return recent alerts."""
        return self.alerts[:limit]


# Global singleton instance
grid_service = FieldGridService()
