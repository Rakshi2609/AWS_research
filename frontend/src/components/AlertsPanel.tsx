import React from 'react';
import { AlertItem } from '../types';
import { Bell, AlertTriangle, ShieldCheck } from 'lucide-react';

interface Props {
  alerts: AlertItem[];
}

export const AlertsPanel: React.FC<Props> = ({ alerts }) => {
  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col h-full">
      
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Bell className="w-4 h-4 text-emerald-400" />
          <h2 className="text-base font-bold text-white">
            Live Stress Alerts
          </h2>
        </div>
        <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
          {alerts.length} events
        </span>
      </div>

      {/* Alert List */}
      <div className="space-y-2.5 overflow-y-auto max-h-[320px] pr-1">
        {alerts.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-xs flex flex-col items-center gap-2">
            <ShieldCheck className="w-8 h-8 text-slate-700" />
            No critical stress alerts recorded. Field conditions optimal.
          </div>
        ) : (
          alerts.map(a => {
            const isHigh = a.severity === 'HIGH';
            return (
              <div
                key={a.id}
                className={`p-3 rounded-xl border text-xs transition ${
                  isHigh
                    ? 'bg-red-950/40 border-red-800/60 text-red-200'
                    : 'bg-slate-950/70 border-slate-800/80 text-slate-300'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className={`font-bold flex items-center gap-1.5 ${
                    isHigh ? 'text-red-400' : 'text-yellow-400'
                  }`}>
                    <AlertTriangle className="w-3.5 h-3.5" />
                    Zone {a.grid_id} — {a.stress_type}
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">
                    {new Date(a.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div className="text-[11px] text-slate-300 mt-1 leading-snug">
                  {a.message}
                </div>
                <div className="text-[10px] text-slate-400 mt-1.5 font-mono bg-slate-900/60 p-1.5 rounded border border-slate-800/60">
                  {a.action_taken}
                </div>
              </div>
            );
          })
        )}
      </div>

    </div>
  );
};
