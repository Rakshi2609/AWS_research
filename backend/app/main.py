"""
FastAPI Application Entry Point.
AI-Enabled IoT Smart Crop Stress Detection Using Multi-Sensor Fusion.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import sensors, prediction, field, irrigation, multispectral, simulation
from app.ml.train import train_crop_stress_model
from app.ml.predict import predictor
from app.services.grid_service import grid_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown hooks."""
    print("🌾 Starting Crop Stress AI Backend...")
    # Check if model exists; if not, train initial model automatically
    if not settings.MODEL_PATH.exists():
        print("⚡ No trained model found. Generating synthetic dataset and training initial model...")
        train_crop_stress_model(num_samples=12000)
    
    # Load model into inference engine
    predictor.load_model()
    print("✅ ML Model and inference engine loaded.")
    
    # Initialize baseline grid state
    grid_service.initialize_grid()
    print("✅ Field Grid state initialized (15 zones).")
    
    yield
    
    print("🛑 Shutting down Crop Stress AI Backend...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Edge-oriented agricultural AI system detecting crop stress via multi-sensor fusion (Soil Moisture, EC, Leaf/Air Temp, Sap Flow, VPD, CWSI, NDVI, NDRE).",
    lifespan=lifespan
)

# Enable CORS for local React/Vite development and dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(sensors.router, prefix=settings.API_V1_STR)
app.include_router(prediction.router, prefix=settings.API_V1_STR)
app.include_router(field.router, prefix=settings.API_V1_STR)
app.include_router(irrigation.router, prefix=settings.API_V1_STR)
app.include_router(multispectral.router, prefix=settings.API_V1_STR)
app.include_router(simulation.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
        "endpoints": {
            "sensor_ingestion": "/api/sensor-data",
            "prediction": "/api/predict",
            "field_grid": "/api/field/grid",
            "irrigation": "/api/irrigation/status",
            "multispectral": "/api/multispectral/process",
            "simulation": "/api/simulation/status",
            "ml_metrics": "/api/ml/metrics"
        }
    }
