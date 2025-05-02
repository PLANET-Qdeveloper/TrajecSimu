from enum import Enum
from typing import Optional

import numpy as np
from pydantic import BaseModel, Field, computed_field

# Atmosphere properties
DEFAULT_TEMPERATURE = 298.0  # Kelvin at 10m altitude
DEFAULT_PRESSURE = 1.013e5  # Pascal at 10m altitude
# Wind properties
DEFAULT_WIND_DIRECTION_ORIG = -1.0
DEFAULT_WIND_DIRECTION = 315.0  # degrees
DEFAULT_WIND_SPEED = 2.0  # m/s
DEFAULT_WIND_POWER_COEF = 14.0
DEFAULT_WIND_ALT_STD = 5.0  # meters
DEFAULT_WIND_MODEL = "power"

# Location parameters
DEFAULT_LOC_LAT = 34.736139
DEFAULT_LOC_LON = 139.421333
DEFAULT_LOC_ALT = 0.0
DEFAULT_LOC_MAG = -7.5

DEFAULT_GRAVITY = 9.80665  # Standard gravity at sea level in m/s^2

# Launch conditions
DEFAULT_ELEVATION_ANGLE = 89.0  # degrees
DEFAULT_AZIMUTH = 0.0  # degrees
DEFAULT_RAIL_LENGTH = 5.0  # meters
DEFAULT_LATITUDE = 35.0  # degrees

EARTH_ANGULAR_VELOCITY = 7.2921159e-5  # rad/s


class WindModel(str, Enum):
    """Enum for wind models"""

    POWER = "power"
    POWER_GUST = "power_Gust"
    LOG = "log"
    FORECAST = "forecast"
    STATISTICS = "statistics"
    ERROR_STATISTICS = "error-statistics"
    POWER_ES_HYBRID = "power-es-hybrid"
    POWER_FORECAST_HYBRID = "power-forecast-hybrid"
    LOG_FORECAST_HYBRID = "log-forecast-hybrid"
    POWER_STATISTICS_HYBRID = "power-statistics-hybrid"


class AtmosphereParameters(BaseModel):
    """Atmospheric properties"""

    T0: float = Field(DEFAULT_TEMPERATURE, description="Initial temperature at 10m altitude (Kelvin)")
    p0: float = Field(DEFAULT_PRESSURE, description="Initial pressure at 10m altitude (Pascal)")


class WindParameters(BaseModel):
    """Wind properties"""

    wind_direction_original: float = Field(
        DEFAULT_WIND_DIRECTION_ORIG, description="Original wind direction in degrees (-1.0 to disable)"
    )
    wind_direction: float = Field(DEFAULT_WIND_DIRECTION, description="Wind direction in degrees")
    wind_speed: float = Field(DEFAULT_WIND_SPEED, description="Wind speed in m/s")
    wind_power_coeff: float = Field(DEFAULT_WIND_POWER_COEF, description="Wind power law coefficient")
    wind_alt_std: float = Field(DEFAULT_WIND_ALT_STD, description="Standard altitude for wind measurement in meters")
    wind_model: WindModel = Field(DEFAULT_WIND_MODEL, description="Wind model type")
    forecast_csvname: str | None = Field(None, description="Filename for wind forecast CSV")
    statistics_filename: str | None = Field(None, description="Filename for wind statistics")
    error_stat_filename: str | None = Field(None, description="Filename for wind error statistics")

    @property
    @computed_field
    def wind_coefficient(self) -> float:
        """Calculate wind coefficient based on wind power coefficient"""
        return 1.0 / (self.wind_power_coeff - 1.0)


class LocationParameters(BaseModel):
    """Launch location parameters"""

    loc_lat: float = Field(DEFAULT_LOC_LAT, description="Launch site latitude in degrees")
    loc_lon: float = Field(DEFAULT_LOC_LON, description="Launch site longitude in degrees")
    loc_alt: float = Field(DEFAULT_LOC_ALT, description="Launch site altitude in meters")
    loc_mag: float = Field(DEFAULT_LOC_MAG, description="Magnetic declination at launch site in degrees")
    gravity: float = Field(
        DEFAULT_GRAVITY, description="Gravitational acceleration at launch site in m/s^2"
    )  # Standard gravity at sea level


class LaunchParameters(BaseModel):
    """Launch condition parameters"""

    elev_angle: float = Field(DEFAULT_ELEVATION_ANGLE, description="Elevation angle in degrees")
    azimuth: float = Field(DEFAULT_AZIMUTH, description="Azimuth angle in degrees")
    rail_length: float = Field(DEFAULT_RAIL_LENGTH, description="Launch rail length in meters")
    latitude: float = Field(DEFAULT_LATITUDE, description="Launch site latitude in degrees")

    @computed_field
    @property
    def rail_height(self) -> float:
        """Calculate rail height based on elevation angle and rail length"""
        return self.rail_length * np.sin(np.deg2rad(self.elev_angle))

    @computed_field
    @property
    def omega_earth(self) -> float:
        """Calculate angular velocity of Earth in rad/s"""
        latitude_rad = np.deg2rad(float(self.params_dict["latitude"]))
        return np.array([0.0, 0.0, EARTH_ANGULAR_VELOCITY * np.sin(latitude_rad)])
