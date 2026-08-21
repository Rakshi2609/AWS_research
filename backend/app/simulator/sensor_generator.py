"""
Realistic Multi-Sensor Multi-Node IoT Data Simulator.

Generates correlated agronomic, microclimatic, and physiological sensor readings
for Healthy, Water Stress, Nutrient Stress, and Disease Stress crop conditions.
"""
import random
import math
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np

from app.models.schemas import SensorReading
from app.features.vegetation import estimate_spectral_bands
from app.features.vpd import calculate_vpd
from app.features.cwsi import calculate_cwsi
from app.features.vegetation import calculate_ndvi, calculate_ndre


GRID_MAP = [
    ("A1", 13.0827, 80.2707, "NODE_001"),
    ("A2", 13.0827, 80.2722, "NODE_002"),
    ("A3", 13.0827, 80.2737, "NODE_003"),
    ("A4", 13.0827, 80.2752, "NODE_004"),
    ("A5", 13.0827, 80.2767, "NODE_005"),
    ("B1", 13.0812, 80.2707, "NODE_006"),
    ("B2", 13.0812, 80.2722, "NODE_007"),
    ("B3", 13.0812, 80.2737, "NODE_008"),
    ("B4", 13.0812, 80.2752, "NODE_009"),
    ("B5", 13.0812, 80.2767, "NODE_010"),
    ("C1", 13.0797, 80.2707, "NODE_011"),
    ("C2", 13.0797, 80.2722, "NODE_012"),
    ("C3", 13.0797, 80.2737, "NODE_013"),
    ("C4", 13.0797, 80.2752, "NODE_014"),
    ("C5", 13.0797, 80.2767, "NODE_015"),
]


class SensorDataSimulator:
    """
    Simulates physical sensor responses under various agricultural stress conditions
    incorporating diurnal environmental variations and biological physiological correlations.
    """

    def __init__(self, random_seed: Optional[int] = 42):
        if random_seed is not None:
            random.seed(random_seed)
            np.random.seed(random_seed)

    def generate_ambient_environment(self, hour_of_day: float) -> Dict[str, float]:
        """
        Generate realistic diurnal ambient environmental variables.
        Day peak around 13:00 - 14:00.
        """
        # Solar radiation cycle (W/m²), peaking ~850 W/m² at 13:00
        solar_rad = max(0.0, 850.0 * math.sin(math.pi * max(0.0, min(14.0, hour_of_day - 5.0)) / 14.0))
        solar_rad += random.gauss(0, 20.0)
        solar_rad = max(0.0, min(1100.0, solar_rad))

        # Air temperature (°C), min ~22°C at 05:00, max ~34°C at 14:00
        diurnal_t = 28.0 + 6.0 * math.sin(math.pi * (hour_of_day - 8.0) / 12.0)
        air_temp = diurnal_t + random.gauss(0, 0.8)
        air_temp = max(15.0, min(45.0, air_temp))

        # Relative humidity (%), inversely correlated with temperature
        base_rh = 75.0 - 30.0 * math.sin(math.pi * (hour_of_day - 7.0) / 12.0)
        rel_hum = base_rh + random.gauss(0, 2.5)
        rel_hum = max(20.0, min(98.0, rel_hum))

        # Wind speed (m/s)
        wind_speed = max(0.2, random.gauss(2.5, 0.8))

        return {
            "air_temperature": round(air_temp, 2),
            "relative_humidity": round(rel_hum, 2),
            "solar_radiation": round(solar_rad, 1),
            "wind_speed": round(wind_speed, 2),
        }

    def generate_reading_for_condition(
        self,
        stress_class: str,
        grid_info: Tuple[str, float, float, str],
        timestamp: datetime,
        hour_of_day: Optional[float] = None,
        inject_missing: bool = False,
        noise_scale: float = 1.0
    ) -> Dict[str, Any]:
        """
        Generate a single sensor reading matching the canonical Pydantic schema
        with biological cross-correlations for the specified stress condition.
        """
        grid_id, lat, lon, node_id = grid_info
        if hour_of_day is None:
            hour_of_day = timestamp.hour + timestamp.minute / 60.0

        env = self.generate_ambient_environment(hour_of_day)
        air_temp = env["air_temperature"]
        rel_hum = env["relative_humidity"]
        solar_rad = env["solar_radiation"]
        wind_speed = env["wind_speed"]

        vpd = calculate_vpd(air_temp, rel_hum)

        # Generate correlated variables per class
        if stress_class == "Healthy":
            sm15 = random.gauss(32.0, 2.5 * noise_scale)
            sm30 = sm15 + random.gauss(3.0, 1.0)
            sm60 = sm30 + random.gauss(3.5, 1.0)
            soil_temp = air_temp - random.gauss(2.5, 0.5)
            ec = random.gauss(1.4, 0.2 * noise_scale)
            
            # Healthy transpiration cools the leaf below air temperature
            cooling_effect = (0.5 + 0.8 * (vpd / 2.0))
            leaf_temp = air_temp - cooling_effect + random.gauss(0, 0.4 * noise_scale)
            
            # High active sap flow
            sap_flow = max(0.6, min(1.4, 0.85 * (1.0 + solar_rad / 800.0) + random.gauss(0, 0.08)))
            
        elif stress_class == "Water Stress":
            sm15 = random.gauss(12.5, 2.0 * noise_scale)
            sm30 = sm15 + random.gauss(2.5, 1.0)
            sm60 = sm30 + random.gauss(3.0, 1.0)
            soil_temp = air_temp - random.gauss(0.8, 0.5)
            ec = random.gauss(1.6, 0.3 * noise_scale)
            
            # Stomatal closure stops transpiration -> leaf heats up past air temperature
            heating_effect = 2.0 + (solar_rad / 500.0) * 1.5
            leaf_temp = air_temp + heating_effect + random.gauss(0, 0.5 * noise_scale)
            
            # Severely suppressed sap flow
            sap_flow = max(0.04, min(0.35, 0.18 * (1.0 + solar_rad / 1200.0) + random.gauss(0, 0.04)))
            
        elif stress_class == "Nutrient Stress":
            # Adequate moisture, but abnormal EC and degrading chlorophyll
            sm15 = random.gauss(29.0, 2.5 * noise_scale)
            sm30 = sm15 + random.gauss(2.5, 1.0)
            sm60 = sm30 + random.gauss(3.0, 1.0)
            soil_temp = air_temp - random.gauss(2.0, 0.5)
            
            # Either nutrient deficiency (low EC) or salinity toxicity (high EC)
            if random.random() < 0.5:
                ec = random.gauss(0.42, 0.08 * noise_scale)  # N/P/K deficiency
            else:
                ec = random.gauss(3.8, 0.4 * noise_scale)   # Salinity / fertilizer burn
                
            leaf_temp = air_temp + random.gauss(0.8, 0.4 * noise_scale)
            sap_flow = max(0.35, min(0.70, 0.52 * (1.0 + solar_rad / 1000.0) + random.gauss(0, 0.05)))
            
        elif stress_class == "Disease Stress":
            # Adequate to high soil moisture, but vascular clogging / fungal pathogen
            sm15 = random.gauss(33.0, 3.0 * noise_scale)
            sm30 = sm15 + random.gauss(3.0, 1.0)
            sm60 = sm30 + random.gauss(3.5, 1.0)
            soil_temp = air_temp - random.gauss(2.2, 0.5)
            ec = random.gauss(1.35, 0.2 * noise_scale)
            
            # Localized canopy "fever" and compromised transpiration
            leaf_temp = air_temp + random.gauss(1.8, 0.6 * noise_scale)
            
            # Distinctive marker: LOW sap flow DESPITE HIGH soil moisture!
            sap_flow = max(0.08, min(0.38, 0.22 * (1.0 + solar_rad / 1200.0) + random.gauss(0, 0.04)))
            
        else:
            raise ValueError(f"Unknown stress class: {stress_class}")

        # Bounds safety
        sm15 = max(5.0, min(50.0, sm15))
        sm30 = max(7.0, min(55.0, sm30))
        sm60 = max(9.0, min(60.0, sm60))
        soil_temp = max(10.0, min(45.0, soil_temp))
        ec = max(0.1, min(6.0, ec))
        leaf_temp = max(15.0, min(52.0, leaf_temp))
        sap_flow = max(0.01, min(2.0, sap_flow))

        # Generate spectral bands
        red, red_edge, nir = estimate_spectral_bands(stress_class, noise=0.015 * noise_scale)
        ndvi = calculate_ndvi(nir, red)
        ndre = calculate_ndre(nir, red_edge)
        cwsi = calculate_cwsi(leaf_temp, air_temp, vpd, solar_rad)

        reading_dict = {
            "timestamp": timestamp.isoformat(),
            "node_id": node_id,
            "latitude": lat,
            "longitude": lon,
            "grid_id": grid_id,
            "soil_moisture_15": round(sm15, 2),
            "soil_moisture_30": round(sm30, 2),
            "soil_moisture_60": round(sm60, 2),
            "soil_temperature": round(soil_temp, 2),
            "electrical_conductivity": round(ec, 3),
            "air_temperature": round(air_temp, 2),
            "relative_humidity": round(rel_hum, 2),
            "solar_radiation": round(solar_rad, 1),
            "wind_speed": round(wind_speed, 2),
            "leaf_temperature": round(leaf_temp, 2),
            "sap_flow": round(sap_flow, 3),
            "red": red,
            "red_edge": red_edge,
            "nir": nir,
            "source": "simulation",
            # target label for training datasets
            "stress_class": stress_class,
            # precalculated features
            "vpd": vpd,
            "cwsi": cwsi,
            "ndvi": ndvi,
            "ndre": ndre
        }

        # Optional injection of random missing values for robustness evaluation
        if inject_missing and random.random() < 0.03:
            drop_key = random.choice(["wind_speed", "solar_radiation", "soil_temperature", "sap_flow"])
            reading_dict[drop_key] = np.nan

        return reading_dict

    def generate_dataset(
        self,
        num_samples: int = 12000,
        class_distribution: Optional[Dict[str, float]] = None,
        inject_missing_rate: float = 0.02
    ) -> pd.DataFrame:
        """
        Generate a complete training / testing dataset across multiple grid nodes.
        """
        if class_distribution is None:
            # Balanced distribution across classes
            class_distribution = {
                "Healthy": 0.35,
                "Water Stress": 0.25,
                "Nutrient Stress": 0.20,
                "Disease Stress": 0.20,
            }

        classes = list(class_distribution.keys())
        probabilities = list(class_distribution.values())

        records = []
        base_time = datetime(2026, 8, 21, 6, 0, 0)

        for i in range(num_samples):
            # Advance time slightly to sample full diurnal spectrum
            sample_time = base_time + timedelta(minutes=i * 2)
            hour_of_day = (sample_time.hour + sample_time.minute / 60.0) % 24.0

            # Pick a grid cell and node
            grid_info = random.choice(GRID_MAP)

            # Sample stress class
            stress_class = np.random.choice(classes, p=probabilities)

            # Inject missing values occasionally
            inject_missing = random.random() < inject_missing_rate

            reading = self.generate_reading_for_condition(
                stress_class=stress_class,
                grid_info=grid_info,
                timestamp=sample_time,
                hour_of_day=hour_of_day,
                inject_missing=inject_missing
            )
            records.append(reading)

        df = pd.DataFrame(records)
        return df


def get_grid_map() -> List[Tuple[str, float, float, str]]:
    """Return configured field nodes map."""
    return list(GRID_MAP)
