import React, { useState } from 'react';
import { Camera, Send } from 'lucide-react';
import { processMultispectral } from '../services/api';
import { MultispectralProcessResponse } from '../types';

export const MultispectralViewer: React.FC = () => {
  const [red, setRed] = useState<number>(0.06);
  const [redEdge, setRedEdge] = useState<number>(0.22);
  const [nir, setNir] = useState<number>(0.75);
  const [result, setResult] = useState<MultispectralProcessResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const presets = [
    { label: 'Healthy Canopy', r: 0.05, re: 0.20, n: 0.72 },
    { label: 'Water Deficit', r: 0.12, re: 0.28, n: 0.48 },
    { label: 'Nutrient Chlorosis', r: 0.18, re: 0.34, n: 0.42 },
    { label: 'Diseased Patch', r: 0.15, re: 0.30, n: 0.45 },
  ];

  const handleCompute = async () => {
    setLoading(true);
    try {
      const res = await processMultispectral({ red, red_edge: redEdge, nir });
      setResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const applyPreset = (p: typeof presets[0]) => {
    setRed(p.r);
    setRedEdge(p.re);
    setNir(p.n);
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl">
      
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Camera className="w-4 h-4 text-emerald-400" />
          <h2 className="text-base font-bold text-white">
            Multispectral & Drone Spectral Processor
          </h2>
        </div>
        <span className="text-[10px] text-slate-400 font-mono">
          NDVI / NDRE Extraction
        </span>
      </div>

      <p className="text-xs text-slate-400 mb-4">
        Process calibrated optical reflectance bands (Red 660nm, RedEdge 705nm, NIR 840nm) into vegetation indices.
      </p>

      {/* Preset Quick Buttons */}
      <div className="flex flex-wrap gap-2 mb-4">
        <span className="text-xs text-slate-400 self-center">Presets:</span>
        {presets.map(p => (
          <button
            key={p.label}
            onClick={() => applyPreset(p)}
            className="px-2.5 py-1 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 text-xs border border-slate-800 transition"
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Band Sliders */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        
        {/* Red */}
        <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800">
          <div className="flex justify-between text-xs text-slate-400 mb-1">
            <span className="font-semibold text-red-400">Red Band (660nm)</span>
            <span className="font-mono">{red.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min="0.01"
            max="0.50"
            step="0.01"
            value={red}
            onChange={(e) => setRed(parseFloat(e.target.value))}
            className="w-full accent-red-500"
          />
        </div>

        {/* Red Edge */}
        <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800">
          <div className="flex justify-between text-xs text-slate-400 mb-1">
            <span className="font-semibold text-yellow-400">RedEdge Band (705nm)</span>
            <span className="font-mono">{redEdge.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min="0.05"
            max="0.60"
            step="0.01"
            value={redEdge}
            onChange={(e) => setRedEdge(parseFloat(e.target.value))}
            className="w-full accent-yellow-500"
          />
        </div>

        {/* NIR */}
        <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800">
          <div className="flex justify-between text-xs text-slate-400 mb-1">
            <span className="font-semibold text-emerald-400">NIR Band (840nm)</span>
            <span className="font-mono">{nir.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min="0.10"
            max="0.95"
            step="0.01"
            value={nir}
            onChange={(e) => setNir(parseFloat(e.target.value))}
            className="w-full accent-emerald-500"
          />
        </div>

      </div>

      <div className="flex items-center justify-between">
        <button
          onClick={handleCompute}
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition flex items-center gap-1.5 shadow-lg shadow-emerald-950/50"
        >
          <Send className="w-3.5 h-3.5" /> Compute Spectral Indices
        </button>

        {result && (
          <div className="flex items-center gap-4 text-xs">
            <div>
              NDVI: <span className="font-bold text-white font-mono">{result.ndvi.toFixed(3)}</span>
            </div>
            <div>
              NDRE: <span className="font-bold text-white font-mono">{result.ndre.toFixed(3)}</span>
            </div>
            <div className="text-emerald-400 font-semibold">
              {result.chlorophyll_status}
            </div>
          </div>
        )}
      </div>

    </div>
  );
};
