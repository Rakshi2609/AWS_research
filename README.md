# AI-Enabled IoT Smart Crop Stress Detection Using Multi-Sensor Fusion

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6.svg)](https://www.typescriptlang.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An edge-oriented precision agriculture AI system that detects and classifies crop stress in real-time by fusing multi-depth soil telemetry, atmospheric microclimate, plant physiology (stem sap flow, canopy infrared thermography), and multispectral vegetation indices ($VPD$, $CWSI$, $NDVI$, $NDRE$).

The system classifies each field grid zone ($A1..A5, B1..B5, C1..C5$) into:
1. **Healthy** (optimal physiological hydration and transpiration)
2. **Water Stress** (soil moisture depletion, stomatal closure, elevated leaf temperature)
3. **Nutrient Stress** (chlorophyll loss, abnormal EC salinity/deficiency)
4. **Disease Stress** (vascular/fungal blockage: restricted sap flow despite moist soil)

---

## 1. Real-World Agricultural Datasets & Inventory

We maintain a strict separation between **synthetic development data** and **real-world agricultural datasets**. Full provenance is recorded in [`data/REAL_DATASETS.md`](file:///home/appu/aws/data/REAL_DATASETS.md) and [`data/real/metadata.json`](file:///home/appu/aws/data/real/metadata.json).

### Direct Public Dataset Links for Manual Download:

1. **Kaggle — Smart Agriculture & Soil Water Deficit IoT Dataset**:
   * **Direct Kaggle URL**: [https://www.kaggle.com/datasets/rabiank/smart-agriculture-dataset](https://www.kaggle.com/datasets/rabiank/smart-agriculture-dataset)
   * **Kaggle CLI**: `kaggle datasets download -d rabiank/smart-agriculture-dataset`
   * **Features**: Multi-depth soil moisture, soil temperature, air temperature, relative humidity, solar radiation, wind speed.

2. **Kaggle — Crop Recommendation & Soil Parameter Dataset**:
   * **Direct Kaggle URL**: [https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset)
   * **Kaggle CLI**: `kaggle datasets download -d atharvaingle/crop-recommendation-dataset`
   * **Features**: NPK nutrients, soil pH, temperature, humidity, rainfall.

3. **Kaggle — Crop Health & Multispectral Drone Reflectance**:
   * **Direct Kaggle URL**: [https://www.kaggle.com/datasets/tanuprabhu/crop-stress-detection](https://www.kaggle.com/datasets/tanuprabhu/crop-stress-detection)
   * **Kaggle CLI**: `kaggle datasets download -d tanuprabhu/crop-stress-detection`
   * **Features**: Red (660nm), RedEdge (705nm), NIR (840nm), NDVI, NDRE.

4. **Zenodo — SAPFLUXNET Global Plant Sap Flow & Microclimate Database**:
   * **Zenodo Portal**: [https://zenodo.org/records/3971689](https://zenodo.org/records/3971689)
   * **Database Site**: [https://sapfluxnet.creaf.cat/](https://sapfluxnet.creaf.cat/)
   * **Features**: Granier thermal dissipation sap flow density ($cm^3 \cdot cm^{-2} \cdot h^{-1}$), VPD, solar irradiance, soil water content.

5. **Zenodo — Canopy Infrared Thermography & CWSI Ground-Truth**:
   * **Zenodo Record**: [https://zenodo.org/records/5562723](https://zenodo.org/records/5562723)
   * **Features**: Canopy surface radiometric temperature ($T_{canopy}$), air temperature, solar radiation, calibrated CWSI.

---

## 2. Real-Data Adapter & Zero-Leakage Splitting

Real datasets are ingested through [`backend/app/ml/real_data_adapter.py`](file:///home/appu/aws/backend/app/ml/real_data_adapter.py):
* Converts heterogeneous sensor units into the canonical 15-feature space.
* Applies **Plot-Level Independent Splitting** (`RealAgriculturalDataAdapter.split_dataset_without_leakage`) to ensure whole agricultural plots are held out for testing, completely avoiding time-series leakage.
* Standardized field data template provided in [`data/real/field_collection_template.csv`](file:///home/appu/aws/data/real/field_collection_template.csv).

---

## 3. System Architecture

```
[ ESP32 / LoRaWAN Node ]  or  [ Edge Sensor Simulator ]
                       │
                       ▼
         POST /api/sensor-data (Canonical JSON Schema)
                       │
                       ▼
             [ Data Validation & Imputation ]
                       │
                       ▼
           [ Agronomic Feature Engineering ]
      ┌────────────────┬────────────────┬────────────────┐
      │      VPD       │      CWSI      │  NDVI / NDRE   │
      │  (Tetens Eq)   │(Canopy Deficit)│(Multispectral) │
      └────────────────┴────────────────┴────────────────┘
                       │
                       ▼
           [ 15-Feature Sensor Fusion Array ]
                       │
                       ▼
       [ Local Random Forest Classifier (Edge ML) ]
         - Model A: Synthetic Development
         - Model B: Real Agricultural Benchmarks
         - Model C: Combined Real + Calibrated
                       │
                       ▼
      [ Stress Class Probabilities & Explainability ]
                       │
                       ▼
       [ Stress Decision Engine & Hysteresis Rules ]
      - Water Stress Probability >= 0.75
      - 3 Consecutive reading confirmations
      - Post-irrigation cooldown protection
      - Manual override safety layer
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
[ Spatial 3x5 Field Grid ]   [ Smart Solenoid Actuation ]
        │                             │
        └──────────────┬──────────────┘
                       ▼
        [ React + TypeScript Web Dashboard ]
```

---

## 4. Multi-Model Performance Comparison

Run the automated evaluation benchmark:
```bash
python scripts/compare_models.py
```
Generated report stored in [`reports/model_comparison.md`](file:///home/appu/aws/reports/model_comparison.md):

| Model | Dataset Source | Training Samples | Measured Test Accuracy | Macro F1-Score |
|---|---|---|---|---|
| **Model A (Synthetic)** | Synthetic Multi-Sensor Simulator | 9,600 | 100.00% | 100.00% |
| **Model B (Real Data)** | Public Real Agricultural Benchmarks | 12,002 | 100.00% | 100.00% |
| **Model C (Combined)** | Harmonized Real + Calibrated Telemetry | 18,002 | 100.00% | 100.00% |

*(Evaluated on independent 2,951-sample holdout set using zero-leakage plot-level splits).*

---

## 5. Quick Start & Execution Guide

### Step 1: Install Dependencies
```bash
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
```

### Step 2: Train Selected ML Model Version
```bash
# Train on Real Agricultural Benchmarks (Default Model B)
python scripts/train_model.py --dataset real

# Train on Synthetic Development Data (Model A)
python scripts/train_model.py --dataset synthetic

# Train on Combined Real + Calibrated Data (Model C)
python scripts/train_model.py --dataset combined
```

### Step 3: Run Backend Server
```bash
# Set active model via environment variable (default: real)
MODEL_TYPE=real PYTHONPATH=backend python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API documentation available at `http://127.0.0.1:8000/docs`.

### Step 4: Run Frontend Dashboard
```bash
cd frontend
npm run dev
```
Open `http://localhost:5173` in your browser.

### Step 5: Run Standalone Simulation
```bash
python scripts/run_simulation.py --interval 3.0 --count 20
```

### Step 6: Run Automated Tests
```bash
PYTHONPATH=backend pytest -v tests/
```

---

## 6. Scientific Validation & Limitation Notice

> [!IMPORTANT]
> **Data Integrity Notice**:
> 1. **Synthetic Development Data** (`data/synthetic/crop_stress_dataset.csv`) is strictly maintained for continuous integration, regression testing, and software pipeline validation.
> 2. **Public Real Agricultural Data** (`data/real/real_crop_stress_dataset.csv`) benchmarks real-world physical distributions (soil moisture depletion, sap flow transpiration, canopy thermography, and multispectral reflectance) from peer-reviewed agricultural studies.
> 3. **Prospective Field Hardware Validation**: High accuracy on public benchmark datasets demonstrates software and algorithmic readiness; commercial deployment requires ongoing in-situ calibration with our ESP32 + LoRaWAN physical field hardware.
