import React, { useState } from 'react';
import { GridCellState } from '../types';
import { 
  X, 
  Droplets, 
  Power,
  MapPin,
  Cpu
} from 'lucide-react';
import { controlIrrigation } from '../services/api';

interface Props {
  cell: GridCellState;
  onClose: () => void;
  onRefresh: () => void;
}

export const CellDetailModal: React.FC<Props> = ({ cell, onClose, onRefresh }) => {
  const [loading, setLoading] = useState(false);

  const handleValveToggle = async (action: 'OPEN' | 'CLOSE') => {
    setLoading(true);
    try {
      await controlIrrigation({ zone: cell.grid_id, action });
      onRefresh();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const s = cell.sensor_values;
  const d = cell.derived_features;
  const rec = cell.recommendation;

  return (
    <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl p-6 relative animate-in fade-in zoom-in-95">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-white">Zone {cell.grid_id} Diagnostics</h2>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                {cell.node_id}
              </span>
            </div>
            <p className="text-xs text-slate-400 flex items-center gap-1.5 mt-0.5">
              <MapPin className="w-3.5 h-3.5 text-slate-500" />
              GPS: {cell.latitude.toFixed(4)}° N, {cell.longitude.toFixed(4)}° E | Updated: {new Date(cell.last_updated).toLocaleTimeString()}
            </p>
          </div>
        </div>

        {/* AI Stress & Recommendation Summary */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">AI Classification</span>
            <span className="text-xs font-mono text-emerald-400">Confidence: {(cell.confidence * 100).toFixed(1)}%</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="text-lg font-extrabold text-white">
              {cell.current_stress}
            </div>
            <div className="text-xs px-2.5 py-1 rounded-md font-bold bg-slate-800 text-slate-200 border border-slate-700">
              Action: {rec.recommendation}
            </div>
          </div>
          <p className="text-xs text-slate-300 mt-2 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/80">
            {rec.reason}
          </p>
        </div>

        {/* Telemetry Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
          
          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
            <div className="text-[11px] text-slate-400">Soil Moisture (15/30/60 cm)</div>
            <div className="text-sm font-bold text-white mt-1">
              {s.soil_moisture_15.toFixed(1)}% / {s.soil_moisture_30.toFixed(1)}% / {s.soil_moisture_60.toFixed(1)}%
            </div>
          </div>

          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
            <div className="text-[11px] text-slate-400">Soil Temp & EC</div>
            <div className="text-sm font-bold text-white mt-1">
              {s.soil_temperature.toFixed(1)}°C | {s.electrical_conductivity.toFixed(2)} dS/m
            </div>
          </div>

          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
            <div className="text-[11px] text-slate-400">Leaf vs Air Temp (ΔT)</div>
            <div className="text-sm font-bold text-white mt-1">
              {s.leaf_temperature.toFixed(1)}°C / {s.air_temperature.toFixed(1)}°C 
              <span className={`ml-1 text-xs ${(s.leaf_temperature - s.air_temperature) > 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                ({(s.leaf_temperature - s.air_temperature) > 0 ? '+' : ''}{(s.leaf_temperature - s.air_temperature).toFixed(1)}°)
              </span>
            </div>
          </div>

          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
            <div className="text-[11px] text-slate-400">Sap Flow Transpiration</div>
            <div className="text-sm font-bold text-white mt-1">
              {s.sap_flow.toFixed(3)} relative rate
            </div>
          </div>

          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
            <div className="text-[11px] text-slate-400">VPD & CWSI Indices</div>
            <div className="text-sm font-bold text-white mt-1">
              VPD: {d.vpd.toFixed(2)} kPa | CWSI: {d.cwsi.toFixed(2)}
            </div>
          </div>

          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
            <div className="text-[11px] text-slate-400">Multispectral (NDVI / NDRE)</div>
            <div className="text-sm font-bold text-white mt-1">
              NDVI: {d.ndvi.toFixed(2)} | NDRE: {d.ndre.toFixed(2)}
            </div>
          </div>

        </div>

        {/* Manual Actuator Controls */}
        <div className="border-t border-slate-800 pt-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400">Valve Actuation:</span>
            <span className={`text-xs font-bold px-2 py-0.5 rounded ${
              cell.valve_state === 'OPEN' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'bg-slate-800 text-slate-400'
            }`}>
              {cell.valve_state}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => handleValveToggle('OPEN')}
              disabled={loading || cell.valve_state === 'OPEN'}
              className="px-3 py-1.5 rounded-lg text-xs font-bold bg-cyan-600 hover:bg-cyan-500 text-white disabled:opacity-40 transition flex items-center gap-1"
            >
              <Droplets className="w-3.5 h-3.5" /> Manual Open
            </button>
            <button
              onClick={() => handleValveToggle('CLOSE')}
              disabled={loading || cell.valve_state === 'CLOSED'}
              className="px-3 py-1.5 rounded-lg text-xs font-bold bg-slate-800 hover:bg-slate-700 text-slate-200 disabled:opacity-40 transition flex items-center gap-1 border border-slate-700"
            >
              <Power className="w-3.5 h-3.5" /> Manual Close
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};
