"""
Multispectral Vegetation Indices Feature Engineering.

Computes:
- NDVI (Normalized Difference Vegetation Index): Chlorophyll absorption & biomass
- NDRE (Normalized Difference Red Edge Index): Early nitrogen/chlorophyll stress detection
"""
import random


def calculate_ndvi(nir: float, red: float) -> float:
    """
    Calculate Normalized Difference Vegetation Index (NDVI).
    
    Formula:
        NDVI = (NIR - Red) / (NIR + Red)
        
    Args:
        nir: Near-infrared band reflectance (0.0 to 1.0)
        red: Red band reflectance (0.0 to 1.0)
        
    Returns:
        float: NDVI index clamped to [-1.0, 1.0]
    """
    denom = float(nir) + float(red)
    if abs(denom) < 1e-7:
        return 0.0
    ndvi = (float(nir) - float(red)) / denom
    return max(-1.0, min(1.0, round(ndvi, 4)))


def calculate_ndre(nir: float, red_edge: float) -> float:
    """
    Calculate Normalized Difference Red Edge Index (NDRE).
    
    Formula:
        NDRE = (NIR - RedEdge) / (NIR + RedEdge)
        
    Args:
        nir: Near-infrared band reflectance (0.0 to 1.0)
        red_edge: RedEdge band reflectance (0.0 to 1.0)
        
    Returns:
        float: NDRE index clamped to [-1.0, 1.0]
    """
    denom = float(nir) + float(red_edge)
    if abs(denom) < 1e-7:
        return 0.0
    ndre = (float(nir) - float(red_edge)) / denom
    return max(-1.0, min(1.0, round(ndre, 4)))


def estimate_spectral_bands(crop_condition: str, noise: float = 0.015) -> tuple[float, float, float]:
    """
    Estimate simulated Red, RedEdge, and NIR reflectance values for training
    and simulation mode based on biological canopy characteristics.
    
    Returns:
        tuple[float, float, float]: (Red, RedEdge, NIR)
    """
    if crop_condition == "Healthy":
        red = max(0.02, random.gauss(0.06, noise))
        red_edge = max(0.12, random.gauss(0.22, noise))
        nir = max(0.40, min(0.95, random.gauss(0.68, noise)))
    elif crop_condition == "Water Stress":
        red = max(0.05, random.gauss(0.12, noise))
        red_edge = max(0.15, random.gauss(0.26, noise))
        nir = max(0.30, min(0.75, random.gauss(0.48, noise)))
    elif crop_condition == "Nutrient Stress":
        # Chlorophyll degradation shifts red and red-edge significantly
        red = max(0.08, random.gauss(0.18, noise))
        red_edge = max(0.20, random.gauss(0.34, noise))
        nir = max(0.25, min(0.65, random.gauss(0.42, noise)))
    elif crop_condition == "Disease Stress":
        # Necrotic spots and cellular collapse
        red = max(0.07, random.gauss(0.15, noise))
        red_edge = max(0.18, random.gauss(0.30, noise))
        nir = max(0.28, min(0.70, random.gauss(0.45, noise)))
    else:
        red, red_edge, nir = 0.10, 0.25, 0.50
        
    return round(red, 4), round(red_edge, 4), round(nir, 4)
