import React, { useState } from 'react';
import { useFieldData } from './hooks/useFieldData';
import { DashboardHeader } from './components/DashboardHeader';
import { MetricsOverview } from './components/MetricsOverview';
import { FieldGridMap } from './components/FieldGridMap';
import { SensorPanel } from './components/SensorPanel';
import { DerivedFeaturesPanel } from './components/DerivedFeaturesPanel';
import { PredictionPanel } from './components/PredictionPanel';
import { ExplainabilityChart } from './components/ExplainabilityChart';
import { AlertsPanel } from './components/AlertsPanel';
import { IrrigationControl } from './components/IrrigationControl';
import { MultispectralViewer } from './components/MultispectralViewer';
import { 
  Layers, 
  Droplets, 
  Camera, 
  BarChart3, 
  AlertCircle 
} from 'lucide-react';

export const App: React.FC = () => {
  const {
    gridData,
    selectedCell,
    selectCell,
    alerts,
    metrics,
    error,
    refresh
  } = useFieldData(2500);

  const [activeTab, setActiveTab] = useState<'overview' | 'irrigation' | 'multispectral' | 'ml'>('overview');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-emerald-500 selection:text-white">
      
      {/* Top Sticky Header */}
      <DashboardHeader
        simulationActive={gridData?.simulation_active ?? false}
        systemMode={gridData?.system_mode ?? 'AUTO'}
        totalZones={gridData?.total_zones ?? 15}
        onRefresh={refresh}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 py-6 space-y-6">
        
        {/* Error Notification banner if backend connection drops */}
        {error && (
          <div className="bg-red-950/80 border border-red-800 text-red-200 px-4 py-3 rounded-xl flex items-center gap-3 text-xs">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            <div>
              <span className="font-bold">Backend Connection Warning:</span> {error}. Ensure FastAPI is running on port 8000.
            </div>
          </div>
        )}

        {/* Top Summary Metrics */}
        <MetricsOverview gridData={gridData} />

        {/* Navigation Tabs */}
        <div className="flex border-b border-slate-800 space-x-6 text-sm font-semibold">
          <button
            onClick={() => setActiveTab('overview')}
            className={`pb-3 flex items-center gap-2 border-b-2 transition ${
              activeTab === 'overview'
                ? 'border-emerald-500 text-emerald-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers className="w-4 h-4" />
            Field Overview & Telemetry
          </button>

          <button
            onClick={() => setActiveTab('irrigation')}
            className={`pb-3 flex items-center gap-2 border-b-2 transition ${
              activeTab === 'irrigation'
                ? 'border-cyan-500 text-cyan-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Droplets className="w-4 h-4" />
            Irrigation & Solenoids
          </button>

          <button
            onClick={() => setActiveTab('multispectral')}
            className={`pb-3 flex items-center gap-2 border-b-2 transition ${
              activeTab === 'multispectral'
                ? 'border-purple-500 text-purple-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Camera className="w-4 h-4" />
            Multispectral / Drone
          </button>

          <button
            onClick={() => setActiveTab('ml')}
            className={`pb-3 flex items-center gap-2 border-b-2 transition ${
              activeTab === 'ml'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            ML Model Diagnostics
          </button>
        </div>

        {/* Tab 1: Overview */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            
            {/* Interactive Field Grid Map */}
            <FieldGridMap
              cells={gridData?.cells ?? []}
              selectedCell={selectedCell}
              onSelectCell={selectCell}
              onRefresh={refresh}
            />

            {/* Middle Row: Selected Cell Telemetry & Derived Features */}
            {selectedCell && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Left 2 cols: Sensor Telemetry & Derived Features */}
                <div className="lg:col-span-2 space-y-6">
                  <SensorPanel cell={selectedCell} />
                  <DerivedFeaturesPanel 
                    features={selectedCell.derived_features} 
                    zoneId={selectedCell.grid_id} 
                  />
                </div>

                {/* Right col: ML Prediction & Alerts */}
                <div className="space-y-6">
                  <PredictionPanel cell={selectedCell} />
                  <AlertsPanel alerts={alerts} />
                </div>

              </div>
            )}

            {/* Bottom Row: Explainability */}
            <ExplainabilityChart metrics={metrics} />

          </div>
        )}

        {/* Tab 2: Irrigation & Solenoids */}
        {activeTab === 'irrigation' && (
          <div className="space-y-6">
            <IrrigationControl gridData={gridData} onRefresh={refresh} />
            <AlertsPanel alerts={alerts} />
          </div>
        )}

        {/* Tab 3: Multispectral / Drone */}
        {activeTab === 'multispectral' && (
          <div className="space-y-6">
            <MultispectralViewer />
            {selectedCell && (
              <DerivedFeaturesPanel 
                features={selectedCell.derived_features} 
                zoneId={selectedCell.grid_id} 
              />
            )}
          </div>
        )}

        {/* Tab 4: ML Diagnostics */}
        {activeTab === 'ml' && (
          <div className="space-y-6">
            <ExplainabilityChart metrics={metrics} />
            {selectedCell && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <PredictionPanel cell={selectedCell} />
                <SensorPanel cell={selectedCell} />
              </div>
            )}
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-4 px-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>
            AI-Enabled IoT Smart Crop Stress Detection System • Local Edge Runtime
          </div>
          <div className="font-mono text-[11px]">
            Inference: Local Random Forest (15 Features) • Schema-Compliant ESP32 Ready
          </div>
        </div>
      </footer>

    </div>
  );
};
