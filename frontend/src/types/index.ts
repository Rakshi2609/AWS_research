export type StressType = 'Healthy' | 'Water Stress' | 'Nutrient Stress' | 'Disease Stress';

export interface DerivedFeatures {
  vpd: number;
  cwsi: number;
  ndvi: number;
  ndre: number;
}

export interface SensorValues {
  soil_moisture_15: number;
  soil_moisture_30: number;
  soil_moisture_60: number;
  soil_temperature: number;
  electrical_conductivity: number;
  air_temperature: number;
  relative_humidity: number;
  solar_radiation: number;
  wind_speed: number;
  leaf_temperature: number;
  sap_flow: number;
}

export interface IrrigationRecommendation {
  zone: string;
  stress: string;
  confidence: number;
  recommendation: string;
  reason: string;
  consecutive_hits: number;
  valve_action: string | null;
}

export interface GridCellState {
  grid_id: string;
  row: string;
  col: number;
  latitude: number;
  longitude: number;
  node_id: string;
  current_stress: StressType;
  confidence: number;
  probabilities: Record<StressType, number>;
  sensor_values: SensorValues;
  derived_features: DerivedFeatures;
  recommendation: IrrigationRecommendation;
  valve_state: 'OPEN' | 'CLOSED';
  last_updated: string;
  consecutive_water_stress_count: number;
}

export interface FieldGridResponse {
  cells: GridCellState[];
  total_zones: number;
  healthy_count: number;
  water_stress_count: number;
  nutrient_stress_count: number;
  disease_stress_count: number;
  active_valves_count: number;
  system_mode: 'AUTO' | 'MANUAL';
  simulation_active: boolean;
  timestamp: string;
}

export interface AlertItem {
  id: string;
  timestamp: string;
  grid_id: string;
  stress_type: StressType;
  confidence: number;
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  message: string;
  action_taken: string;
}

export interface FeatureImportanceItem {
  feature: string;
  importance: number;
}

export interface MLMetricsResponse {
  accuracy: number;
  precision_macro: number;
  recall_macro: number;
  f1_macro: number;
  confusion_matrix: number[][];
  classification_report: Record<string, any>;
  feature_importance: FeatureImportanceItem[];
  class_names: string[];
  feature_names: string[];
  training_samples: number;
  test_samples: number;
  model_version: string;
  dataset_type?: string;
  dataset_source?: string;
  split_strategy?: string;
  trained_at: string;
}

export interface MultispectralProcessResponse {
  ndvi: number;
  ndre: number;
  chlorophyll_status: string;
  canopy_density: string;
  notes: string;
}
