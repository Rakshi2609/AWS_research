"""System configuration and constants."""
import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = BASE_DIR.parent / "data"
MODELS_DIR = APP_DIR / "ml"

class Settings(BaseModel):
    PROJECT_NAME: str = "Crop Stress AI - Multi-Sensor Fusion"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Field Grid Configuration (3x5 = 15 zones)
    GRID_ROWS: list[str] = ["A", "B", "C"]
    GRID_COLS: list[int] = [1, 2, 3, 4, 5]
    BASE_LATITUDE: float = 13.0827
    BASE_LONGITUDE: float = 80.2707
    LAT_STEP: float = 0.0015
    LON_STEP: float = 0.0015
    
    # Stress Decision Engine Rules
    WATER_STRESS_THRESHOLD: float = 0.75
    CONSECUTIVE_READINGS_REQUIRED: int = 3
    IRRIGATION_COOLDOWN_SECONDS: int = 300
    
    # Paths
    MODEL_PATH: Path = MODELS_DIR / "model.joblib"
    METADATA_PATH: Path = MODELS_DIR / "metadata.json"
    TRAINING_DATA_PATH: Path = DATA_DIR / "training" / "crop_stress_dataset.csv"
    SENSOR_LOGS_DIR: Path = DATA_DIR / "sensor_logs"
    MULTISPECTRAL_DIR: Path = DATA_DIR / "multispectral"

settings = Settings()

# Ensure directories exist
settings.SENSOR_LOGS_DIR.mkdir(parents=True, exist_ok=True)
settings.TRAINING_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
settings.MULTISPECTRAL_DIR.mkdir(parents=True, exist_ok=True)
