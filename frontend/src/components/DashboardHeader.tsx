import React, { useState } from 'react';
import { 
  Sprout, 
  Play, 
  RotateCw, 
  SlidersHorizontal,
  Radio
} from 'lucide-react';
import { toggleSimulation, stepSimulation, controlIrrigation } from '../services/api';

interface Props {
  simulationActive: boolean;
  systemMode: 'AUTO' | 'MANUAL';
  totalZones: number;
  onRefresh: () => void;
}

export const DashboardHeader: React.FC<Props> = ({
  simulationActive,
  systemMode,
  totalZones,
  onRefresh
}) => {
  const [loadingSim, setLoadingSim] = useState(false);
  const [loadingMode, setLoadingMode] = useState(false);

  const handleToggleSimulation = async () => {
    setLoadingSim(true);
    try {
      await toggleSimulation(!simulationActive, 2.5);
      onRefresh();
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingSim(false);
    }
  };

  const handleStepSimulation = async () => {
    setLoadingSim(true);
    try {
      await stepSimulation();
      onRefresh();
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingSim(false);
    }
  };

  const handleToggleSystemMode = async () => {
    setLoadingMode(true);
    try {
      const newMode = systemMode === 'AUTO' ? 'MANUAL' : 'AUTO';
      await controlIrrigation({ system_mode: newMode });
      onRefresh();
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingMode(false);
    }
  };

  return (
    <header className="bg-slate-900/90 backdrop-blur border-b border-slate-800 sticky top-0 z-30 px-4 lg:px-8 py-3.5">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
        
        {/* Brand & Subtitle */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-lg shadow-emerald-950/50">
            <Sprout className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-extrabold text-white tracking-tight">CropStress AI</h1>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800">
                Edge v1.0
              </span>
            </div>
            <p className="text-xs text-slate-400">Multi-Sensor Fusion & Irrigation Decision System ({totalZones} Field Nodes)</p>
          </div>
        </div>

        {/* Global Controls */}
        <div className="flex flex-wrap items-center gap-2.5">
          
          {/* Mode Switcher */}
          <button
            onClick={handleToggleSystemMode}
            disabled={loadingMode}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
              systemMode === 'AUTO'
                ? 'bg-blue-950/60 border-blue-700/60 text-blue-300 hover:bg-blue-900/80'
                : 'bg-amber-950/60 border-amber-700/60 text-amber-300 hover:bg-amber-900/80'
            }`}
            title="Toggle autonomous decision engine or manual valve control"
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            Mode: <span className="font-bold">{systemMode}</span>
          </button>

          {/* Standalone Step */}
          <button
            onClick={handleStepSimulation}
            disabled={loadingSim}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            title="Trigger one simulation telemetric cycle"
          >
            <RotateCw className={`w-3.5 h-3.5 ${loadingSim ? 'animate-spin' : ''}`} />
            Step Cycle
          </button>

          {/* Simulation Mode Toggle */}
          <button
            onClick={handleToggleSimulation}
            disabled={loadingSim}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-bold transition shadow-sm ${
              simulationActive
                ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-900/40 animate-pulse'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700'
            }`}
          >
            {simulationActive ? (
              <>
                <Radio className="w-3.5 h-3.5 text-white" />
                SIMULATION: LIVE
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 text-emerald-400" />
                START SIMULATION
              </>
            )}
          </button>
        </div>

      </div>
    </header>
  );
};
