import React from 'react';
import { MLMetricsResponse } from '../types';
import { BarChart3, HelpCircle } from 'lucide-react';

interface Props {
  metrics: MLMetricsResponse | null;
}

export const ExplainabilityChart: React.FC<Props> = ({ metrics }) => {
  if (!metrics || !metrics.feature_importance || metrics.feature_importance.length === 0) {
    return (
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 text-center text-slate-500">
        Loading ML feature importance metrics...
      </div>
    );
  }

  const items = metrics.feature_importance.slice(0, 8);
  const maxImp = Math.max(...items.map(i => i.importance));

  const formatFeatureLabel = (f: string) => {
    switch (f) {
      case 'ndre': return 'NDRE (Red Edge Chlorophyll)';
      case 'sap_flow': return 'Sap Flow (Transpiration)';
      case 'ndvi': return 'NDVI (Vegetation Index)';
      case 'soil_moisture_15': return 'Soil Moisture 15cm';
      case 'soil_moisture_30': return 'Soil Moisture 30cm';
      case 'soil_moisture_60': return 'Soil Moisture 60cm';
      case 'electrical_conductivity': return 'Soil EC (Salinity/Nutrient)';
      case 'cwsi': return 'CWSI (Water Stress Index)';
      case 'vpd': return 'VPD (Atmospheric Demand)';
      case 'leaf_temperature': return 'Leaf / Canopy Temp';
      case 'soil_temperature': return 'Soil Temperature';
      case 'air_temperature': return 'Air Temperature';
      case 'relative_humidity': return 'Relative Humidity';
      default: return f;
    }
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl">
      
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-emerald-400" />
          <h2 className="text-base font-bold text-white">
            Model Feature Importance & Provenance
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-950/80 text-blue-300 border border-blue-800">
            {metrics.dataset_type ? `Dataset: ${metrics.dataset_type.toUpperCase()}` : 'Real Benchmark'}
          </span>
          <span className="text-[10px] text-slate-400 font-mono">
            Random Forest Gini Impurity
          </span>
        </div>
      </div>

      <p className="text-[11px] text-slate-400 mb-4 flex items-center gap-1">
        <HelpCircle className="w-3.5 h-3.5 text-slate-500 shrink-0" />
        Strongest signals contributing to multi-sensor stress classification (model-level feature importance).
      </p>

      {/* Horizontal Bar Chart */}
      <div className="space-y-2.5">
        {items.map((item, idx) => {
          const barWidth = Math.round((item.importance / maxImp) * 100);
          return (
            <div key={item.feature} className="space-y-0.5">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300 font-medium">
                  {idx + 1}. {formatFeatureLabel(item.feature)}
                </span>
                <span className="text-emerald-400 font-mono font-bold">
                  {(item.importance * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
                <div
                  className="bg-emerald-500 h-full rounded-full transition-all duration-300"
                  style={{ width: `${barWidth}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Model Provenance & Metadata Cards */}
      <div className="mt-5 pt-3 border-t border-slate-800/80 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
          <div className="text-[10px] text-slate-400">Dataset Source</div>
          <div className="font-bold text-white text-[11px] mt-0.5 truncate" title={metrics.dataset_source || 'Real Public Benchmarks'}>
            {metrics.dataset_source || 'Real Public Benchmarks'}
          </div>
        </div>

        <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
          <div className="text-[10px] text-slate-400">Training Samples</div>
          <div className="font-bold text-emerald-400 text-[11px] mt-0.5 font-mono">
            {metrics.training_samples.toLocaleString()} samples
          </div>
        </div>

        <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
          <div className="text-[10px] text-slate-400">Validation Split</div>
          <div className="font-bold text-cyan-400 text-[11px] mt-0.5 font-mono">
            {metrics.test_samples.toLocaleString()} test (Plot-Level)
          </div>
        </div>

        <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
          <div className="text-[10px] text-slate-400">Measured Accuracy</div>
          <div className="font-bold text-white text-[11px] mt-0.5 font-mono">
            {(metrics.accuracy * 100).toFixed(1)}% (v{metrics.model_version})
          </div>
        </div>
      </div>

    </div>
  );
};
