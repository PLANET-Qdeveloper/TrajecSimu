"""シミュレーションパラメータの定義"""

from enum import Enum

import geopandas as gpd
import numpy as np
from pydantic import BaseModel, Field
from scipy.spatial.transform import Rotation
from shapely.geometry import Point

from schema.rocket import RocketConfigModel
from schema.transform import Transform


class WindModel(str, Enum):
    """Wind model enumeration."""

    power = "power"
    power_forecast_hybrid = "power-forecast-hydrid"


class AeroFinMode(str, Enum):
    """Aero fin mode enumeration."""

    indiv = "indiv"
    integ = "integ"


class LaunchSiteModel(BaseModel):
    """Launch site model."""

    # Launch site name
    launch_site_name: str = Field(
        default="noshiro",
        description="Name of the launch site",
    )

    geo_location: Point = Field(
        default=Point(139.421333, 34.736139),
        description="Geographical location of launch site",
    )

    # Launch site location
    rocket_transform: Transform = Field(
        default=Transform(point=np.ndarray([]), rotation=[0, 75]),
        description="Location of launch site",
    )

    rail_length: float = Field(5.0, description="Length of launcher rail")


class EnviromentModel(BaseModel):
    """Environment model."""

    # Atmosphere property
    ground_temperature: float = Field(298.0, description="Temperature at 10m altitude [K]")
    ground_pressure: float = Field(1.013e5, description="Pressure at 10m alt. [Pa]")

    # Wind property
    wind_direction_original: float = Field(-1.0)
    wind_direction: float = Field(315.0, description="Azimuth where wind is blowing FROM")
    wind_speed: float = Field(2.0, description="Wind speed at 'wind_alt_std' alt. [m/s]")
    wind_power_coeff: float = Field(14.0)
    wind_alt_std: float = Field(5.0, description="Alt. at which the wind speed is given [m]")
    wind_model: WindModel = Field(
        WindModel.power, description="'power' for Wind Power Method, 'power-forecast-hydrid' for power-forecast hybrid"
    )

    earth_rotaion: float = Field(7.2921159e-5, description="Earth rotation speed [rad/s]")


class SimulationParameterModel(BaseModel):
    """Simulation parameters model."""

    # Numerical executive parameters
    dt: float = Field(0.05, description="Time step [s]")
    t_max: float = Field(100 * 60, description="Maximum time [s]")
    integ: str = Field("lsoda_odeint", description="Time integration scheme")

    # Rocket configuration
    rocket_config: RocketConfigModel = Field(
        default=RocketConfigModel(),
        description="Rocket configuration parameters",
    )

    # Simulation name
    simulation_name: str = Field(
        default="rocket_simulation",
        description="Name of the simulation instance",
    )

    # Simulation instance name
    launch_site_name: str = Field(
        default="noshiro",
        description="Name of the simulation instance",
    )
