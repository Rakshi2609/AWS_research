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

## 1. System Architecture

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

## 2. Sensor Data Schema

Every sensor payload follows one canonical Pydantic model (`SensorReading`):

```json
{
  "timestamp": "2026-08-21T10:15:00",
  "node_id": "NODE_001",
  "latitude": 13.0827,
  "longitude": 80.2707,
  "grid_id": "A1",
  "soil_moisture_15": 22.4,
  "soil_moisture_30": 27.1,
  "soil_moisture_60": 31.8,
  "soil_temperature": 27.5,
  "electrical_conductivity": 1.14,
  "air_temperature": 31.2,
  "relative_humidity": 58.4,
  "solar_radiation": 720.0,
  "wind_speed": 2.8,
  "leaf_temperature": 34.1,
  "sap_flow": 0.42,
  "source": "simulation",
  "red": 0.06,
  "red_edge": 0.22,
  "nir": 0.75
}
```

---

## 3. Feature Engineering Formulations

### A. Vapor Pressure Deficit (VPD)
Measures the drying capacity of the air (in $\text{kPa}$):
$$e_s(T_{air}) = 0.61078 \times \exp\left(\frac{17.27 \times T_{air}}{T_{air} + 237.3}\right)$$
$$e_a = e_s(T_{air}) \times \left(\frac{RH}{100}\right)$$
$$VPD = e_s(T_{air}) - e_a$$

### B. Crop Water Stress Index (CWSI)
Standardizes canopy thermal response against non-stressed and non-transpiring baselines:
$$dT = T_{leaf} - T_{air}$$
$$dT_{lower} = a + b \times VPD \quad (a=1.5, b=-1.2)$$
$$dT_{upper} = 4.5 + \left(\frac{\text{Solar Radiation}}{1000}\right) \times 1.5$$
$$CWSI = \text{clamp}\left(\frac{dT - dT_{lower}}{dT_{upper} - dT_{lower}}, 0.0, 1.0\right)$$

### C. Vegetation Reflectance Indices (NDVI & NDRE)
$$NDVI = \frac{\text{NIR} - \text{Red}}{\text{NIR} + \text{Red}}$$
$$NDRE = \frac{\text{NIR} - \text{RedEdge}}{\text{NIR} + \text{RedEdge}}$$

---

## 4. Machine Learning & Multi-Sensor Fusion

- **Algorithm**: `RandomForestClassifier` (`n_estimators=120`, `class_weight='balanced'`)
- **Input Features (15)**:
  `soil_moisture_15`, `soil_moisture_30`, `soil_moisture_60`, `soil_temperature`, `electrical_conductivity`, `air_temperature`, `relative_humidity`, `solar_radiation`, `wind_speed`, `leaf_temperature`, `sap_flow`, `vpd`, `cwsi`, `ndvi`, `ndre`
- **Output**: 4-class probabilities + Gini impurity feature importances for real-time explainability.
- **Edge Deployment**: Serialized to `backend/app/ml/model.joblib` and `backend/app/ml/metadata.json` for completely local offline execution (no external cloud AI calls required).

---

## 5. Stress Decision Engine

To prevent false irrigation triggers:
- **Water Stress Probability Threshold**: $\ge 0.75$ ($75\%$)
- **Consecutive Confirmations**: Required $3$ consecutive readings above threshold
- **Cooldown Interval**: 300 seconds ($5$ minutes)
- **Manual Overrides**: Zone valve states can be toggled manually or governed automatically.
- **Hardware Safety**: When `source: "simulation"`, valves update simulated state without activating physical actuators.

---

## 6. Quick Start & Execution Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ / npm

### Step 1: Install Dependencies

```bash
# Install Python backend dependencies
pip install -r backend/requirements.txt

# Install React frontend dependencies
cd frontend && npm install && cd ..
```

### Step 2: Generate Dataset & Train ML Model

```bash
# Generate synthetic dataset (12,000 samples)
python scripts/generate_dataset.py --samples 12000

# Train Random Forest classifier & output real measured metrics
python scripts/train_model.py
```

### Step 3: Run Backend Server

```bash
# Run FastAPI server on port 8000
PYTHONPATH=backend python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation available at `http://127.0.0.1:8000/docs`.

### Step 4: Run Frontend Dashboard

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173` in your browser.

### Step 5: Run Standalone Simulation (Optional)

```bash
# Stream real-time simulated telemetry packets from 15 nodes
python scripts/run_simulation.py --interval 3.0 --count 20
```

*(You can also click **"START SIMULATION"** directly inside the web dashboard to start the background telemetry stream).*

---

## 7. Running the Automated Test Suite

```bash
PYTHONPATH=backend pytest -v tests/
```

Test suite verifies:
- `test_features.py`: VPD, CWSI, NDVI, NDRE, and fusion vector generation
- `test_ml.py`: Preprocessing, imputation, Random Forest inference, probability bounds
- `test_stress_engine.py`: Temporal hysteresis, consecutive count rule, cooldown, recommendations
- `test_api.py`: FastAPI endpoints (`/api/sensor-data`, `/api/predict`, `/api/field/grid`, `/api/irrigation/control`, `/api/multispectral/process`)
- `test_e2e.py`: End-to-end flow from telemetry ingestion to grid state update and alert generation

---

## 8. API Endpoint Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/sensor-data` | Ingest sensor telemetry from ESP32 / LoRaWAN / Simulator |
| `POST` | `/api/sensor-data/batch` | Batch ingest readings from multiple field nodes |
| `POST` | `/api/predict` | Direct ML inference on sensor packet |
| `GET` | `/api/field/grid` | Spatial 3x5 grid state, zone classifications, and statistics |
| `GET` | `/api/field/cell/{grid_id}` | Detailed telemetry history for a specific grid cell |
| `GET` | `/api/irrigation/status` | Active valves, system mode (AUTO/MANUAL), recommendations |
| `POST` | `/api/irrigation/control` | Manual valve override or system mode toggle |
| `POST` | `/api/multispectral/process` | Calculate NDVI and NDRE from optical bands |
| `GET` | `/api/ml/metrics` | Measured accuracy, confusion matrix, and feature importances |
| `POST` | `/api/simulation/toggle` | Start/stop continuous background simulation stream |
| `POST` | `/api/simulation/step` | Trigger single synchronized field telemetry cycle |
| `GET` | `/api/alerts` | Live stress alert event stream |

---

## 9. Hardware Integration Contract (ESP32 & LoRaWAN)

To transition from the simulator to physical hardware:

1. **No ML or Dashboard Changes**: The backend endpoint `/api/sensor-data` is identical.
2. **ESP32 Firmware Payload**: Program ESP32 / LoRaWAN gateway to serialize readings into JSON matching the `SensorReading` schema.
3. **HTTP / Gateway Bridge**:
   ```cpp
   // Example ESP32 HTTP POST payload
   String payload = "{"
     "\"node_id\":\"NODE_001\","
     "\"latitude\":13.0827,"
     "\"longitude\":80.2707,"
     "\"grid_id\":\"A1\","
     "\"soil_moisture_15\":" + String(sm15) + ","
     "\"soil_moisture_30\":" + String(sm30) + ","
     "\"soil_moisture_60\":" + String(sm60) + ","
     "\"soil_temperature\":" + String(soilTemp) + ","
     "\"electrical_conductivity\":" + String(ec) + ","
     "\"air_temperature\":" + String(airTemp) + ","
     "\"relative_humidity\":" + String(rh) + ","
     "\"solar_radiation\":" + String(solar) + ","
     "\"wind_speed\":" + String(wind) + ","
     "\"leaf_temperature\":" + String(leafTemp) + ","
     "\"sap_flow\":" + String(sapFlow) + ","
     "\"source\":\"hardware\""
   "}";

   http.begin("http://<edge-gateway-ip>:8000/api/sensor-data");
   http.addHeader("Content-Type", "application/json");
   int httpResponseCode = http.POST(payload);
   ```
4. **Source Distinction**: Setting `"source": "hardware"` flags physical telemetry.

---

## 10. Multispectral Drone Integration

The `/api/multispectral/process` endpoint accepts:
- `red`: Red band reflectance ($660\text{nm}$)
- `red_edge`: RedEdge band reflectance ($705\text{nm}$)
- `nir`: Near-Infrared band reflectance ($840\text{nm}$)

Calculates $NDVI$ and $NDRE$ and provides canopy density and nitrogen/chlorophyll status assessments.

---

## 11. Limitations & Simulation Validation Notice

> [!NOTE]
> **Validation Notice**:
> The synthetic training dataset generated in this repository models established agronomic and biophysical relationships (such as Tetens vapor pressure equations, empirical CWSI baselines, and diurnal environmental cycles) for the purpose of validating the software architecture, edge inference pipeline, and decision engine.
> 
> Synthetic simulation results must not be represented as real-world field-trial validation. Prior to commercial deployment in specific crop varietals (e.g. maize, grapevines, cotton), the CWSI non-water-stressed baselines ($a, b$) and soil moisture thresholds should be calibrated against local in-situ field measurements.
