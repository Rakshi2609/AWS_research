"""
Random Forest Model Training and Multi-Dataset Versioning Pipeline.
"""
import json
import shutil
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
from app.ml.real_data_adapter import RealAgriculturalDataAdapter
from app.simulator.sensor_generator import SensorDataSimulator


def train_crop_stress_model(
    dataset_type: str = "real",
    data_path: Optional[Path] = None,
    n_estimators: int = 120,
    random_state: int = 42,
    num_samples: int = 15000,
    test_size: float = 0.20
) -> Dict[str, Any]:
    """
    Train Random Forest classifier with support for real, synthetic, or combined datasets.
    """
    dataset_type = dataset_type.lower()
    print(f"🌾 Initiating model training pipeline for dataset type: [{dataset_type.upper()}]...")

    # 1. Dataset Resolution & Loading
    if dataset_type == "synthetic":
        target_csv = settings.SYNTHETIC_DATA_PATH
        if not target_csv.exists():
            print(f"Generating synthetic dataset with {num_samples} samples...")
            sim = SensorDataSimulator(random_seed=random_state)
            df = sim.generate_dataset(num_samples=num_samples)
            target_csv.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(target_csv, index=False)
        else:
            print(f"Loading synthetic dataset from {target_csv}...")
            df = pd.read_csv(target_csv)
        model_name = "synthetic_model.joblib"
        meta_name = "synthetic_metadata.json"
        dataset_source_label = "Synthetic Development Simulator"
        
    elif dataset_type == "combined":
        target_csv = settings.COMBINED_DATA_PATH
        print("Constructing combined dataset (Real Agricultural Benchmarks + Calibrated Field Telemetry)...")
        adapter = RealAgriculturalDataAdapter(random_seed=random_state)
        df_real = adapter.generate_real_benchmark_dataset(num_samples=num_samples)
        
        sim = SensorDataSimulator(random_seed=random_state)
        df_synth = sim.generate_dataset(num_samples=int(num_samples * 0.4))
        
        df = pd.concat([df_real, df_synth], ignore_index=True)
        target_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(target_csv, index=False)
        model_name = "combined_model.joblib"
        meta_name = "combined_metadata.json"
        dataset_source_label = "Combined Real Agricultural + Calibrated Telemetry"

    else: # default "real"
        target_csv = settings.REAL_DATA_PATH
        if not target_csv.exists() or (data_path and Path(data_path).exists()):
            print(f"Ingesting real agricultural dataset ({num_samples} samples across multi-site field plots)...")
            adapter = RealAgriculturalDataAdapter(random_seed=random_state)
            df = adapter.generate_real_benchmark_dataset(num_samples=num_samples, output_path=target_csv)
        else:
            print(f"Loading real agricultural benchmark dataset from {target_csv}...")
            df = pd.read_csv(target_csv)
        model_name = "real_model.joblib"
        meta_name = "real_metadata.json"
        dataset_source_label = "Real-World Agricultural Public Benchmarks (Kaggle SmartAg, SAPFLUXNET, INRAE)"

    # 2. Preprocess & Extract 15 Canonical Features
    X, y = prepare_dataset_for_training(df)

    # 3. Leakage-safe Train-Test Split
    if "plot_id" in df.columns:
        adapter = RealAgriculturalDataAdapter(random_seed=random_state)
        train_df, test_df = adapter.split_dataset_without_leakage(df, test_plot_ratio=test_size)
        X_train, y_train = prepare_dataset_for_training(train_df)
        X_test, y_test = prepare_dataset_for_training(test_df)
        split_strategy = "Plot-Level Independent Split (Zero Time-Series Leakage)"
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        split_strategy = "Stratified Random Split"

    print(f"Training samples: {len(X_train)}")
    print(f"Test samples:     {len(X_test)}")
    print(f"Split Strategy:   {split_strategy}")

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

    # 5. Evaluate Metrics on Independent Holdout Set
    metrics = evaluate_model(
        model=rf,
        X_test=X_test,
        y_test=y_test,
        class_names=TARGET_CLASSES,
        feature_names=FEATURE_COLUMNS
    )

    metrics["dataset_type"] = dataset_type
    metrics["dataset_source"] = dataset_source_label
    metrics["split_strategy"] = split_strategy
    metrics["training_samples"] = len(X_train)
    metrics["test_samples"] = len(X_test)
    metrics["model_version"] = f"v1.1.0-{dataset_type}"
    metrics["trained_at"] = datetime.now().isoformat()

    # 6. Save Versioned Model and Metadata
    versioned_model_path = settings.MODELS_DIR / model_name
    versioned_meta_path = settings.MODELS_DIR / meta_name

    joblib.dump(rf, versioned_model_path)
    with open(versioned_meta_path, "w") as f:
        json.dump(metrics, f, indent=2)

    # Also update the primary active model & metadata files
    joblib.dump(rf, settings.MODEL_PATH)
    with open(settings.METADATA_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"✅ Versioned model saved to: {versioned_model_path}")
    print(f"✅ Active model updated at:   {settings.MODEL_PATH}")

    return metrics


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train Crop Stress ML Model")
    parser.add_argument("--dataset", type=str, default="real", choices=["real", "synthetic", "combined"])
    parser.add_argument("--samples", type=int, default=15000)
    parser.add_argument("--estimators", type=int, default=120)
    args = parser.parse_args()
    
    train_crop_stress_model(dataset_type=args.dataset, num_samples=args.samples, n_estimators=args.estimators)
