"""
Stress Decision Engine.

Applies multi-reading temporal rules, confidence thresholds, and cooldowns
before issuing irrigation or agronomic control actions.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.core.config import settings
from app.models.schemas import IrrigationRecommendation


class StressDecisionEngine:
    """
    Evaluates ML predictions and sensor telemetry to generate robust agronomic
    recommendations without triggering premature or noisy actions.
    """

    def __init__(
        self,
        water_stress_threshold: float = settings.WATER_STRESS_THRESHOLD,
        consecutive_required: int = settings.CONSECUTIVE_READINGS_REQUIRED,
        cooldown_seconds: int = settings.IRRIGATION_COOLDOWN_SECONDS
    ):
        self.water_stress_threshold = water_stress_threshold
        self.consecutive_required = consecutive_required
        self.cooldown_seconds = cooldown_seconds
        
        # In-memory tracking per zone
        self.zone_consecutive_water_stress: Dict[str, int] = {}
        self.zone_last_irrigated: Dict[str, datetime] = {}
        self.zone_valve_states: Dict[str, str] = {}  # "OPEN" or "CLOSED"
        self.manual_overrides: Dict[str, str] = {}   # zone -> "OPEN" / "CLOSED" / "AUTO"
        self.system_mode: str = "AUTO"  # "AUTO" or "MANUAL"

    def evaluate(
        self,
        grid_id: str,
        prediction: str,
        confidence: float,
        probabilities: Dict[str, float],
        sensor_values: Dict[str, float],
        derived_features: Dict[str, float],
        timestamp: Optional[datetime] = None
    ) -> IrrigationRecommendation:
        """
        Evaluate reading and update zone decision state.
        """
        if timestamp is None:
            timestamp = datetime.now()

        water_prob = probabilities.get("Water Stress", 0.0)
        current_hits = self.zone_consecutive_water_stress.get(grid_id, 0)
        valve_action = "HOLD"

        # Check if zone is currently in cooldown after recent irrigation
        last_irr = self.zone_last_irrigated.get(grid_id)
        in_cooldown = False
        if last_irr and (timestamp - last_irr).total_seconds() < self.cooldown_seconds:
            in_cooldown = True

        # Rule 1: Water Stress Consecutive Evaluation
        if water_prob >= self.water_stress_threshold or (prediction == "Water Stress" and confidence >= 0.70):
            current_hits += 1
        else:
            # Gradually decay hits or reset
            current_hits = max(0, current_hits - 1)
            
        self.zone_consecutive_water_stress[grid_id] = current_hits

        # Determine Recommendation & Valve Action
        if current_hits >= self.consecutive_required:
            if in_cooldown:
                recommendation = "IRRIGATION_COOLDOWN"
                reason = f"High water stress ({water_prob*100:.1f}%), but zone is currently within post-irrigation cooldown ({int((timestamp - last_irr).total_seconds())}s / {self.cooldown_seconds}s)."
                valve_action = "HOLD"
            else:
                recommendation = "IRRIGATE"
                reason = f"High water-stress probability ({(water_prob*100):.1f}% >= {int(self.water_stress_threshold*100)}%) detected for {current_hits} consecutive readings (CWSI: {derived_features.get('cwsi', 0):.2f}, SM15: {sensor_values.get('soil_moisture_15', 0):.1f}%)."
                if self.system_mode == "AUTO":
                    valve_action = "OPEN"
                    self.zone_valve_states[grid_id] = "OPEN"
                    self.zone_last_irrigated[grid_id] = timestamp
        elif prediction == "Nutrient Stress" and confidence >= 0.65:
            recommendation = "FERTILIZE_CHECK"
            ec = sensor_values.get("electrical_conductivity", 0.0)
            ndre = derived_features.get("ndre", 0.0)
            reason = f"Nutrient stress detected with {confidence*100:.1f}% confidence. EC is {ec:.2f} dS/m and NDRE is {ndre:.2f}. Inspect fertigation system and soil nutrient levels."
            valve_action = "HOLD"
        elif prediction == "Disease Stress" and confidence >= 0.65:
            recommendation = "FUNGICIDE_INSPECT"
            sap = sensor_values.get("sap_flow", 0.0)
            reason = f"Pathogen/disease stress detected with {confidence*100:.1f}% confidence. Sap flow is severely reduced ({sap:.2f}) despite adequate soil moisture. Inspect zone for fungal/vascular infection."
            valve_action = "HOLD"
        elif prediction == "Water Stress" and current_hits < self.consecutive_required:
            recommendation = "MONITORING_WATER_DEFICIT"
            reason = f"Water stress detected ({water_prob*100:.1f}%), reading {current_hits}/{self.consecutive_required} needed to confirm persistent deficit."
            valve_action = "HOLD"
        else:
            recommendation = "NORMAL_MONITOR"
            reason = "Crop physiological indicators within optimal operating range."
            if self.system_mode == "AUTO" and self.zone_valve_states.get(grid_id) == "OPEN":
                # Close valve when healthy
                valve_action = "CLOSE"
                self.zone_valve_states[grid_id] = "CLOSED"

        # Apply manual overrides if set
        manual_override = self.manual_overrides.get(grid_id)
        if manual_override in ["OPEN", "CLOSED"]:
            self.zone_valve_states[grid_id] = manual_override
            valve_action = f"MANUAL_{manual_override}"
            reason += f" [Manual Override Active: {manual_override}]"

        return IrrigationRecommendation(
            zone=grid_id,
            stress=prediction,
            confidence=round(confidence, 4),
            recommendation=recommendation,
            reason=reason,
            consecutive_hits=current_hits,
            valve_action=valve_action
        )

    def set_valve_state(self, grid_id: str, state: str) -> None:
        """Manually open or close a zone valve."""
        self.zone_valve_states[grid_id] = state
        self.manual_overrides[grid_id] = state

    def set_system_mode(self, mode: str) -> None:
        """Switch between AUTO and MANUAL system modes."""
        self.system_mode = mode.upper()
        if self.system_mode == "AUTO":
            self.manual_overrides.clear()


# Global singleton instance
stress_engine = StressDecisionEngine()
