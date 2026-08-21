import { 
  FieldGridResponse, 
  AlertItem, 
  MLMetricsResponse, 
  MultispectralProcessResponse,
  GridCellState 
} from '../types';

const API_BASE = '/api';

export async function fetchFieldGrid(): Promise<FieldGridResponse> {
  const res = await fetch(`${API_BASE}/field/grid`);
  if (!res.ok) throw new Error(`Failed to fetch grid: ${res.statusText}`);
  return res.json();
}

export async function fetchCellDetails(gridId: string): Promise<{ current: GridCellState; history: any[] }> {
  const res = await fetch(`${API_BASE}/field/cell/${gridId}`);
  if (!res.ok) throw new Error(`Failed to fetch cell details: ${res.statusText}`);
  return res.json();
}

export async function fetchAlerts(): Promise<AlertItem[]> {
  const res = await fetch(`${API_BASE}/alerts?limit=50`);
  if (!res.ok) throw new Error(`Failed to fetch alerts: ${res.statusText}`);
  return res.json();
}

export async function fetchMLMetrics(): Promise<MLMetricsResponse> {
  const res = await fetch(`${API_BASE}/ml/metrics`);
  if (!res.ok) throw new Error(`Failed to fetch ML metrics: ${res.statusText}`);
  return res.json();
}

export async function toggleSimulation(enabled: boolean, intervalSeconds: number = 3.0): Promise<any> {
  const res = await fetch(`${API_BASE}/simulation/toggle`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ enabled, interval_seconds: intervalSeconds }),
  });
  if (!res.ok) throw new Error(`Failed to toggle simulation: ${res.statusText}`);
  return res.json();
}

export async function stepSimulation(): Promise<any> {
  const res = await fetch(`${API_BASE}/simulation/step`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(`Failed to step simulation: ${res.statusText}`);
  return res.json();
}

export async function controlIrrigation(payload: { zone?: string; action?: string; system_mode?: string }): Promise<any> {
  const res = await fetch(`${API_BASE}/irrigation/control`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Failed to control irrigation: ${res.statusText}`);
  return res.json();
}

export async function processMultispectral(bands: { red: number; red_edge: number; nir: number; green?: number }): Promise<MultispectralProcessResponse> {
  const res = await fetch(`${API_BASE}/multispectral/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(bands),
  });
  if (!res.ok) throw new Error(`Failed to process multispectral bands: ${res.statusText}`);
  return res.json();
}

export async function sendSensorReading(reading: any): Promise<GridCellState> {
  const res = await fetch(`${API_BASE}/sensor-data`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(reading),
  });
  if (!res.ok) throw new Error(`Failed to send sensor reading: ${res.statusText}`);
  return res.json();
}
