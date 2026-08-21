import React, { useState } from 'react';
import { GridCellState, StressType } from '../types';
import { Droplets, Info, MapPin } from 'lucide-react';
import { CellDetailModal } from './CellDetailModal';

interface Props {
  cells: GridCellState[];
  selectedCell: GridCellState | null;
  onSelectCell: (cell: GridCellState) => void;
  onRefresh: () => void;
}

export const FieldGridMap: React.FC<Props> = ({
  cells,
  selectedCell,
  onSelectCell,
  onRefresh
}) => {
  const [modalCell, setModalCell] = useState<GridCellState | null>(null);

  // Group cells by rows (A, B, C)
  const rows = ['A', 'B', 'C'];

  const getStressColorClasses = (stress: StressType, isSelected: boolean) => {
    let base = '';
    switch (stress) {
      case 'Healthy':
        base = 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300 hover:border-emerald-400 hover:bg-emerald-900/50';
        break;
      case 'Water Stress':
        base = 'bg-red-950/50 border-red-500/60 text-red-300 hover:border-red-400 hover:bg-red-900/60 glow-water animate-pulse';
        break;
      case 'Nutrient Stress':
        base = 'bg-yellow-950/40 border-yellow-500/50 text-yellow-300 hover:border-yellow-400 hover:bg-yellow-900/50 glow-nutrient';
        break;
      case 'Disease Stress':
        base = 'bg-purple-950/40 border-purple-500/50 text-purple-300 hover:border-purple-400 hover:bg-purple-900/50 glow-disease';
        break;
      default:
        base = 'bg-slate-900 border-slate-800 text-slate-300';
    }

    if (isSelected) {
      base += ' ring-2 ring-white ring-offset-2 ring-offset-slate-950 scale-[1.02] shadow-xl';
    }
    return base;
  };

  const getBadgeColor = (stress: StressType) => {
    switch (stress) {
      case 'Healthy': return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
      case 'Water Stress': return 'bg-red-500/20 text-red-300 border-red-500/30';
      case 'Nutrient Stress': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
      case 'Disease Stress': return 'bg-purple-500/20 text-purple-300 border-purple-500/30';
    }
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 mb-6 shadow-xl">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <MapPin className="w-4 h-4 text-emerald-400" />
            Spatial Field Stress Grid (3×5 Matrix)
          </h2>
          <p className="text-xs text-slate-400">
            Real-time classification per LoRaWAN node. Click any cell to select or inspect telemetry.
          </p>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center gap-2 text-[11px]">
          <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-700/50 text-emerald-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span> Healthy
          </span>
          <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-red-950/80 border border-red-700/50 text-red-300">
            <span className="w-2 h-2 rounded-full bg-red-400 animate-ping"></span> Water Stress
          </span>
          <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-yellow-950/80 border border-yellow-700/50 text-yellow-300">
            <span className="w-2 h-2 rounded-full bg-yellow-400"></span> Nutrient Stress
          </span>
          <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-purple-950/80 border border-purple-700/50 text-purple-300">
            <span className="w-2 h-2 rounded-full bg-purple-400"></span> Disease
          </span>
        </div>
      </div>

      {/* 3x5 Field Grid Layout */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
        {rows.map(row => {
          const rowCells = cells
            .filter(c => c.row === row)
            .sort((a, b) => a.col - b.col);

          return rowCells.map(cell => {
            const isSelected = selectedCell?.grid_id === cell.grid_id;
            return (
              <div
                key={cell.grid_id}
                onClick={() => onSelectCell(cell)}
                className={`border rounded-xl p-3 cursor-pointer transition-all duration-150 flex flex-col justify-between min-h-[135px] ${getStressColorClasses(
                  cell.current_stress,
                  isSelected
                )}`}
              >
                {/* Top Row: Zone & Node ID & Valve */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className="text-sm font-extrabold text-white tracking-wide">
                      Zone {cell.grid_id}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {cell.node_id}
                    </span>
                  </div>
                  {cell.valve_state === 'OPEN' && (
                    <span className="flex items-center gap-1 text-[10px] font-bold px-1.5 py-0.5 rounded bg-cyan-500 text-slate-950 animate-bounce">
                      <Droplets className="w-3 h-3" /> VALV
                    </span>
                  )}
                </div>

                {/* Center: Stress Badge & Confidence */}
                <div className="my-1.5">
                  <div className={`inline-block text-[11px] font-bold px-2 py-0.5 rounded border ${getBadgeColor(cell.current_stress)}`}>
                    {cell.current_stress}
                  </div>
                  <div className="text-[10px] text-slate-300 mt-1 font-mono">
                    Conf: <span className="font-bold text-white">{(cell.confidence * 100).toFixed(0)}%</span>
                    {cell.current_stress === 'Water Stress' && cell.consecutive_water_stress_count > 0 && (
                      <span className="ml-1 text-red-300">({cell.consecutive_water_stress_count}/3)</span>
                    )}
                  </div>
                </div>

                {/* Bottom Row: Quick Telemetry Indices */}
                <div className="pt-1.5 border-t border-white/10 flex items-center justify-between text-[10px] text-slate-300 font-mono">
                  <div>
                    SM15: <span className="text-white font-bold">{cell.sensor_values.soil_moisture_15.toFixed(1)}%</span>
                  </div>
                  <div>
                    CWSI: <span className="text-white font-bold">{cell.derived_features.cwsi.toFixed(2)}</span>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setModalCell(cell);
                    }}
                    className="p-1 rounded hover:bg-white/20 text-slate-300 hover:text-white"
                    title="Open Full Zone Diagnostics"
                  >
                    <Info className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          });
        })}
      </div>

      {/* Modal */}
      {modalCell && (
        <CellDetailModal
          cell={modalCell}
          onClose={() => setModalCell(null)}
          onRefresh={onRefresh}
        />
      )}
    </div>
  );
};
