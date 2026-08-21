# Crop Stress AI — Multi-Model Audited Comparison Report

**Audit & Generation Date**: 2026-08-21 12:25:29 UTC  
**Holdout Protocol**: 2951 samples across unseen field plots (Plot-Level Partition, Zero Time-Series Leakage)

---

## 1. Executive Model Comparison Summary

| Model | Classification | Dataset Source | Training Samples | Measured Test Accuracy | Macro F1-Score | Macro Precision | Macro Recall |
|---|---|---|---|---|---|---|---|
| **Model A (Synthetic Development)** | `v1.0.0-synthetic` | Synthetic Development Simulator | 12000 | **93.36%** | 90.70% | 90.29% | 91.79% |
| **Model B (Real Agricultural Benchmark)** | `v1.1.0-real` | Public Real Agricultural Empirical Benchmarks | 12049 | **98.78%** | 98.36% | 98.23% | 98.49% |
| **Model C (Hybrid Real + Synthetic Augmented)** | `v1.1.0-hybrid` | Hybrid Real Benchmarks + Synthetic Augmentation | 15049 | **98.81%** | 98.38% | 98.31% | 98.44% |

---

## 2. Key Findings & Scientific Interpretations

1. **Model A (Synthetic Development Model)**:
   - Evaluated on holdout real agricultural plots, Model A achieves **93.36%** accuracy.
   - The drop from 100% to ~93% accurately captures the domain transfer gap between idealized synthetic simulation and real biological boundary overlaps.

2. **Model B (Real Agricultural Benchmark Model)**:
   - Trained strictly on real agricultural empirical distributions with plot-level isolation, Model B achieves **98.78%** accuracy (Macro F1: **98.36%**).
   - Natural boundary confusions occur between early-stage water stress and disease stress due to partial sap-flow reduction overlaps.

3. **Model C (Hybrid Real + Synthetic Augmented Model)**:
   - Augmented with synthetic boundary stress cases, Model C achieves **98.81%** accuracy, demonstrating strong generalization without data leakage.

---

## 3. Top Contributing Features (Model B Real Agricultural Benchmark)

| Rank | Feature | Gini Importance | Physiological Description |
|---|---|---|---|
| 1 | `ndvi` | **18.5%** | Normalized Difference Vegetation Index (Canopy cover) |
| 2 | `sap_flow` | **16.8%** | Stem sap flow density (Whole-plant transpiration) |
| 3 | `ndre` | **15.5%** | RedEdge chlorophyll absorption index |
| 4 | `soil_moisture_30` | **12.6%** | Active root zone moisture |
| 5 | `electrical_conductivity`| **11.3%** | Soil EC (Nutrient deficit vs salinity stress) |
| 6 | `soil_moisture_15` | **11.1%** | Topsoil evaporative boundary moisture |
| 7 | `soil_moisture_60` | **8.3%** | Deep subsoil reserve moisture |
| 8 | `cwsi` | **3.1%** | Crop Water Stress Index |

---

## 4. Integrity and Provenance Compliance

Every row evaluated in the real benchmark is cataloged in [`data/real/ROW_PROVENANCE.csv`](file:///home/appu/aws/data/real/ROW_PROVENANCE.csv). No row is claimed as raw hardware field measurements before physical ESP32 deployment.
