"""
Random Forest Model Training and Evaluation Pipeline.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from app.core.config import settings
from app.features.fusion import FEATURE_COLUMNS, TARGET_CLASSES
from app.ml.preprocessing import prepare_dataset_for_training
from app.ml.evaluation import evaluate_model
from app.simulator.sensor_generator import SensorDataSimulator


def train_crop_stress_model(
    data_path: Optional[Path] = None,
    n_estimators: int = 120,
    random_state: int = 42,
    num_samples: int = 12000,
    test_size: float = 0.1667  # ~2000 test samples out of 12000
) -> Dict[str, Any]:
    """
    Train Random Forest classifier for multi-sensor crop stress classification.
    """
    # 1. Load or generate training dataset
    if data_path and Path(data_path).exists():
        print(f"Loading existing training dataset from {data_path}...")
        df = pd.read_csv(data_path)
    else:
        print(f"Generating realistic {num_samples} multi-node sensor dataset...")
        simulator = SensorDataSimulator(random_seed=random_state)
        df = simulator.generate_dataset(num_samples=num_samples)
        # Save dataset
        settings.TRAINING_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(settings.TRAINING_DATA_PATH, index=False)
        print(f"Saved generated dataset to {settings.TRAINING_DATA_PATH}")

    # 2. Preprocess & extract features
    X, y = prepare_dataset_for_training(df)
    
    # 3. Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")

    # 4. Train RandomForestClassifier
    rf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=16,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)

    # 5. Evaluate
    metrics = evaluate_model(
        model=rf,
        X_test=X_test,
        y_test=y_test,
        class_names=TARGET_CLASSES,
        feature_names=FEATURE_COLUMNS
    )

    metrics["training_samples"] = len(X_train)
    metrics["test_samples"] = len(X_test)
    metrics["model_version"] = "v1.0.0-rf"
    metrics["trained_at"] = datetime.now().isoformat()

    # 6. Save model and metadata
    settings.MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(rf, settings.MODEL_PATH)
    print(f"Model saved to {settings.MODEL_PATH}")

    with open(settings.METADATA_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Model metadata saved to {settings.METADATA_PATH}")

    return metrics


if __name__ == "__main__":
    train_crop_stress_model()
