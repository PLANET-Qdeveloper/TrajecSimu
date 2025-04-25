"""シミュレーションパラメータの定義"""

import math
from enum import Enum
from functools import cached_property

import geopandas as gpd
import numpy as np
import pyproj
from pydantic import BaseModel, Field, computed_field
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
    wind_direction: float = Field(315.0, description="Azimuth where wind is blowing FROM")
    wind_speed: float = Field(2.0, description="Wind speed at 'wind_alt_std' alt. [m/s]")
    wind_power_coeff: float = Field(14.0)
    wind_alt_std: float = Field(5.0, description="Alt. at which the wind speed is given [m]")
    wind_model: WindModel = Field(
        WindModel.power, description="'power' for Wind Power Method, 'power-forecast-hydrid' for power-forecast hybrid"
    )


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
    launch_site: LaunchSiteModel = Field(
        default=LaunchSiteModel(),
        description="Launch site parameters",
    )

    @computed_field
    @cached_property
    def earth_rotation_speed(self) -> float:
        """地球の回転速度を計算するプロパティ

        Returns:
            float: 地球の回転速度 [m/s]
        """
        return self.calculate_earth_rotation_speed(self.launch_site.geo_location.y)

    @classmethod
    def calculate_radius_at_latitude(cls, lat_rad: float, a: float, b: float) -> float:
        """回転楕円体上の特定の緯度での地球の半径を計算

        Parameters:
        lat_rad (float): 緯度（ラジアン）
        a (float): 長半径（メートル）
        b (float): 短半径（メートル）

        Returns:
        float: 指定緯度での半径（メートル）
        """
        # 楕円体の緯度でのパラメトリック方程式による半径計算
        # 参考: https://en.wikipedia.org/wiki/Earth_radius#Radius_at_a_given_geodetic_latitude
        num = (a**2 * np.cos(lat_rad)) ** 2 + (b**2 * np.sin(lat_rad)) ** 2
        den = (a * np.cos(lat_rad)) ** 2 + (b * np.sin(lat_rad)) ** 2
        return np.sqrt(num / den)

    @classmethod
    def calculate_earth_rotation_speed(cls, latitude: float) -> float:
        """指定された緯度経度での地球の回転速度を計算する関数

        Parameters:
        latitude (float): 緯度（度）
        longitude (float): 経度（度）

        Returns:
        float: 回転速度 (m/s)
        """
        # WGS84楕円体パラメータを使用
        ellps = pyproj.Geod(ellps="WGS84")

        # 地球の平均半径 (メートル) WGS84楕円体の平均半径を使用
        a = ellps.a  # 長半径
        b = ellps.b  # 短半径

        # 地球の1日の回転周期（秒）
        # 恒星日を使用 (23時間56分4.091秒)
        sidereal_day = 23 * 3600 + 56 * 60 + 4.091

        # 緯度をラジアンに変換
        lat_rad = math.radians(latitude)

        # 楕円体上の点での地球半径を計算
        # 回転楕円体での緯度での半径
        radius = cls.calculate_radius_at_latitude(lat_rad, a, b)

        # 回転速度の計算 (m/s) 周速度 = 2πr / T
        circumference = 2 * np.pi * radius * np.cos(lat_rad)
        return circumference / sidereal_day
