import React, { useState } from 'react';
import { FieldGridResponse } from '../types';
import { 
  Droplets, 
  Power, 
  CheckCircle2, 
  AlertCircle
} from 'lucide-react';
import { controlIrrigation } from '../services/api';

interface Props {
  gridData: FieldGridResponse | null;
  onRefresh: () => void;
}

export const IrrigationControl: React.FC<Props> = ({ gridData, onRefresh }) => {
  const [loading, setLoading] = useState(false);

  if (!gridData) return null;

  const handleModeSwitch = async (mode: 'AUTO' | 'MANUAL') => {
    setLoading(true);
    try {
      await controlIrrigation({ system_mode: mode });
      onRefresh();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleZoneValve = async (zone: string, action: 'OPEN' | 'CLOSE') => {
    setLoading(true);
    try {
      await controlIrrigation({ zone, action });
      onRefresh();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const recommendedCells = gridData.cells.filter(
    c => c.recommendation.recommendation === 'IRRIGATE'
  );

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl">
      
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2">
          <Droplets className="w-4 h-4 text-cyan-400" />
          <h2 className="text-base font-bold text-white">
            Smart Irrigation & Solenoid Control
          </h2>
        </div>

        {/* Mode Selector */}
        <div className="flex items-center gap-2 bg-slate-950 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => handleModeSwitch('AUTO')}
            disabled={loading || gridData.system_mode === 'AUTO'}
            className={`px-3 py-1 rounded-lg text-xs font-bold transition ${
              gridData.system_mode === 'AUTO'
                ? 'bg-blue-600 text-white shadow'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            AUTO (AI Governed)
          </button>
          <button
            onClick={() => handleModeSwitch('MANUAL')}
            disabled={loading || gridData.system_mode === 'MANUAL'}
            className={`px-3 py-1 rounded-lg text-xs font-bold transition ${
              gridData.system_mode === 'MANUAL'
                ? 'bg-amber-600 text-white shadow'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            MANUAL OVERRIDE
          </button>
        </div>
      </div>

      {/* Recommended Zones Banner */}
      <div className="bg-slate-950/80 border border-slate-800/80 rounded-xl p-3.5 mb-4">
        <div className="text-xs text-slate-400 uppercase tracking-wider font-semibold mb-2">
          Irrigation Recommendations
        </div>
        {recommendedCells.length === 0 ? (
          <div className="text-xs text-slate-400 flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            No active zones requiring immediate irrigation.
          </div>
        ) : (
          <div className="flex flex-wrap gap-2">
            {recommendedCells.map(c => (
              <span
                key={c.grid_id}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-red-950/80 border border-red-700/60 text-xs font-bold text-red-200 animate-pulse"
              >
                <AlertCircle className="w-3.5 h-3.5 text-red-400" />
                Zone {c.grid_id} (Water Stress ≥ 75% for 3+ cycles)
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Zone Solenoids 15 Grid Matrix */}
      <div className="text-xs font-semibold text-slate-300 mb-2">
        Zone Solenoid Valves Matrix:
      </div>

      <div className="grid grid-cols-3 sm:grid-cols-5 gap-2">
        {gridData.cells.map(cell => {
          const isOpen = cell.valve_state === 'OPEN';
          return (
            <div
              key={cell.grid_id}
              className={`p-2.5 rounded-xl border flex flex-col justify-between text-xs ${
                isOpen 
                  ? 'bg-cyan-950/50 border-cyan-500/60 text-cyan-200' 
                  : 'bg-slate-950 border-slate-800/80 text-slate-400'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-white">Zone {cell.grid_id}</span>
                <span className={`text-[10px] font-mono font-extrabold ${isOpen ? 'text-cyan-400 animate-pulse' : 'text-slate-500'}`}>
                  {isOpen ? 'OPEN' : 'OFF'}
                </span>
              </div>

              <div className="mt-2 flex gap-1">
                <button
                  onClick={() => handleZoneValve(cell.grid_id, isOpen ? 'CLOSE' : 'OPEN')}
                  disabled={loading}
                  className={`w-full py-1 rounded text-[10px] font-bold transition flex items-center justify-center gap-1 ${
                    isOpen
                      ? 'bg-red-950 hover:bg-red-900 text-red-300 border border-red-800'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
                  }`}
                >
                  <Power className="w-3 h-3" /> {isOpen ? 'Close' : 'Open'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <p className="text-[10px] text-slate-500 mt-3 font-mono">
        Safety Protection: In simulation mode, valves update internal state without physical hardware actuation.
      </p>

    </div>
  );
};
