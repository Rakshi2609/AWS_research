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
      
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-emerald-400" />
          <h2 className="text-base font-bold text-white">
            Model Feature Importance
          </h2>
        </div>
        <span className="text-[10px] text-slate-400 font-mono">
          Random Forest Gini Impurity
        </span>
      </div>

      <p className="text-[11px] text-slate-400 mb-4 flex items-center gap-1">
        <HelpCircle className="w-3.5 h-3.5 text-slate-500 shrink-0" />
        Strongest signals contributing to multi-sensor stress classification (model-level importance).
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

      {/* Model metadata stats */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500 font-mono">
        <div>Model Accuracy: {(metrics.accuracy * 100).toFixed(1)}%</div>
        <div>Trained Samples: {metrics.training_samples}</div>
        <div>Ver: {metrics.model_version}</div>
      </div>

    </div>
  );
};
