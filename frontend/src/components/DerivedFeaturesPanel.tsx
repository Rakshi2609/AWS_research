import React from 'react';
import { DerivedFeatures } from '../types';
import { Sparkles } from 'lucide-react';

interface Props {
  features: DerivedFeatures | null;
  zoneId: string;
}

export const DerivedFeaturesPanel: React.FC<Props> = ({ features, zoneId }) => {
  if (!features) return null;

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl">
      
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-4 h-4 text-cyan-400" />
        <h2 className="text-base font-bold text-white">
          Derived Agronomic Features — Zone {zoneId}
        </h2>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5">
        
        {/* VPD */}
        <div className="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800">
          <div className="text-xs text-slate-400 font-medium">Vapor Pressure Deficit</div>
          <div className="text-xl font-black text-white mt-1">
            {features.vpd.toFixed(2)} <span className="text-xs font-normal text-slate-400">kPa</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            {features.vpd < 0.8 ? 'Low Demand' : features.vpd > 2.2 ? 'High Evaporative Stress' : 'Balanced Transpiration'}
          </div>
        </div>

        {/* CWSI */}
        <div className="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800">
          <div className="text-xs text-slate-400 font-medium">Crop Water Stress Index</div>
          <div className={`text-xl font-black mt-1 ${features.cwsi > 0.65 ? 'text-red-400' : 'text-emerald-400'}`}>
            {features.cwsi.toFixed(2)}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            {features.cwsi < 0.3 ? 'Normal / Hydrated' : features.cwsi < 0.65 ? 'Mild Deficit' : 'Severe Canopy Deficit'}
          </div>
        </div>

        {/* NDVI */}
        <div className="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800">
          <div className="text-xs text-slate-400 font-medium">NDVI Index</div>
          <div className={`text-xl font-black mt-1 ${features.ndvi < 0.5 ? 'text-amber-400' : 'text-emerald-400'}`}>
            {features.ndvi.toFixed(2)}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            {features.ndvi > 0.7 ? 'High Biomass / Vigorous' : features.ndvi > 0.5 ? 'Moderate Cover' : 'Sparse / Degraded'}
          </div>
        </div>

        {/* NDRE */}
        <div className="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800">
          <div className="text-xs text-slate-400 font-medium">NDRE (RedEdge Index)</div>
          <div className={`text-xl font-black mt-1 ${features.ndre < 0.3 ? 'text-yellow-400' : 'text-emerald-400'}`}>
            {features.ndre.toFixed(2)}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            {features.ndre > 0.45 ? 'Optimal Chlorophyll' : 'Chlorophyll Depletion'}
          </div>
        </div>

      </div>
    </div>
  );
};
