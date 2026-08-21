#!/usr/bin/env python3
"""
Generate synthetic multi-node sensor dataset for model training and evaluation.
"""
import sys
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import argparse
from app.simulator.sensor_generator import SensorDataSimulator
from app.core.config import settings


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic crop stress dataset")
    parser.add_argument("--samples", type=int, default=12000, help="Total number of samples to generate")
    parser.add_argument("--output", type=str, default=str(settings.TRAINING_DATA_PATH), help="Output CSV path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    print(f"🌾 Generating {args.samples} correlated sensor samples across 15 field grid nodes...")
    simulator = SensorDataSimulator(random_seed=args.seed)
    df = simulator.generate_dataset(num_samples=args.samples)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

    print(f"✅ Dataset successfully saved to: {out_path}")
    print(f"   Shape: {df.shape}")
    print(f"   Class Distribution:")
    for cls_name, count in df["stress_class"].value_counts().items():
        print(f"     - {cls_name:16}: {count} ({count/len(df)*100:.1f}%)")


if __name__ == "__main__":
    main()
