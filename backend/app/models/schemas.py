"""Canonical Pydantic models for IoT Crop Stress Detection System."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class SensorReading(BaseModel):
    """
    Canonical sensor reading payload received from ESP32 nodes,
    LoRaWAN gateways, or the edge simulator.
    """
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="ISO 8601 Timestamp of reading"
    )
    node_id: str = Field(..., description="Unique node identifier, e.g. NODE_001")
    latitude: float = Field(..., description="GPS latitude coordinate")
    longitude: float = Field(..., description="GPS longitude coordinate")
    grid_id: str = Field(..., description="Field grid location, e.g. A1, B3")
    
    # Soil metrics
    soil_moisture_15: float = Field(..., description="Volumetric water content at 15cm depth (%)")
    soil_moisture_30: float = Field(..., description="Volumetric water content at 30cm depth (%)")
    soil_moisture_60: float = Field(..., description="Volumetric water content at 60cm depth (%)")
    soil_temperature: float = Field(..., description="Soil temperature in Celsius")
    electrical_conductivity: float = Field(..., description="Soil electrical conductivity in dS/m (or mS/cm)")
    
    # Environmental metrics
    air_temperature: float = Field(..., description="Ambient air temperature in Celsius")
    relative_humidity: float = Field(..., description="Ambient relative humidity (%)")
    solar_radiation: float = Field(..., description="Solar irradiance (W/m²)")
    wind_speed: float = Field(..., description="Wind speed (m/s)")
    
    # Plant canopy & physiological metrics
    leaf_temperature: float = Field(..., description="Infrared canopy/leaf temperature in Celsius")
    sap_flow: float = Field(..., description="Stem sap flow rate (relative or g/h)")
    
    # Optional metadata and multispectral reflectance bands
    source: Optional[str] = Field("simulation", description="'simulation' or 'hardware'")
    red: Optional[float] = Field(None, description="Red reflectance band (660nm)")
    red_edge: Optional[float] = Field(None, description="RedEdge reflectance band (705nm)")
    nir: Optional[float] = Field(None, description="Near-Infrared reflectance band (840nm)")


class DerivedFeatures(BaseModel):
    """Engineered physiological & spectral indices."""
    vpd: float = Field(..., description="Vapor Pressure Deficit (kPa)")
    cwsi: float = Field(..., description="Crop Water Stress Index (0.0 to 1.0)")
    ndvi: float = Field(..., description="Normalized Difference Vegetation Index (-1.0 to 1.0)")
    ndre: float = Field(..., description="Normalized Difference Red Edge Index (-1.0 to 1.0)")


class PredictionRequest(BaseModel):
    """Direct inference request with sensor reading and optional derived features."""
    sensor_data: SensorReading
    derived_features: Optional[DerivedFeatures] = None


class PredictionResponse(BaseModel):
    """ML sensor-fusion classification response."""
    prediction: str = Field(..., description="Classified condition: Healthy, Water Stress, Nutrient Stress, Disease Stress")
    confidence: float = Field(..., description="Prediction confidence score (0.0 to 1.0)")
    probabilities: Dict[str, float] = Field(..., description="Probability distribution across all 4 stress classes")
    features: DerivedFeatures = Field(..., description="Calculated feature indices")
    contributing_signals: Optional[List[Dict[str, Any]]] = Field(
        default=None, 
        description="Top contributing feature importances for explainability"
    )


class IrrigationRecommendation(BaseModel):
    """Stress decision engine recommendation for a zone."""
    zone: str = Field(..., description="Field grid ID, e.g. A3")
    stress: str = Field(..., description="Identified stress condition")
    confidence: float = Field(..., description="Detection confidence")
    recommendation: str = Field(..., description="Action: IRRIGATE, FERTILIZE_CHECK, FUNGICIDE_INSPECT, NORMAL_MONITOR")
    reason: str = Field(..., description="Detailed decision rule reasoning")
    consecutive_hits: int = Field(0, description="Consecutive readings meeting threshold")
    valve_action: Optional[str] = Field(None, description="Valve command: OPEN, CLOSE, HOLD")


class GridCellState(BaseModel):
    """Complete real-time state of an individual field grid cell."""
    grid_id: str
    row: str
    col: int
    latitude: float
    longitude: float
    node_id: str
    current_stress: str
    confidence: float
    probabilities: Dict[str, float]
    sensor_values: Dict[str, float]
    derived_features: DerivedFeatures
    recommendation: IrrigationRecommendation
    valve_state: str = "CLOSED"  # OPEN, CLOSED
    last_updated: str
    consecutive_water_stress_count: int = 0


class FieldGridResponse(BaseModel):
    """Collection of all field grid cells and aggregate summary."""
    cells: List[GridCellState]
    total_zones: int
    healthy_count: int
    water_stress_count: int
    nutrient_stress_count: int
    disease_stress_count: int
    active_valves_count: int
    system_mode: str = "AUTO"  # AUTO or MANUAL
    simulation_active: bool = False
    timestamp: str


class IrrigationControlRequest(BaseModel):
    """Command to control irrigation mode or individual zone valve."""
    zone: Optional[str] = None
    action: Optional[str] = None  # OPEN, CLOSE, AUTO
    system_mode: Optional[str] = None  # AUTO, MANUAL


class IrrigationStatusResponse(BaseModel):
    """Overall status of irrigation system."""
    system_mode: str
    active_valves: List[str]
    recommendations: List[IrrigationRecommendation]
    last_action_timestamp: str


class MultispectralProcessRequest(BaseModel):
    """Payload for multispectral band extraction and index computation."""
    red: float
    red_edge: float
    nir: float
    green: Optional[float] = None


class MultispectralProcessResponse(BaseModel):
    """Calculated vegetation indices from multispectral data."""
    ndvi: float
    ndre: float
    chlorophyll_status: str
    canopy_density: str
    notes: str


class AlertItem(BaseModel):
    """System alert log item."""
    id: str
    timestamp: str
    grid_id: str
    stress_type: str
    confidence: float
    severity: str  # HIGH, MEDIUM, LOW
    message: str
    action_taken: str


class MLMetricsResponse(BaseModel):
    """ML evaluation metrics and feature importances."""
    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    confusion_matrix: List[List[int]]
    classification_report: Dict[str, Any]
    feature_importance: List[Dict[str, Any]]
    class_names: List[str]
    feature_names: List[str]
    training_samples: int
    test_samples: int
    model_version: str
    trained_at: str
