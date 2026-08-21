"""
Vapor Pressure Deficit (VPD) Feature Engineering.

VPD measures the drying power of the air in kPa, reflecting the difference
between saturation vapor pressure at air temperature and actual vapor pressure.
Higher VPD indicates high evaporative demand on crop foliage.
"""
import math


def calculate_vpd(air_temperature: float, relative_humidity: float) -> float:
    """
    Calculate Vapor Pressure Deficit (VPD) in kiloPascals (kPa).
    
    Formula (Tetens equation for saturation vapor pressure):
        e_s(T) = 0.61078 * exp((17.27 * T) / (T + 237.3))
        e_a = e_s(T) * (RH / 100.0)
        VPD = e_s(T) - e_a = e_s(T) * (1.0 - RH / 100.0)
        
    Args:
        air_temperature: Ambient air temperature in degrees Celsius (°C).
        relative_humidity: Relative humidity in percentage (0 to 100%).
        
    Returns:
        float: Vapor Pressure Deficit in kPa (clamped to >= 0.0).
    """
    # Sanitize inputs
    rh = max(0.0, min(100.0, float(relative_humidity)))
    t = float(air_temperature)
    
    # Saturation vapor pressure in kPa
    sat_vp = 0.61078 * math.exp((17.27 * t) / (t + 237.3))
    
    # Actual vapor pressure in kPa
    act_vp = sat_vp * (rh / 100.0)
    
    vpd = sat_vp - act_vp
    return max(0.0, round(vpd, 4))
