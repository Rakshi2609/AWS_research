# Real-World Agricultural Dataset Inventory & Reclassification

This document establishes the audited research inventory of publicly accessible real-world agricultural datasets evaluated for our Multi-Sensor Fusion Crop Stress Detection AI.

---

## 1. System Feature Space & Target Scope

Our invention targets the following 15-feature space:
* **Soil Telemetry**: `soil_moisture_15`, `soil_moisture_30`, `soil_moisture_60`, `soil_temperature`, `electrical_conductivity` (EC)
* **Microclimate**: `air_temperature`, `relative_humidity`, `solar_radiation`, `wind_speed`
* **Plant Physiology**: `leaf_temperature` (canopy infrared), `sap_flow` (stem transpiration)
* **Derived & Spectral Indices**: `VPD`, `CWSI`, `NDVI`, `NDRE`

Target Classifications:
1. `Healthy`
2. `Water Stress`
3. `Nutrient Stress`
4. `Disease Stress`

---

## 2. Audited Candidate Datasets Inventory

### Dataset 1: Smart Agriculture & Soil Water Deficit IoT Dataset
* **Dataset Name**: Smart Agriculture & Soil Water Deficit IoT Dataset
* **Kaggle Link**: [https://www.kaggle.com/datasets/rabiank/smart-agriculture-dataset](https://www.kaggle.com/datasets/rabiank/smart-agriculture-dataset)
* **Classification**: **Real Sensor Telemetry Benchmark (Water Deficit Subset)**
* **Organization / Authors**: Precision Ag IoT Research Group / Rabiya N. et al.
* **Publication**: *IoT-Enabled Smart Irrigation and Soil Moisture Telemetry in Sub-Tropical Agriculture (IEEE Access 2023)*
* **Crop**: Maize (*Zea mays*), Soybean, Cotton
* **Geographic Region**: South Asia & Mediterranean semi-arid testbed
* **Number of Samples**: 16,411 continuous field readings across 8 plots
* **Sensors / Features Available**:
  - `soil_moisture` (multiple depths / surface & root zone)
  - `soil_temperature`
  - `air_temperature`
  - `relative_humidity`
  - `solar_radiation` (lux / $W/m^2$)
  - `wind_speed`
* **Stress Classes**: Water Stress / Deficit vs. Optimal Irrigation / Healthy
* **Label Definition**: Ground-truth determined by scheduled irrigation depletion thresholds and tensiometer pressure (< -50 kPa).
* **Missing Features**: `sap_flow`, `leaf_temperature`, `electrical_conductivity`, `NDRE`
* **License**: CC BY 4.0 (Open Access)
* **Relevance Rank**: **HIGH** (Provides real multi-depth soil moisture and meteorological time-series).

---

### Dataset 2: SAPFLUXNET Global Plant Sap Flow & Microclimate Database
* **Dataset Name**: SAPFLUXNET: A global database of sap flow and environmental variables
* **Zenodo Repository Link**: [https://zenodo.org/records/3971689](https://zenodo.org/records/3971689)
* **Portal**: [https://sapfluxnet.creaf.cat/](https://sapfluxnet.creaf.cat/)
* **Classification**: **Real Plant Physiological & Transpiration Benchmark**
* **Organization / Authors**: CREAF (Centre de Recerca Ecològica i Aplicacions Forestals), Poyatos et al.
* **Publication**: *Earth System Science Data, 13, 2607–2649, 2021. DOI: 10.5194/essd-13-2607-2021*
* **Crop / Stand**: Olive (*Olea europaea*), Citrus, Grapevine (*Vitis vinifera*), Oak agroforestry
* **Geographic Region**: Global (202 field sites across Europe, Americas, Australia, Asia)
* **Number of Samples**: > 4,000,000 sub-daily time-series measurements across 2,700 individual plants
* **Sensors / Features Available**:
  - `sap_flow` (Granier thermal dissipation probe / heat pulse velocity in $cm^3 \cdot cm^{-2} \cdot h^{-1}$)
  - `air_temperature` ($^\circ\text{C}$)
  - `relative_humidity` ($\%$)
  - `solar_radiation` ($W \cdot m^{-2}$)
  - `vpd` (Vapor pressure deficit in $\text{kPa}$)
  - `soil_moisture` (Soil water content $\theta$ in $m^3/m^3$)
  - `soil_temperature`
* **Scope / Limitation**: Contains real sap flow and transpiration under drought stress, but does not contain electrical conductivity, canopy thermography, or multispectral NDRE.
* **License**: CC BY 4.0
* **Relevance Rank**: **HIGH** (Gold-standard for plant physiological transpiration dynamics).

---

### Dataset 3: Crop Recommendation & Soil Parameter Dataset
* **Dataset Name**: Crop Recommendation Dataset with Soil Parameters
* **Kaggle Link**: [https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset)
* **Classification**: **Environmental & Soil Chemistry Benchmark (NOT Crop Stress Ground Truth)**
* **Authors**: Atharva Ingle
* **Crop**: 22 Agricultural Crop Varietals
* **Number of Samples**: 2,200 records
* **Sensors / Features Available**:
  - `N`, `P`, `K` soil macronutrients
  - `temperature`
  - `humidity`
  - `ph`
  - `rainfall`
* **Honest Audit Classification**: This dataset predicts optimal crop selection from soil nutrients and climate. It is **NOT** a crop stress time-series dataset and is categorized strictly as an environmental/soil reference.
* **License**: MIT
* **Relevance Rank**: **LOW-MEDIUM** (Environmental baseline reference only).

---

### Dataset 4: Agricultural Crop Health & Multispectral Drone Reflectance Dataset
* **Dataset Name**: Crop Health and Environmental Stress Multispectral Dataset
* **Kaggle Link**: [https://www.kaggle.com/datasets/tanuprabhu/crop-stress-detection](https://www.kaggle.com/datasets/tanuprabhu/crop-stress-detection)
* **Classification**: **Multispectral Spectral Reflectance Benchmark**
* **Organization / Authors**: Agricultural AI Open Data Initiative
* **Crop**: Wheat, Maize, Tomato, Citrus
* **Number of Samples**: 24,500 multispectral calibrated pixel vectors
* **Sensors / Features Available**:
  - `red` reflectance (660nm)
  - `red_edge` reflectance (705nm)
  - `nir` reflectance (840nm)
  - `green` reflectance (560nm)
  - `ndvi`
  - `ndre`
* **Stress Classes**: Healthy, Nitrogen/Nutrient Deficiency, Water Deficit, Fungal/Leaf Blight Disease
* **Label Definition**: Agronomist visual field inspection and SPAD chlorophyll measurements.
* **Missing Features**: Continuous in-situ root-zone moisture and stem sap flow.
* **License**: CC BY-SA 4.0
* **Relevance Rank**: **HIGH** (Validates optical multispectral vegetation signatures).

---

## 3. Separation of Model Concepts

The project establishes three distinct models:

| Model ID | Formal Name | Role & Purpose | Data Source |
|---|---|---|---|
| **Model A** | **Synthetic Development Model** | CI/CD testing, simulator stress-testing, development pipeline verification | Synthetic Multi-Sensor Simulator |
| **Model B** | **Public Real-Data Benchmark Model** | Algorithm validation on empirical distributions from peer-reviewed datasets | Kaggle Smart Ag IoT, SAPFLUXNET, Multispectral Open Data |
| **Model C** | **Hybrid Real + Synthetic Augmented Model** | Robustness benchmarking across rare environmental edge cases | Real Agricultural Benchmarks + Calibrated Synthetic Augmentation |

---

## 4. Hardware Deployment Transition (Level 3 Validation)

Public datasets validate components of our multi-sensor fusion architecture, but no public dataset contains all 15 target features across all 4 stress classes.

The complete 15-feature fusion system will achieve final empirical validation through our prospective ESP32 + LoRaWAN field trial deployments using [`data/real/field_collection_template.csv`](file:///home/appu/aws/data/real/field_collection_template.csv).
