"""
Crop Stress ML Prediction and Inference Service.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import pandas as pd
import numpy as np

from app.core.config import settings
from app.features.fusion import (
    FEATURE_COLUMNS,
    TARGET_CLASSES,
    extract_derived_features,
    to_feature_dict
)
from app.ml.preprocessing import preprocess_reading_dict


class CropStressPredictor:
    """
    Inference engine for sensor fusion crop stress classification.
    """
    def __init__(self, model_path: Optional[Path] = None, metadata_path: Optional[Path] = None):
        self.model_path = model_path or settings.MODEL_PATH
        self.metadata_path = metadata_path or settings.METADATA_PATH
        self.model = None
        self.metadata: Dict[str, Any] = {}
        self.load_model()

    def load_model(self) -> bool:
        """Load trained Random Forest model and metadata."""
        try:
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
            if self.metadata_path.exists():
                with open(self.metadata_path, "r") as f:
                    self.metadata = json.load(f)
            return self.model is not None
        except Exception as e:
            print(f"Warning: Failed to load model from {self.model_path}: {e}")
            return False

    def predict(self, sensor_data: Any, derived: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Run sensor fusion inference on a sensor reading.
        Returns prediction class, confidence, class probabilities, derived features, and explainability.
        """
        if self.model is None:
            if not self.load_model():
                raise RuntimeError("ML Model not trained or loaded. Please train the model first.")

        # Ensure dictionary format
        if hasattr(sensor_data, "model_dump"):
            raw_dict = sensor_data.model_dump()
        elif isinstance(sensor_data, dict):
            raw_dict = dict(sensor_data)
        else:
            raw_dict = vars(sensor_data)

        # Preprocess and impute
        clean_features = preprocess_reading_dict(raw_dict)
        
        # Create DataFrame with proper feature names
        feature_df = pd.DataFrame([[clean_features[col] for col in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)

        # Predict class and probabilities
        pred_class = self.model.predict(feature_df)[0]
        probs = self.model.predict_proba(feature_df)[0]

        # Map classes to probabilities
        classes_in_model = list(self.model.classes_)
        prob_dict = {cls: 0.0 for cls in TARGET_CLASSES}
        for cls, p in zip(classes_in_model, probs):
            prob_dict[cls] = round(float(p), 4)

        confidence = prob_dict.get(pred_class, round(float(np.max(probs)), 4))

        # Explainability: Top contributing feature importances
        feature_importances = self.metadata.get("feature_importance", [])
        if not feature_importances and hasattr(self.model, "feature_importances_"):
            feature_importances = [
                {"feature": f, "importance": round(float(imp), 4)}
                for f, imp in zip(FEATURE_COLUMNS, self.model.feature_importances_)
            ]
            feature_importances.sort(key=lambda x: x["importance"], reverse=True)

        return {
            "prediction": str(pred_class),
            "confidence": round(float(confidence), 4),
            "probabilities": prob_dict,
            "features": {
                "vpd": clean_features["vpd"],
                "cwsi": clean_features["cwsi"],
                "ndvi": clean_features["ndvi"],
                "ndre": clean_features["ndre"]
            },
            "contributing_signals": feature_importances[:6]
        }


# Global singleton instance
predictor = CropStressPredictor()
