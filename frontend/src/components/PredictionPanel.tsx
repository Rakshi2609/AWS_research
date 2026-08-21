import React from 'react';
import { GridCellState, StressType } from '../types';
import { BrainCircuit } from 'lucide-react';

interface Props {
  cell: GridCellState | null;
}

export const PredictionPanel: React.FC<Props> = ({ cell }) => {
  if (!cell) return null;

  const probs = cell.probabilities;
  const classes: StressType[] = ['Healthy', 'Water Stress', 'Nutrient Stress', 'Disease Stress'];

  const getClassColor = (c: StressType) => {
    switch (c) {
      case 'Healthy': return 'bg-emerald-500 text-emerald-300';
      case 'Water Stress': return 'bg-red-500 text-red-300';
      case 'Nutrient Stress': return 'bg-yellow-500 text-yellow-300';
      case 'Disease Stress': return 'bg-purple-500 text-purple-300';
    }
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col justify-between">
      
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <BrainCircuit className="w-4 h-4 text-emerald-400" />
            <h2 className="text-base font-bold text-white">
              AI Sensor Fusion Prediction
            </h2>
          </div>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-300">
            Random Forest
          </span>
        </div>

        {/* Current Predicted Class Box */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 mb-4">
          <div className="text-xs text-slate-400 uppercase tracking-wider font-semibold mb-1">
            Predicted Condition
          </div>
          <div className="flex items-center justify-between">
            <div className="text-2xl font-black text-white">
              {cell.current_stress}
            </div>
            <div className="text-right">
              <div className="text-xs text-slate-400">Confidence</div>
              <div className="text-lg font-bold text-emerald-400 font-mono">
                {(cell.confidence * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        </div>

        {/* Class Probabilities Bar Breakdown */}
        <div className="space-y-2.5">
          <div className="text-xs font-semibold text-slate-300">
            Probability Distribution:
          </div>
          {classes.map(cls => {
            const p = probs[cls] || 0.0;
            const pct = Math.round(p * 100);
            return (
              <div key={cls} className="space-y-1">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-slate-300">{cls}</span>
                  <span className="font-mono text-slate-400">{pct}%</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-300 ${getClassColor(cls).split(' ')[0]}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Decision Engine Recommendation Note */}
      <div className="mt-4 pt-3 border-t border-slate-800/80">
        <div className="text-[11px] text-slate-400">
          Recommendation: <span className="text-white font-semibold">{cell.recommendation.recommendation}</span>
        </div>
      </div>

    </div>
  );
};
