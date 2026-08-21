"""System configuration and constants."""
import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = BASE_DIR.parent / "data"
MODELS_DIR = APP_DIR / "ml" / "models"

class Settings(BaseModel):
    PROJECT_NAME: str = "Crop Stress AI - Multi-Sensor Fusion"
    VERSION: str = "1.1.0"
    API_V1_STR: str = "/api"
    
    # Active Model Selection: "real" | "synthetic" | "combined"
    MODEL_TYPE: str = os.getenv("MODEL_TYPE", "real")
    
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
    MODELS_DIR: Path = MODELS_DIR
    MODEL_PATH: Path = APP_DIR / "ml" / "model.joblib"
    METADATA_PATH: Path = APP_DIR / "ml" / "metadata.json"
    
    # Dataset Paths
    SYNTHETIC_DATA_PATH: Path = DATA_DIR / "synthetic" / "crop_stress_dataset.csv"
    REAL_DATA_PATH: Path = DATA_DIR / "real" / "real_crop_stress_dataset.csv"
    COMBINED_DATA_PATH: Path = DATA_DIR / "real" / "combined_crop_stress_dataset.csv"
    TRAINING_DATA_PATH: Path = DATA_DIR / "real" / "real_crop_stress_dataset.csv"
    
    SENSOR_LOGS_DIR: Path = DATA_DIR / "sensor_logs"
    MULTISPECTRAL_DIR: Path = DATA_DIR / "multispectral"

settings = Settings()

# Ensure directories exist
settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
settings.SENSOR_LOGS_DIR.mkdir(parents=True, exist_ok=True)
settings.REAL_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
settings.SYNTHETIC_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
settings.MULTISPECTRAL_DIR.mkdir(parents=True, exist_ok=True)
