"""
Crop Water Stress Index (CWSI) Feature Engineering.

CWSI assesses canopy water deficit using infrared leaf/canopy temperature
relative to ambient air temperature, standardized against non-water-stressed
(lower baseline) and fully stressed (upper baseline) canopy conditions.
"""

def calculate_cwsi(
    leaf_temperature: float,
    air_temperature: float,
    vpd: float,
    solar_radiation: float = 600.0,
    a_lower: float = 1.5,
    b_lower: float = -1.2,
    dt_upper_base: float = 4.5
) -> float:
    """
    Calculate empirical Crop Water Stress Index (CWSI).
    
    Theoretical concept:
        CWSI = [(T_leaf - T_air) - dT_lower] / [dT_upper - dT_lower]
        
    Where:
        dT = T_leaf - T_air
        dT_lower (non-water-stressed baseline) = a_lower + b_lower * VPD
        dT_upper (non-transpiring canopy baseline) = dt_upper_base + (solar_radiation / 1000.0) * 1.5
        
    The implementation is isolated and parameterized so it can be calibrated
    with crop-specific wet/dry canopy baselines.
    
    Args:
        leaf_temperature: Leaf/canopy surface temperature (°C).
        air_temperature: Ambient air temperature (°C).
        vpd: Vapor pressure deficit (kPa).
        solar_radiation: Solar irradiance (W/m²).
        a_lower: Intercept for non-water-stressed baseline.
        b_lower: Slope for non-water-stressed baseline against VPD.
        dt_upper_base: Base upper limit for non-transpiring canopy.
        
    Returns:
        float: CWSI index between 0.0 (fully hydrated/transpiring) and 1.0 (extreme water stress).
    """
    dt = float(leaf_temperature) - float(air_temperature)
    vpd_val = max(0.1, float(vpd))
    
    # Non-water-stressed lower baseline (healthy transpiring crop is cooler under high VPD)
    dt_lower = a_lower + (b_lower * vpd_val)
    
    # Non-transpiring upper baseline (closed stomata under solar load)
    radiation_factor = max(0.0, float(solar_radiation)) / 1000.0
    dt_upper = dt_upper_base + (radiation_factor * 1.5)
    
    # Safeguard against denominator collapse
    if dt_upper <= dt_lower:
        dt_upper = dt_lower + 2.0
        
    cwsi_raw = (dt - dt_lower) / (dt_upper - dt_lower)
    
    # Clamp between 0.0 and 1.0
    cwsi = max(0.0, min(1.0, cwsi_raw))
    return round(cwsi, 4)
