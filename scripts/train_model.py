#!/usr/bin/env python3
"""
Train Random Forest Classifier for Crop Stress Detection and evaluate metrics.
"""
import sys
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import argparse
from app.ml.train import train_crop_stress_model
from app.core.config import settings


def main():
    parser = argparse.ArgumentParser(description="Train Crop Stress Multi-Sensor ML Model")
    parser.add_argument("--samples", type=int, default=12000, help="Dataset samples (if generating new)")
    parser.add_argument("--estimators", type=int, default=120, help="Number of Random Forest trees")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    print("=" * 60)
    print("🌾 CROP STRESS AI: MULTI-SENSOR FUSION MODEL TRAINING")
    print("=" * 60)

    metrics = train_crop_stress_model(
        data_path=settings.TRAINING_DATA_PATH if settings.TRAINING_DATA_PATH.exists() else None,
        n_estimators=args.estimators,
        random_state=args.seed,
        num_samples=args.samples
    )

    print("\n" + "=" * 60)
    print("📊 EVALUATION RESULTS (Measured on independent test set):")
    print("=" * 60)
    print(f"Training samples: {metrics['training_samples']}")
    print(f"Test samples:     {metrics['test_samples']}")
    print(f"\nAccuracy:         {metrics['accuracy'] * 100:.2f}%")
    print(f"Macro F1-Score:   {metrics['f1_macro'] * 100:.2f}%")
    print(f"Macro Precision:  {metrics['precision_macro'] * 100:.2f}%")
    print(f"Macro Recall:     {metrics['recall_macro'] * 100:.2f}%")

    print("\nClassification Report:")
    report = metrics["classification_report"]
    print(f"{'Class':<18} {'Precision':<10} {'Recall':<10} {'F1-Score':<10} {'Support':<8}")
    print("-" * 58)
    for cls in metrics["class_names"]:
        if cls in report:
            cls_stat = report[cls]
            print(f"{cls:<18} {cls_stat['precision']:<10.3f} {cls_stat['recall']:<10.3f} {cls_stat['f1-score']:<10.3f} {int(cls_stat['support']):<8}")
    print("-" * 58)

    print("\nTop Contributing Features (Random Forest Importance):")
    for idx, item in enumerate(metrics["feature_importance"][:8], 1):
        bar_len = int(item['importance'] * 30)
        bar = "█" * bar_len
        print(f" {idx}. {item['feature']:<24} {bar} ({item['importance'] * 100:.1f}%)")

    print("\nConfusion Matrix:")
    header = "          " + "  ".join([f"{c[:4]:>6}" for c in metrics["class_names"]])
    print(header)
    for i, row in enumerate(metrics["confusion_matrix"]):
        row_str = "  ".join([f"{val:>6}" for val in row])
        print(f"{metrics['class_names'][i][:8]:<10} {row_str}")
        
    print("\n✅ Model training complete and ready for edge inference.")


if __name__ == "__main__":
    main()
