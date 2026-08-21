import { useState, useEffect, useCallback, useRef } from 'react';
import { FieldGridResponse, AlertItem, MLMetricsResponse, GridCellState } from '../types';
import { fetchFieldGrid, fetchAlerts, fetchMLMetrics } from '../services/api';

export function useFieldData(pollingIntervalMs: number = 2500) {
  const [gridData, setGridData] = useState<FieldGridResponse | null>(null);
  const [selectedCell, setSelectedCell] = useState<GridCellState | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [metrics, setMetrics] = useState<MLMetricsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const selectedCellIdRef = useRef<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [gData, aData] = await Promise.all([
        fetchFieldGrid(),
        fetchAlerts(),
      ]);
      setGridData(gData);
      setAlerts(aData);

      // Keep selected cell updated
      if (gData.cells.length > 0) {
        if (selectedCellIdRef.current) {
          const found = gData.cells.find(c => c.grid_id === selectedCellIdRef.current);
          if (found) setSelectedCell(found);
        } else {
          // Default to first cell or first stressed cell
          const stressed = gData.cells.find(c => c.current_stress !== 'Healthy');
          const defaultCell = stressed || gData.cells[0];
          setSelectedCell(defaultCell);
          selectedCellIdRef.current = defaultCell.grid_id;
        }
      }
      setError(null);
    } catch (err: any) {
      console.error("Error refreshing field data:", err);
      setError(err.message || 'Failed to connect to backend');
    } finally {
      setLoading(false);
    }
  }, []);

  const selectCell = (cell: GridCellState) => {
    setSelectedCell(cell);
    selectedCellIdRef.current = cell.grid_id;
  };

  // Initial fetch for metrics
  useEffect(() => {
    fetchMLMetrics()
      .then(m => setMetrics(m))
      .catch(e => console.warn("Could not load ML metrics:", e));
  }, []);

  // Polling loop
  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, pollingIntervalMs);
    return () => clearInterval(interval);
  }, [refresh, pollingIntervalMs]);

  return {
    gridData,
    selectedCell,
    selectCell,
    alerts,
    metrics,
    loading,
    error,
    refresh
  };
}
