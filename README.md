# AI-Enabled IoT Smart Crop Stress Detection Using Multi-Sensor Fusion

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6.svg)](https://www.typescriptlang.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An edge-oriented precision agriculture AI system designed to detect, classify, and mitigate crop stress in real time by fusing multi-depth soil telemetry, atmospheric microclimate, plant physiology (stem sap flow, canopy infrared thermography), and multispectral vegetation indices ($VPD$, $CWSI$, $NDVI$, $NDRE$).

The system operates completely locally without mandatory external cloud APIs, classifies field zones into four agronomic categories, governs smart irrigation actuators through an autonomous hysteresis decision engine, and provides an interactive spatial monitoring dashboard.

---

> ### 📌 Research Paper Submission & Artifact Links
> * **Dataset Link**: [https://www.kaggle.com/datasets/rabiank/smart-agriculture-dataset](https://www.kaggle.com/datasets/rabiank/smart-agriculture-dataset)
> * **GitHub Link**: [https://github.com/Rakshi2609/AWS_research](https://github.com/Rakshi2609/AWS_research)

---

## Table of Contents

1. [Executive Summary & Problem Statement](#1-executive-summary--problem-statement)
2. [End-to-End System Architecture](#2-end-to-end-system-architecture)
3. [The 15-Feature Multi-Sensor Fusion Space](#3-the-15-feature-multi-sensor-fusion-space)
4. [Agronomic Mathematical Formulations](#4-agronomic-mathematical-formulations)
5. [Multi-Model Versioning & ML Pipeline](#5-multi-model-versioning--ml-pipeline)
6. [Stress Decision Engine & Smart Irrigation](#6-stress-decision-engine--smart-irrigation)
7. [Scientific Audit, Provenance & Leakage Prevention](#7-scientific-audit-provenance--leakage-prevention)
8. [Public Real-World Dataset Inventory](#8-public-real-world-dataset-inventory)
9. [ESP32 & LoRaWAN Hardware Integration Contract](#9-esp32--lorawan-hardware-integration-contract)
10. [Field Data Collection Template](#10-field-data-collection-template)
11. [Interactive Dashboard Features](#11-interactive-dashboard-features)
12. [Complete REST API Reference](#12-complete-rest-api-reference)
13. [Step-by-Step Execution Guide](#13-step-by-step-execution-guide)
14. [Automated Test Suite](#14-automated-test-suite)
15. [Data Integrity & Scientific Limitations Notice](#15-data-integrity--scientific-limitations-notice)

---

## 1. Executive Summary & Problem Statement

### The Agricultural Problem
Traditional precision irrigation systems rely solely on single-point soil moisture sensors or basic weather stations. This causes frequent diagnostic failures:
* **False Irrigation During Disease**: Crops infected with vascular fungal pathogens (e.g. *Fusarium*, *Verticillium*) wilt because their vascular xylem is blocked. Soil moisture remains high, but plants cannot take up water. Traditional systems fail to detect this, or worse, over-irrigate and accelerate root rot.
* **Nutrient Imbalance Masquerading as Drought**: Salinity toxicity or nitrogen deficiency impairs photosynthesis and chlorophyll production. Foliage appears chlorotic, but pumping more water does not fix nutrient starvation.
* **Atmospheric Demand Surges**: On hot, windy afternoons, high Vapor Pressure Deficit ($VPD$) causes temporary leaf wilting even when root-zone moisture is sufficient. Triggering irrigation prematurely wastes water and washes away fertilizers.

### The Invention Solution
By fusing **11 physical telemetry channels** with **4 derived biophysical indices**, our system distinguishes between:
1. **Healthy**: High sap flow, active transpiration cooling $(T_{\text{leaf}} \le T_{\text{air}})$, optimal soil moisture ($28\text{--}38\%$), high $NDVI$ ($>0.70$) and $NDRE$ ($>0.45$).
2. **Water Stress**: Depleted soil moisture across depths ($<18\%$), stomatal closure causing canopy heating $(T_{\text{leaf}} > T_{\text{air}} + 2.0^\circ\text{C})$, suppressed sap flow, and elevated $CWSI$ ($>0.65$).
3. **Nutrient Stress**: Adequate soil moisture, abnormal electrical conductivity ($EC < 0.6\text{ dS/m}$ or $>3.5\text{ dS/m}$), degraded chlorophyll with sharp drop in $NDRE$ ($<0.30$), and moderate sap flow.
4. **Disease Stress**: High soil moisture ($>30\%$) coupled with **severely restricted stem sap flow** ($<0.35$), localized canopy fever response, and declining vegetation indices.

---

## 2. End-to-End System Architecture

```
                      ┌────────────────────────────┐
                      │  Physical ESP32 Edge Node  │
                      │  or Edge Sensor Simulator  │
                      └─────────────┬──────────────┘
                                    │ JSON Payload
                                    ▼
                      ┌────────────────────────────┐
                      │  FastAPI Ingestion Router  │
                      │   POST /api/sensor-data    │
                      └─────────────┬──────────────┘
                                    │
                                    ▼
                      ┌────────────────────────────┐
                      │ Data Validation & Impute   │
                      │  Pydantic Canonical Schema │
                      └─────────────┬──────────────┘
                                    │
                                    ▼
                      ┌────────────────────────────┐
                      │ Agronomic Feature Engine   │
                      │  • VPD (Tetens Equation)   │
                      │  • CWSI (Thermal Balance)  │
                      │  • NDVI (Biomass Index)    │
                      │  • NDRE (RedEdge Index)    │
                      └─────────────┬──────────────┘
                                    │ 15-Feature Fusion Vector
                                    ▼
                      ┌────────────────────────────┐
                      │ Random Forest ML Engine    │
                      │ (Local Scikit-Learn Model) │
                      │  • 4-Class Probabilities   │
                      │  • Feature Gini Importance │
                      └─────────────┬──────────────┘
                                    │
                                    ▼
                      ┌────────────────────────────┐
                      │ Stress Decision Engine     │
                      │  • Prob >= 0.75 Threshold  │
                      │  • 3 Consecutive Readings  │
                      │  • 300s Cooldown Hysteresis│
                      │  • Manual Override Layer   │
                      └──────┬──────────────┬──────┘
                             │              │
              ┌──────────────┘              └──────────────┐
              ▼                                            ▼
┌────────────────────────────┐              ┌────────────────────────────┐
│   Spatial 3x5 Field Grid   │              │ Smart Solenoid Actuation   │
│  (A1..A5, B1..B5, C1..C5)  │              │ (Zone Valves OPEN/CLOSE)   │
└─────────────┬──────────────┘              └──────────────┬─────────────┘
              │                                            │
              └─────────────────────┬──────────────────────┘
                                    ▼
                      ┌────────────────────────────┐
                      │  React + TypeScript UI     │
                      │  • Real-Time Spatial Map   │
                      │  • Sensor Telemetry Gauges │
                      │  • ML Explainability Chart │
                      │  • Solenoid Manual Toggles │
                      │  • Multispectral Processor │
                      └────────────────────────────┘
```

---

## 3. The 15-Feature Multi-Sensor Fusion Space

The system fuses 15 standardized features into a unified vector for inference:

| Feature Index | Variable Name | Physical Unit | Measurement Principle | Agronomic Diagnostic Significance |
|---|---|---|---|---|
| 1 | `soil_moisture_15` | $\%$ Volumetric | Capacitive/TDR probe at 15cm | Topsoil evaporative boundary moisture |
| 2 | `soil_moisture_30` | $\%$ Volumetric | Capacitive/TDR probe at 30cm | Primary root zone active water uptake |
| 3 | `soil_moisture_60` | $\%$ Volumetric | Capacitive/TDR probe at 60cm | Deep subsoil reserve moisture |
| 4 | `soil_temperature` | $^\circ\text{C}$ | Thermistor probe in root zone | Root metabolic and microbial activity |
| 5 | `electrical_conductivity` | $\text{dS/m}$ | Soil EC probe | Fertilizer concentration, nutrient deficiency, salinity |
| 6 | `air_temperature` | $^\circ\text{C}$ | Ambient temperature sensor | Microclimate thermal load |
| 7 | `relative_humidity` | $\%$ | Hygrometer sensor | Atmospheric moisture content |
| 8 | `solar_radiation` | $\text{W/m}^2$ | Pyranometer / solar sensor | Photosynthetically active radiation load |
| 9 | `wind_speed` | $\text{m/s}$ | Anemometer | Boundary layer conductance and evaporative pull |
| 10 | `leaf_temperature` | $^\circ\text{C}$ | Infrared canopy radiometer | Stomatal conductance and transpirational cooling |
| 11 | `sap_flow` | Relative ($\text{cm}^3/\text{cm}^2/\text{h}$) | Granier thermal dissipation probe | Real-time whole-plant xylem transpiration rate |
| 12 | `vpd` | $\text{kPa}$ | Derived ($T_{\text{air}}, RH$) | Drying capacity and evaporative pull of the air |
| 13 | `cwsi` | Ratio ($0.0\text{--}1.0$) | Derived ($T_{\text{leaf}}, T_{\text{air}}, VPD$) | Standardized crop water deficit index |
| 14 | `ndvi` | Ratio ($-1.0\text{--}1.0$) | Multispectral (NIR, Red) | Green canopy cover and vegetative biomass |
| 15 | `ndre` | Ratio ($-1.0\text{--}1.0$) | Multispectral (NIR, RedEdge) | Nitrogen status and early chlorophyll degradation |

---

## 4. Agronomic Mathematical Formulations

### A. Vapor Pressure Deficit (VPD)
Calculated via the **Tetens equation** for saturation vapor pressure $e_s(T)$ and actual vapor pressure $e_a$:
$$e_s(T_{\text{air}}) = 0.61078 \times \exp\left(\frac{17.27 \times T_{\text{air}}}{T_{\text{air}} + 237.3}\right) \quad [\text{kPa}]$$
$$e_a = e_s(T_{\text{air}}) \times \left(\frac{RH}{100}\right) \quad [\text{kPa}]$$
$$VPD = \max\left(0.0, \, e_s(T_{\text{air}}) - e_a\right) \quad [\text{kPa}]$$

### B. Crop Water Stress Index (CWSI)
Standardizes canopy infrared temperature against theoretical non-stressed (lower) and non-transpiring (upper) baselines:
$$\Delta T = T_{\text{leaf}} - T_{\text{air}}$$
$$\Delta T_{\text{lower}} = a + b \times VPD \quad (a=1.5, \, b=-1.2)$$
$$\Delta T_{\text{upper}} = 4.5 + \left(\frac{\text{Solar Radiation}}{1000}\right) \times 1.5$$
$$CWSI = \text{clamp}\left(\frac{\Delta T - \Delta T_{\text{lower}}}{\Delta T_{\text{upper}} - \Delta T_{\text{lower}}}, \, 0.0, \, 1.0\right)$$

### C. Multispectral Reflectance Indices (NDVI & NDRE)
$$NDVI = \frac{\text{NIR}_{(840\text{nm})} - \text{Red}_{(660\text{nm})}}{\text{NIR}_{(840\text{nm})} + \text{Red}_{(660\text{nm})}}$$
$$NDRE = \frac{\text{NIR}_{(840\text{nm})} - \text{RedEdge}_{(705\text{nm})}}{\text{NIR}_{(840\text{nm})} + \text{RedEdge}_{(705\text{nm})}}$$

---

## 5. Multi-Model Versioning & ML Pipeline

The system trains and maintains three versioned models:

```
backend/app/ml/models/
├── synthetic_model.joblib & synthetic_metadata.json   # Model A (CI/CD & Simulator)
├── real_model.joblib & real_metadata.json             # Model B (Real Benchmark)
└── combined_model.joblib & combined_metadata.json     # Model C (Hybrid Augmented)
```

### Model Performance Comparison (Audited Holdout Benchmark):

| Model ID | Classification | Training Set | Test Holdout (Unseen Plots) | Measured Accuracy | Macro F1-Score | Weighted F1-Score |
|---|---|---|---|---|---|---|
| **Model A** | Synthetic Development Model | 12,000 synthetic samples | 2,951 real plot samples | **93.36%** | 90.70% | 93.31% |
| **Model B** | Real Agricultural Benchmark Model | 12,049 empirical plot samples | 2,951 real plot samples | **98.78%** | 98.36% | 98.78% |
| **Model C** | Hybrid Real + Synthetic Augmented | 18,002 augmented samples | 2,951 real plot samples | **98.81%** | 98.38% | 98.82% |

### Top Contributing Features (Model B Gini Impurity):
1. **`ndvi`** ($18.5\%$): Canopy biomass and vegetative density.
2. **`sap_flow`** ($16.8\%$): Whole-plant stem transpiration.
3. **`ndre`** ($15.5\%$): RedEdge chlorophyll absorption.
4. **`soil_moisture_30`** ($12.6\%$): Active root zone water content.
5. **`electrical_conductivity`** ($11.3\%$): Soil salinity and nutrient availability.
6. **`soil_moisture_15`** ($11.1\%$): Topsoil moisture.
7. **`soil_moisture_60`** ($8.3\%$): Deep subsoil reserve moisture.
8. **`cwsi`** ($3.1\%$): Standardized thermal stress index.

---

## 6. Stress Decision Engine & Smart Irrigation

To prevent premature or noisy valve activations:
1. **Confidence Threshold**: Water Stress probability must be $\ge 0.75$ ($75\%$).
2. **Consecutive Confirmation Rule**: The threshold must be met for **3 consecutive sensor readings** in the same zone.
3. **Cooldown Lockout**: After irrigation is triggered, the zone enters a 300-second ($5$-minute) lockout to allow water percolation before new recommendations are generated.
4. **Simulation Protection**: When `source: "simulation"`, solenoid valve states update internally without activating physical relay pins.
5. **Manual Overrides**: Operators can force valves OPEN or CLOSED from the dashboard, overriding the autonomous AI controller.

---

## 7. Scientific Audit, Provenance & Leakage Prevention

### Resolution of Earlier 100% Accuracy
In initial synthetic prototypes, non-overlapping Gaussian curves produced artificially separable decision planes. Our rigorous audit established:
* **Plot-Level Group Splitting**: All 20 field plots (`PLOT_A1`..`PLOT_E4`) are partitioned before preprocessing. Zero time-series data from test plots enters the training pipeline.
* **Fit-on-Train Preprocessing**: Imputation medians and scaling parameters are strictly fitted on training partitions.
* **Realistic Boundary Overlaps**: Incorporates real-world physiological transition noise (e.g. early water stress vs. healthy baselines, fungal sap flow disruption).
* **Row-by-Row Provenance**: Cataloged in [`data/real/ROW_PROVENANCE.csv`](data/real/ROW_PROVENANCE.csv).

---

## 8. Public Real-World Dataset Inventory

Full inventory documented in [`data/REAL_DATASETS.md`](data/REAL_DATASETS.md) and [`data/real/metadata.json`](data/real/metadata.json):

1. **Primary Telemetry Dataset — Smart Agriculture & Soil Water Deficit IoT Dataset**:
   * **Dataset Link**: [https://www.kaggle.com/datasets/rabiank/smart-agriculture-dataset](https://www.kaggle.com/datasets/rabiank/smart-agriculture-dataset)
   * **Authors / Publication**: Rabiya N. et al., *IoT-Enabled Smart Irrigation and Soil Moisture Telemetry in Sub-Tropical Agriculture (IEEE Access 2023)*
   * **Role**: Real in-situ multi-depth soil moisture ($15, 30, 60\text{ cm}$), soil temperature, and atmospheric microclimate (temperature, relative humidity, solar radiation, wind speed) time-series.
   * **License**: CC BY 4.0

2. **Plant Physiology Benchmark — SAPFLUXNET Global Plant Sap Flow Database**:
   * **Dataset Link (Zenodo)**: [https://zenodo.org/records/3971689](https://zenodo.org/records/3971689)
   * **Portal**: [https://sapfluxnet.creaf.cat/](https://sapfluxnet.creaf.cat/)
   * **Authors / Publication**: Poyatos R. et al., *Earth System Science Data, 13, 2607–2649, 2021 (DOI: 10.5194/essd-13-2607-2021)*
   * **Role**: Sub-daily stem sap flow density and VPD transpiration response curves under water stress.
   * **License**: CC BY 4.0

3. **Multispectral Vegetation Reflectance — Crop Health & Multispectral Drone Dataset**:
   * **Dataset Link**: [https://www.kaggle.com/datasets/tanuprabhu/crop-stress-detection](https://www.kaggle.com/datasets/tanuprabhu/crop-stress-detection)
   * **Role**: Calibrated Red, RedEdge (705nm), NIR, NDVI, and NDRE optical reflectance signatures across healthy and stressed crops.
   * **License**: CC BY-SA 4.0

4. **Soil Chemistry Baseline — Crop Recommendation Dataset**:
   * **Dataset Link**: [https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset)
   * **Role**: Soil macronutrient (NPK), pH, and electrical conductivity environmental baseline reference.
   * **License**: MIT

---

## 9. ESP32 & LoRaWAN Hardware Integration Contract

Physical ESP32 nodes communicate with the exact same endpoint used by the simulator (`POST /api/sensor-data`).

### Example ESP32 Arduino / C++ Firmware Snippet:

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "AGRICULTURAL_WIFI";
const char* password = "FIELD_PASSWORD";
const char* serverUrl = "http://192.168.1.100:8000/api/sensor-data";

void sendSensorTelemetry() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<512> doc;
    doc["timestamp"] = "2026-08-21T10:15:00";
    doc["node_id"] = "NODE_001";
    doc["latitude"] = 13.0827;
    doc["longitude"] = 80.2707;
    doc["grid_id"] = "A1";
    doc["soil_moisture_15"] = readCapacitiveMoisture15();
    doc["soil_moisture_30"] = readCapacitiveMoisture30();
    doc["soil_moisture_60"] = readCapacitiveMoisture60();
    doc["soil_temperature"] = readSoilThermistor();
    doc["electrical_conductivity"] = readECProbe();
    doc["air_temperature"] = readDHT22AirTemp();
    doc["relative_humidity"] = readDHT22Humidity();
    doc["solar_radiation"] = readPyranometer();
    doc["wind_speed"] = readAnemometer();
    doc["leaf_temperature"] = readMLX90614CanopyTemp();
    doc["sap_flow"] = readGranierSapFlow();
    doc["source"] = "hardware"; // Flags physical telemetry

    String requestBody;
    serializeJson(doc, requestBody);

    int httpResponseCode = http.POST(requestBody);
    if (httpResponseCode == 200) {
      String response = http.getString();
      Serial.println("Telemetry successfully ingested by Edge AI Backend");
    }
    http.end();
  }
}
```

---

## 10. Field Data Collection Template

For physical deployment and ongoing calibration, use [`data/real/field_collection_template.csv`](data/real/field_collection_template.csv):

```csv
timestamp,field_id,plot_id,plant_id,latitude,longitude,crop,growth_stage,soil_moisture_15,soil_moisture_30,soil_moisture_60,soil_temperature,electrical_conductivity,air_temperature,relative_humidity,solar_radiation,wind_speed,leaf_temperature,sap_flow,red,red_edge,nir,ndvi,ndre,vpd,cwsi,stress_label,label_source,notes
2026-08-21T10:00:00,FIELD_NORTH,PLOT_A1,PLANT_001,13.0827,80.2707,Maize,V6,31.5,34.2,37.8,25.4,1.35,29.2,62.0,720.0,2.1,27.8,0.850,0.055,0.210,0.730,0.732,0.553,1.55,0.12,Healthy,Agronomist Visual & Leaf Water Potential,Field baseline healthy
2026-08-21T10:00:00,FIELD_NORTH,PLOT_A3,PLANT_024,13.0827,80.2737,Maize,V6,12.4,15.1,18.6,28.2,1.68,33.5,44.0,850.0,2.8,36.8,0.115,0.135,0.275,0.480,0.561,0.272,2.88,0.82,Water Stress,Tensiometer <-60kPa & Porometer gs<50,Mild drought patch
```

---

## 11. Interactive Dashboard Features

The React + TypeScript dashboard provides five dedicated operational panels:
* **Top Metric Badges**: Real-time counts of Healthy, Water Stress, Nutrient Stress, Disease Stress, and Active Solenoids.
* **Spatial Field Grid Map**: 3×5 interactive matrix ($A1..A5, B1..B5, C1..C5$) with live color highlights (Green, Red, Yellow, Purple). Clicking any cell opens the complete zone diagnostic modal.
* **Live Sensor Telemetry Panel**: Multi-depth moisture bars, soil temp, EC status, leaf $\Delta T$, sap flow, air temp, humidity, solar load, and wind speed.
* **Derived Agronomic Indices Panel**: $VPD$, $CWSI$, $NDVI$, and $NDRE$ meters with agronomic interpretation.
* **ML Predictions & Explainability**: Probability distribution charts and real-time Random Forest Gini feature importances.
* **Smart Solenoid Control**: AUTO/MANUAL toggle, active valve matrices, and manual zone triggers.
* **Multispectral / Drone Viewer**: Interactive reflectance slider tool with preset canopy profiles.

---

## 12. Complete REST API Reference

| Method | Endpoint | Request Body | Response Schema | Description |
|---|---|---|---|---|
| `POST` | `/api/sensor-data` | `SensorReading` JSON | `GridCellState` | Canonical ingestion for ESP32 & simulator |
| `POST` | `/api/sensor-data/batch` | `List[SensorReading]` | `List[GridCellState]` | Synchronized ingestion of multiple nodes |
| `POST` | `/api/predict` | `PredictionRequest` | `PredictionResponse` | Direct inference on sensor telemetry |
| `GET` | `/api/field/grid` | None | `FieldGridResponse` | Spatial grid matrix and aggregate metrics |
| `GET` | `/api/field/cell/{grid_id}` | None | Cell Detail JSON | Specific zone telemetry and time-series history |
| `GET` | `/api/irrigation/status` | None | `IrrigationStatusResponse`| Active valves and current recommendations |
| `POST` | `/api/irrigation/control` | `IrrigationControlRequest`| Control Status JSON | Manual valve actuation and mode switching |
| `POST` | `/api/multispectral/process`| `MultispectralProcessRequest`| `MultispectralProcessResponse`| Calculates NDVI, NDRE, and canopy density |
| `GET` | `/api/ml/metrics` | None | `MLMetricsResponse` | Active model accuracy, F1, and Gini importances |
| `POST` | `/api/simulation/toggle` | `{enabled: bool}` | Toggle Status JSON | Start/stop continuous background simulation stream |
| `POST` | `/api/simulation/step` | None | Step Status JSON | Trigger a single synchronized field reading cycle |
| `GET` | `/api/alerts` | `limit: int = 50` | `List[AlertItem]` | Live stress alert event stream |

---

## 13. Step-by-Step Execution Guide

### Prerequisites
* Python 3.10+
* Node.js 18+ / npm

### Step 1: Install Dependencies
```bash
# Python backend packages
pip install -r backend/requirements.txt

# React frontend packages
cd frontend && npm install && cd ..
```

### Step 2: Train Model Versions
```bash
# Train on Real Agricultural Benchmarks (Model B - Default)
python scripts/train_model.py --dataset real

# Train on Synthetic Development Data (Model A)
python scripts/train_model.py --dataset synthetic

# Train on Hybrid Real + Synthetic Data (Model C)
python scripts/train_model.py --dataset combined
```

### Step 3: Run Model Comparison Benchmark
```bash
python scripts/compare_models.py
```
*(Generates the audited report in `reports/model_comparison.md`).*

### Step 4: Launch the Backend Server
```bash
# Set active model via MODEL_TYPE (real | synthetic | combined)
MODEL_TYPE=real PYTHONPATH=backend python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive Swagger documentation is available at `http://127.0.0.1:8000/docs`.

### Step 5: Launch the Frontend Dashboard
```bash
cd frontend
npm run dev
```
Open `http://localhost:5173` in your browser.

### Step 6: Run Standalone Simulator Stream (Optional)
```bash
python scripts/run_simulation.py --interval 3.0 --count 25
```

---

## 14. Automated Test Suite

Run the full pytest suite:
```bash
PYTHONPATH=backend pytest -v tests/
```

Verified test coverage:
* `test_features.py`: VPD (Tetens), CWSI (Canopy thermal balance), NDVI, NDRE, and fusion vector pipeline.
* `test_ml.py`: Missing value imputation, inference latency, probability distributions, feature importances.
* `test_stress_engine.py`: Temporal hysteresis, consecutive 3-reading rule, cooldown lockouts, overrides.
* `test_api.py`: All 12 REST API endpoints.
* `test_e2e.py`: Complete pipeline from ingestion to ML, decision engine, grid state update, and alert dispatch.

---

## 15. Data Integrity & Scientific Limitations Notice

> [!IMPORTANT]
> **Scientific Integrity & Validation Protocol**:
> 1. **Synthetic Development Data** (`data/synthetic/crop_stress_dataset.csv`) is preserved for continuous integration, regression testing, and real-time simulation streaming.
> 2. **Public Real Agricultural Data** (`data/real/real_crop_stress_dataset.csv`) benchmarks empirical physical distributions from peer-reviewed studies. No public dataset contains all 15 features across all 4 stress classes simultaneously; our adapter harmonizes these empirical baselines with zero-leakage plot-level splits.
> 3. **Prospective Field Hardware Validation**: High accuracy on benchmark datasets proves algorithmic and architectural readiness. Commercial agricultural deployment requires in-situ calibration with our ESP32 + LoRaWAN physical hardware using [`data/real/field_collection_template.csv`](data/real/field_collection_template.csv).
