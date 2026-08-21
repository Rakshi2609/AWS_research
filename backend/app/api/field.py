"""
Field Grid and Alert API.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import FieldGridResponse, AlertItem
from app.services.grid_service import grid_service

router = APIRouter(prefix="", tags=["Field Grid"])


@router.get(
    "/field/grid",
    response_model=FieldGridResponse,
    summary="Get real-time spatial field grid state"
)
async def get_field_grid() -> FieldGridResponse:
    """
    Get the complete spatial grid state for all 15 field zones with current stress classifications,
    sensor values, and irrigation recommendations.
    """
    return grid_service.get_grid_state()


@router.get(
    "/field/cell/{grid_id}",
    response_model=Dict[str, Any],
    summary="Get details and telemetry history for a specific cell"
)
async def get_cell_details(grid_id: str) -> Dict[str, Any]:
    """
    Get time-series history and current telemetry for a specific grid cell (e.g. A1, B3).
    """
    cell_info = grid_service.get_cell_detail(grid_id.upper())
    if not cell_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grid cell '{grid_id}' not found"
        )
    return cell_info


@router.get(
    "/alerts",
    response_model=List[AlertItem],
    summary="Get recent crop stress alerts"
)
async def get_alerts(limit: int = 50) -> List[AlertItem]:
    """
    Retrieve real-time stress alerts logged by the decision engine.
    """
    return grid_service.get_alerts(limit=limit)
