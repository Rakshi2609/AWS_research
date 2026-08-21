"""
Multispectral Image & Vegetation Index Processing Module.
"""
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import MultispectralProcessRequest, MultispectralProcessResponse
from app.features.vegetation import calculate_ndvi, calculate_ndre

router = APIRouter(prefix="", tags=["Multispectral"])


@router.post(
    "/multispectral/process",
    response_model=MultispectralProcessResponse,
    summary="Process multispectral reflectance bands into NDVI & NDRE"
)
async def process_multispectral_bands(data: MultispectralProcessRequest) -> MultispectralProcessResponse:
    """
    Calculate NDVI and NDRE from Red, RedEdge, and NIR reflectance bands (e.g. from drone/satellite).
    """
    ndvi = calculate_ndvi(nir=data.nir, red=data.red)
    ndre = calculate_ndre(nir=data.nir, red_edge=data.red_edge)
    
    # Assess chlorophyll and canopy density status
    if ndre >= 0.45:
        chlorophyll_status = "Optimal / High Nitrogen"
    elif ndre >= 0.30:
        chlorophyll_status = "Moderate / Adequate Nitrogen"
    else:
        chlorophyll_status = "Chlorophyll Deficit / Nitrogen Depletion"

    if ndvi >= 0.70:
        canopy_density = "Dense Vigorous Foliage"
    elif ndvi >= 0.50:
        canopy_density = "Moderate Canopy Cover"
    elif ndvi >= 0.30:
        canopy_density = "Sparse Canopy / Early Stress"
    else:
        canopy_density = "Severe Canopy Defoliation / Bare Soil"

    return MultispectralProcessResponse(
        ndvi=ndvi,
        ndre=ndre,
        chlorophyll_status=chlorophyll_status,
        canopy_density=canopy_density,
        notes="Multispectral computation completed with standard Red (660nm), RedEdge (705nm), and NIR (840nm) bands."
    )


@router.get(
    "/multispectral/samples",
    summary="Get preset multispectral test profiles"
)
async def get_multispectral_samples() -> Dict[str, Any]:
    """
    Return calibrated multispectral sample bands representing different crop health conditions.
    """
    return {
        "samples": [
            {
                "condition": "Healthy Canopy",
                "red": 0.05,
                "red_edge": 0.20,
                "nir": 0.72,
                "expected_ndvi": 0.87,
                "expected_ndre": 0.57
            },
            {
                "condition": "Water Deficit Canopy",
                "red": 0.12,
                "red_edge": 0.28,
                "nir": 0.48,
                "expected_ndvi": 0.60,
                "expected_ndre": 0.26
            },
            {
                "condition": "Nutrient Deficient (Chlorotic)",
                "red": 0.18,
                "red_edge": 0.34,
                "nir": 0.42,
                "expected_ndvi": 0.40,
                "expected_ndre": 0.11
            },
            {
                "condition": "Fungal / Diseased Patch",
                "red": 0.15,
                "red_edge": 0.30,
                "nir": 0.45,
                "expected_ndvi": 0.50,
                "expected_ndre": 0.20
            }
        ]
    }
