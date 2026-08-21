"""
Irrigation Recommendation and Actuation Control API.
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    IrrigationStatusResponse,
    IrrigationControlRequest,
    IrrigationRecommendation
)
from app.services.stress_engine import stress_engine
from app.services.grid_service import grid_service

router = APIRouter(prefix="", tags=["Irrigation Control"])


@router.get(
    "/irrigation/status",
    response_model=IrrigationStatusResponse,
    summary="Get current irrigation status and valve states"
)
async def get_irrigation_status() -> IrrigationStatusResponse:
    """
    Return active valve states, system mode (AUTO/MANUAL), and current recommendations across all zones.
    """
    active_valves = [
        zone for zone, state in stress_engine.zone_valve_states.items() if state == "OPEN"
    ]
    
    recommendations = [
        cell.recommendation for cell in grid_service.grid_cells.values()
        if cell.recommendation.recommendation != "NORMAL_MONITOR"
    ]
    
    return IrrigationStatusResponse(
        system_mode=stress_engine.system_mode,
        active_valves=active_valves,
        recommendations=recommendations,
        last_action_timestamp=datetime.now().isoformat()
    )


@router.post(
    "/irrigation/control",
    summary="Manually control zone valves or switch system mode"
)
async def control_irrigation(cmd: IrrigationControlRequest):
    """
    Control valve states (OPEN/CLOSE) or switch system mode (AUTO/MANUAL).
    In simulation mode, updates simulated valve states safely without activating physical actuators.
    """
    if cmd.system_mode:
        mode = cmd.system_mode.upper()
        if mode not in ["AUTO", "MANUAL"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="System mode must be 'AUTO' or 'MANUAL'"
            )
        stress_engine.set_system_mode(mode)
        
    if cmd.zone and cmd.action:
        zone = cmd.zone.upper()
        action = cmd.action.upper()
        if action not in ["OPEN", "CLOSE", "AUTO"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Action must be 'OPEN', 'CLOSE', or 'AUTO'"
            )
        if action == "AUTO":
            stress_engine.manual_overrides.pop(zone, None)
        else:
            stress_engine.set_valve_state(zone, action)
            # update grid cell representation
            if zone in grid_service.grid_cells:
                grid_service.grid_cells[zone].valve_state = action

    return {
        "status": "success",
        "system_mode": stress_engine.system_mode,
        "zone_states": stress_engine.zone_valve_states
    }
