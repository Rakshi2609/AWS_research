"""
Sensor Telemetry Ingestion API.

Canonical ingestion contract for ESP32 edge nodes, LoRaWAN gateways,
and simulated field nodes.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import SensorReading, GridCellState
from app.services.grid_service import grid_service

router = APIRouter(prefix="", tags=["Sensors"])


@router.post(
    "/sensor-data",
    response_model=GridCellState,
    status_code=status.HTTP_200_OK,
    summary="Ingest single sensor reading from ESP32/LoRaWAN/Simulator"
)
async def ingest_sensor_data(reading: SensorReading) -> GridCellState:
    """
    Ingest a single sensor reading from an ESP32 hardware node or simulator.
    Automatically runs feature extraction, ML inference, decision engine, and updates field grid.
    """
    try:
        updated_cell = grid_service.ingest_sensor_reading(reading)
        return updated_cell
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to ingest sensor reading: {str(e)}"
        )


@router.post(
    "/sensor-data/batch",
    response_model=List[GridCellState],
    status_code=status.HTTP_200_OK,
    summary="Batch ingest multiple sensor readings"
)
async def ingest_batch_sensor_data(readings: List[SensorReading]) -> List[GridCellState]:
    """
    Ingest a batch of sensor readings from multiple edge nodes simultaneously.
    """
    results = []
    for reading in readings:
        try:
            cell = grid_service.ingest_sensor_reading(reading)
            results.append(cell)
        except Exception as e:
            continue
    return results
