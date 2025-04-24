"""シミュレーションパラメータの定義"""

from enum import Enum

import pydantic
from pydantic import BaseModel, Field


class WindModel(str, Enum):
    """Wind model enumeration."""

    power = "power"
    power_forecast_hybrid = "power-forecast-hydrid"


class RocketConfigModel(BaseModel):
    """Rocket simulation configuration parameters model."""

    # Numerical executive parameters
    dt: float = Field(0.05, description="Time step [s]")
    t_max: float = Field(100 * 60, description="Maximum time [s]")
    N_record: int = Field(500, description="Record history every N_record iteration")
    integ: str = Field("lsoda_odeint", description="Time integration scheme")

    # Launch condition parameters
    elev_angle: float = Field(89.0, description="Angle of elevation [deg]")
    azimuth: float = Field(0.0, description="North=0, east=90, south=180, west=270 [deg]")
    rail_length: float = Field(5.0, description="Length of launcher rail")
    latitude: float = Field(35.0, description="Latitude of launch point [deg]")

    # Atmosphere property
    T0: float = Field(298.0, description="Temperature at 10m altitude [K]")
    p0: float = Field(1.013e5, description="Pressure at 10m alt. [Pa]")

    # Wind property
    wind_direction_original: float = Field(-1.0)
    wind_direction: float = Field(315.0, description="Azimuth where wind is blowing FROM")
    wind_speed: float = Field(2.0, description="Wind speed at 'wind_alt_std' alt. [m/s]")
    wind_power_coeff: float = Field(14.0)
    wind_alt_std: float = Field(5.0, description="Alt. at which the wind speed is given [m]")
    wind_model: WindModel = Field(
        "power", description="'power' for Wind Power Method, 'power-forecast-hydrid' for power-forecast hybrid"
    )

    # Rocket aerodynamic parameters
    aero_fin_mode: Literal["integ", "indiv"] = Field(
        "integ", description="'indiv' for individual fin computation, 'integ' for compute fin-body at once"
    )
    Cd0: float = Field(0.6, description="Drag coefficient at Mach 0.1, AoA = 0deg")
    Cmp: float = Field(-0.0, description="Stability derivative of rolling moment coefficient (aerodynamic damping)")
    Cmq: float = Field(
        -4.0, description="Stability derivative of pitching/yawing moment coefficient (aerodynamic damping)"
    )
    Cl_alpha: float = Field(12.0, description="Lift coefficient slope for small AoA [1/rad]")
    Mach_AOA_dep: bool = Field(True, description="True if aerodynamic parameter depends on Mach/AOA, False if ignore")

    # Rocket engine parameters
    t_meco: float = Field(9.3, description="Main Engine Cut Off (meco) time")
    thrust: float = Field(800.0, description="Thrust (const.)")
    thrust_input_type: str = Field("curve_const_t", description="Thrust input csv file type")
    curve_fitting: bool = Field(True, description="True if curvefitting")
    fitting_order: int = Field(15, description="Order of polynomial")
    thrust_mag_factor: float = Field(1.0, description="Thrust magnification factor")
    time_mag_factor: float = Field(1.0, description="Burn time magnification factor")

    # Parachute parameters
    t_deploy: float = Field(1000.0, description="Parachute deployment time from ignition")
    t_para_delay: float = Field(1000.0, description="1st parachute deployment time from apogee detection")
    Cd_para: float = Field(1.0, description="Drag coefficient of 1st parachute")
    S_para: float = Field(0.5, description="Parachute area of 1st parachute [m^2]")
    second_para: bool = Field(False, description="True if two stage parachute deployment")
    t_deploy_2: float = Field(2000, description="2nd parachute deployment time from apogee detection")
    Cd_para_2: float = Field(1, description="Drag coefficient of 2nd parachute")
    S_para_2: float = Field(6.082, description="Parachute area of 2nd parachute [m^2]")
    alt_para_2: float = Field(-100, description="Altitude at which 2nd parachute will be deployed")

    # Location parameters
    loc_lat: float = Field(34.736139)
    loc_lon: float = Field(139.421333)
    loc_alt: float = Field(0)
    loc_mag: float = Field(-7.5)
