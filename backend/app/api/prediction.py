"""
Direct ML Prediction and Metrics API.
"""
import json
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from app.core.config import settings
from app.models.schemas import (
    PredictionRequest,
    PredictionResponse,
    MLMetricsResponse,
    DerivedFeatures
)
from app.ml.predict import predictor

router = APIRouter(prefix="", tags=["ML & Prediction"])


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Run crop stress ML inference on telemetry"
)
async def predict_crop_stress(request: PredictionRequest) -> PredictionResponse:
    """
    Run the trained Random Forest classifier on sensor data and calculated features.
    Returns predicted stress class, confidence, all class probabilities, and derived indices.
    """
    try:
        derived_dict = request.derived_features.model_dump() if request.derived_features else None
        res = predictor.predict(request.sensor_data, derived_dict)
        return PredictionResponse(
            prediction=res["prediction"],
            confidence=res["confidence"],
            probabilities=res["probabilities"],
            features=DerivedFeatures(**res["features"]),
            contributing_signals=res.get("contributing_signals")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(e)}"
        )


@router.get(
    "/ml/metrics",
    response_model=MLMetricsResponse,
    summary="Get ML model evaluation metrics and feature importances"
)
async def get_ml_metrics() -> MLMetricsResponse:
    """
    Retrieve real evaluation metrics, classification report, confusion matrix,
    and feature importances from the trained model.
    """
    if not settings.METADATA_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model metadata not found. Please train the model first."
        )
    try:
        with open(settings.METADATA_PATH, "r") as f:
            metadata = json.load(f)
        return MLMetricsResponse(**metadata)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read model metadata: {str(e)}"
        )
