import React from 'react';
import { GridCellState } from '../types';
import { 
  Droplets, 
  Thermometer, 
  Sun, 
  Gauge, 
  Activity, 
  Layers,
  Zap
} from 'lucide-react';

interface Props {
  cell: GridCellState | null;
}

export const SensorPanel: React.FC<Props> = ({ cell }) => {
  if (!cell) {
    return (
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 text-center text-slate-500">
        Select a field zone to inspect real-time sensor telemetry.
      </div>
    );
  }

  const s = cell.sensor_values;

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl">
      
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-emerald-400" />
          <h2 className="text-base font-bold text-white">
            Sensor Telemetry — Zone {cell.grid_id}
          </h2>
        </div>
        <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
          Node: {cell.node_id}
        </span>
      </div>

      {/* Grid of Telemetry Sensors */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        
        {/* Soil Moisture 15cm */}
        <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span className="flex items-center gap-1.5">
              <Droplets className="w-3.5 h-3.5 text-blue-400" /> SM 15 cm
            </span>
            <span className="text-[10px] text-slate-500 font-mono">Vol %</span>
          </div>
          <div className="text-lg font-extrabold text-white">
            {s.soil_moisture_15.toFixed(1)}%
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
            <div 
              className={`h-full rounded-full ${s.soil_moisture_15 < 20 ? 'bg-red-500' : 'bg-blue-500'}`} 
              style={{ width: `${Math.min(100, s.soil_moisture_15 * 2)}%` }}
            />
          </div>
        </div>

        {/* Soil Moisture 30cm */}
        <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span className="flex items-center gap-1.5">
              <Droplets className="w-3.5 h-3.5 text-blue-400" /> SM 30 cm
            </span>
            <span className="text-[10px] text-slate-500 font-mono">Vol %</span>
          </div>
          <div className="text-lg font-extrabold text-white">
            {s.soil_moisture_30.toFixed(1)}%
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
            <div 
              className={`h-full rounded-full ${s.soil_moisture_30 < 22 ? 'bg-red-500' : 'bg-blue-500'}`} 
              style={{ width: `${Math.min(100, s.soil_moisture_30 * 2)}%` }}
            />
          </div>
        </div>

        {/* Soil Moisture 60cm */}
        <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span className="flex items-center gap-1.5">
              <Droplets className="w-3.5 h-3.5 text-blue-400" /> SM 60 cm
            </span>
            <span className="text-[10px] text-slate-500 font-mono">Vol %</span>
          </div>
          <div className="text-lg font-extrabold text-white">
            {s.soil_moisture_60.toFixed(1)}%
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
            <div 
              className={`h-full rounded-full ${s.soil_moisture_60 < 25 ? 'bg-red-500' : 'bg-blue-500'}`} 
              style={{ width: `${Math.min(100, s.soil_moisture_60 * 2)}%` }}
            />
          </div>
        </div>

        {/* Soil Temperature */}
        <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span className="flex items-center gap-1.5">
              <Thermometer className="w-3.5 h-3.5 text-amber-400" /> Soil Temp
            </span>
            <span className="text-[10px] text-slate-500 font-mono">°C</span>
          </div>
          <div className="text-lg font-extrabold text-white">
            {s.soil_temperature.toFixed(1)} °C
          </div>
          <div className="text-[10px] text-slate-400 mt-1">Root zone thermal status</div>
        </div>

        {/* Electrical Conductivity */}
        <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span className="flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-yellow-400" /> Soil EC
            </span>
            <span className="text-[10px] text-slate-500 font-mono">dS/m</span>
          </div>
          <div className="text-lg font-extrabold text-white">
            {s.electrical_conductivity.toFixed(2)}
          </div>
          <div className="text-[10px] text-slate-400 mt-1">
            {s.electrical_conductivity < 0.6 ? 'Nutrient Deficient' : s.electrical_conductivity > 3.0 ? 'Saline / Toxicity' : 'Optimal Salinity'}
          </div>
        </div>

        {/* Leaf Temp vs Air Temp */}
        <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span className="flex items-center gap-1.5">
              <Thermometer className="w-3.5 h-3.5 text-emerald-400" /> Leaf Temp
            </span>
            <span className="text-[10px] text-slate-500 font-mono">IR Sensor</span>
          </div>
          <div className="text-lg font-extrabold text-white">
            {s.leaf_temperature.toFixed(1)} °C
          </div>
          <div className="text-[10px] text-slate-400 mt-1">
            Air: {s.air_temperature.toFixed(1)} °C (ΔT: {(s.leaf_temperature - s.air_temperature).toFixed(1)}°)
          </div>
        </div>

        {/* Sap Flow */}
        <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span className="flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-cyan-400" /> Sap Flow
            </span>
            <span className="text-[10px] text-slate-500 font-mono">Stem probe</span>
          </div>
          <div className="text-lg font-extrabold text-white">
            {s.sap_flow.toFixed(3)}
          </div>
          <div className="text-[10px] text-slate-400 mt-1">
            {s.sap_flow < 0.3 ? 'Severely Restricted' : s.sap_flow < 0.6 ? 'Moderate' : 'Active Transpiration'}
          </div>
        </div>

        {/* Relative Humidity & Air Temp */}
        <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span className="flex items-center gap-1.5">
              <Gauge className="w-3.5 h-3.5 text-teal-400" /> Humidity / Air
            </span>
          </div>
          <div className="text-lg font-extrabold text-white">
            {s.relative_humidity.toFixed(1)}% <span className="text-xs font-normal text-slate-400">RH</span>
          </div>
          <div className="text-[10px] text-slate-400 mt-1">
            Air: {s.air_temperature.toFixed(1)} °C
          </div>
        </div>

        {/* Solar Radiation & Wind */}
        <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span className="flex items-center gap-1.5">
              <Sun className="w-3.5 h-3.5 text-orange-400" /> Solar & Wind
            </span>
          </div>
          <div className="text-lg font-extrabold text-white">
            {s.solar_radiation.toFixed(0)} <span className="text-xs font-normal text-slate-400">W/m²</span>
          </div>
          <div className="text-[10px] text-slate-400 mt-1">
            Wind: {s.wind_speed.toFixed(1)} m/s
          </div>
        </div>

      </div>
    </div>
  );
};
