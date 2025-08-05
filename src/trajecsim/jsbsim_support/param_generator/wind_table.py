"""風テーブル生成を行うモジュール"""

import numpy as np
import pandas as pd


def generate_wind_table(
    ground_wind_dir: float, ground_wind_speed: float, ref_altitude: float, wind_power_factor: float
) -> list[tuple[float, float, float]]:
    """Generate the wind table using the power law.

    The wind speed V at height h is calculated using the formula:
    V(h) = V_ref * (h / H_REF)^alpha
    where:
        V_ref is the wind speed at a reference height H_REF (ground_wind_speed).
        alpha is the wind_power_factor.
        H_REF is a standard reference height, assumed here as 10.0 meters.

    The wind direction is assumed to be constant with altitude.

    Args:
        ground_wind_dir (float): The ground wind direction (degrees).
        ground_wind_speed (float): The wind speed (m/s) at the reference height H_REF.
        wind_power_factor (float): The exponent alpha for the power law.

    Returns:
        list[tuple[float, float, float]]: List of (altitude_m, speed_mps, direction_deg) tuples.
    """
    # Generate altitudes using logarithmic scale from 0.1m to 10000m
    # Start with 0.1m intervals and scale up to 100m intervals
    altitudes_m_list = []

    # Low altitude range: 0.1m to 10m with 0.1m intervals
    low_altitudes = np.arange(0.1, 10.1, 0.1)
    altitudes_m_list.extend(low_altitudes)

    # Medium altitude range: 10m to 1000m with logarithmic spacing
    # Use logspace to create logarithmic distribution
    medium_altitudes = np.logspace(1, 3, 300)  # 10^1 to 10^3 (10m to 1000m)
    altitudes_m_list.extend(medium_altitudes)

    # High altitude range: 1000m to 10000m with 100m intervals
    high_altitudes = np.arange(1000, 10001, 100)
    altitudes_m_list.extend(high_altitudes)

    # Remove duplicates and sort
    altitudes_m_list = sorted(list(set(altitudes_m_list)))
    altitudes_s = pd.Series(altitudes_m_list, dtype=float)

    # Calculate relative heights (h / H_REF).
    relative_heights_s = altitudes_s / ref_altitude

    # Calculate the power term (h / H_REF)^alpha.
    power_terms_s = relative_heights_s.pow(wind_power_factor)

    # Explicitly define behavior at h=0 (the first altitude point).
    if not altitudes_s.empty and altitudes_s.iloc[0] == 0.0:
        idx_first_element = altitudes_s.index[0]

        if wind_power_factor > 0:
            power_terms_s.loc[idx_first_element] = 0.0
        elif wind_power_factor == 0:
            power_terms_s.loc[idx_first_element] = 1.0
        else:  # wind_power_factor < 0
            power_terms_s.loc[idx_first_element] = 1.0

    wind_speeds_s = ground_wind_speed * power_terms_s

    # Wind direction is assumed constant with altitude, equal to ground_wind_dir.
    wind_directions_list = [float(ground_wind_dir - 180 if ground_wind_dir > 180 else ground_wind_dir + 180)] * len(
        altitudes_m_list
    )
    return [
        (altitude, speed, direction)
        for altitude, speed, direction in zip(altitudes_s, wind_speeds_s, wind_directions_list, strict=False)
    ]
