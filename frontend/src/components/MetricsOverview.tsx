import React from 'react';
import { 
  CheckCircle2, 
  Droplets, 
  Zap, 
  Biohazard, 
  Activity 
} from 'lucide-react';
import { FieldGridResponse } from '../types';

interface Props {
  gridData: FieldGridResponse | null;
}

export const MetricsOverview: React.FC<Props> = ({ gridData }) => {
  if (!gridData) return null;

  const total = gridData.total_zones || 15;
  const healthy = gridData.healthy_count;
  const water = gridData.water_stress_count;
  const nutrient = gridData.nutrient_stress_count;
  const disease = gridData.disease_stress_count;
  const valves = gridData.active_valves_count;

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3.5 mb-6">
      
      {/* Healthy */}
      <div className="bg-slate-900/70 border border-emerald-900/40 rounded-xl p-3.5 flex items-center gap-3.5 relative overflow-hidden">
        <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0">
          <CheckCircle2 className="w-5 h-5" />
        </div>
        <div>
          <div className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider">Healthy</div>
          <div className="text-xl font-extrabold text-white">
            {healthy} <span className="text-xs font-normal text-slate-400">/ {total}</span>
          </div>
        </div>
        <div className="absolute right-2 bottom-1 text-4xl font-black text-emerald-500/5 select-none">
          {Math.round((healthy / total) * 100)}%
        </div>
      </div>

      {/* Water Stress */}
      <div className="bg-slate-900/70 border border-red-900/40 rounded-xl p-3.5 flex items-center gap-3.5 relative overflow-hidden">
        <div className="w-10 h-10 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400 shrink-0">
          <Droplets className="w-5 h-5" />
        </div>
        <div>
          <div className="text-[11px] font-semibold text-red-400 uppercase tracking-wider">Water Stress</div>
          <div className="text-xl font-extrabold text-white">
            {water} <span className="text-xs font-normal text-slate-400">/ {total}</span>
          </div>
        </div>
        <div className="absolute right-2 bottom-1 text-4xl font-black text-red-500/5 select-none">
          {Math.round((water / total) * 100)}%
        </div>
      </div>

      {/* Nutrient Stress */}
      <div className="bg-slate-900/70 border border-yellow-900/40 rounded-xl p-3.5 flex items-center gap-3.5 relative overflow-hidden">
        <div className="w-10 h-10 rounded-lg bg-yellow-500/10 border border-yellow-500/20 flex items-center justify-center text-yellow-400 shrink-0">
          <Zap className="w-5 h-5" />
        </div>
        <div>
          <div className="text-[11px] font-semibold text-yellow-400 uppercase tracking-wider">Nutrient Stress</div>
          <div className="text-xl font-extrabold text-white">
            {nutrient} <span className="text-xs font-normal text-slate-400">/ {total}</span>
          </div>
        </div>
        <div className="absolute right-2 bottom-1 text-4xl font-black text-yellow-500/5 select-none">
          {Math.round((nutrient / total) * 100)}%
        </div>
      </div>

      {/* Disease Stress */}
      <div className="bg-slate-900/70 border border-purple-900/40 rounded-xl p-3.5 flex items-center gap-3.5 relative overflow-hidden">
        <div className="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 shrink-0">
          <Biohazard className="w-5 h-5" />
        </div>
        <div>
          <div className="text-[11px] font-semibold text-purple-400 uppercase tracking-wider">Disease Stress</div>
          <div className="text-xl font-extrabold text-white">
            {disease} <span className="text-xs font-normal text-slate-400">/ {total}</span>
          </div>
        </div>
        <div className="absolute right-2 bottom-1 text-4xl font-black text-purple-500/5 select-none">
          {Math.round((disease / total) * 100)}%
        </div>
      </div>

      {/* Active Valves */}
      <div className="bg-slate-900/70 border border-cyan-900/40 rounded-xl p-3.5 flex items-center gap-3.5 relative overflow-hidden col-span-2 md:col-span-1">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 border ${
          valves > 0 
            ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300 animate-pulse' 
            : 'bg-slate-800 border-slate-700 text-slate-400'
        }`}>
          <Activity className="w-5 h-5" />
        </div>
        <div>
          <div className="text-[11px] font-semibold text-cyan-400 uppercase tracking-wider">Irrigation Valves</div>
          <div className="text-xl font-extrabold text-white">
            {valves} <span className="text-xs font-normal text-slate-400">OPEN</span>
          </div>
        </div>
      </div>

    </div>
  );
};
