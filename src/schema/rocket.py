"""シミュレーションパラメータの定義"""

from pydantic import BaseModel, Field
from shapely.geometry import Point

from schema.sim_parameter import AeroFinMode
from schema.transform import Transform


class RocketAereodynamicModel(BaseModel):
    """Rocket aerodynamic model."""

    # Rocket aerodynamic parameters
    aero_fin_mode: AeroFinMode = Field(
        "integ", description="'indiv' for individual fin computation, 'integ' for compute fin-body at once"
    )
    Cd0: float = Field(0.6, description="Drag coefficient at Mach 0.1, AoA = 0deg")
    Cmp: float = Field(-0.0, description="Stability derivative of rolling moment coefficient (aerodynamic damping)")
    Cmq: float = Field(
        -4.0, description="Stability derivative of pitching/yawing moment coefficient (aerodynamic damping)"
    )
    Cl_alpha: float = Field(12.0, description="Lift coefficient slope for small AoA [1/rad]")
    Mach_AOA_dep: bool = Field(
        default=True, description="True if aerodynamic parameter depends on Mach/AOA, False if ignore"
    )


class RocketEngineModel(BaseModel):
    """Rocket engine model."""

    # Rocket engine parameters
    t_meco: float = Field(9.3, description="Main Engine Cut Off (meco) time")
    thrust: float = Field(800.0, description="Thrust (const.)")
    thrust_input_type: str = Field("curve_const_t", description="Thrust input csv file type")
    curve_fitting: bool = Field(default=True, description="True if curvefitting")
    fitting_order: int = Field(15, description="Order of polynomial")
    thrust_mag_factor: float = Field(1.0, description="Thrust magnification factor")
    time_mag_factor: float = Field(1.0, description="Burn time magnification factor")


class ParachuteModel(BaseModel):
    """Parachute model."""

    # Parachute parameters
    t_deploy: float = Field(1000.0, description="Parachute deployment time from ignition")
    t_para_delay: float = Field(1000.0, description="1st parachute deployment time from apogee detection")
    Cd_para: float = Field(1.0, description="Drag coefficient of 1st parachute")
    S_para: float = Field(0.5, description="Parachute area of 1st parachute [m^2]")
    second_para: bool = Field(default=False, description="True if two stage parachute deployment")
    t_deploy_2: float = Field(2000, description="2nd parachute deployment time from apogee detection")
    Cd_para_2: float = Field(1, description="Drag coefficient of 2nd parachute")
    S_para_2: float = Field(6.082, description="Parachute area of 2nd parachute [m^2]")
    alt_para_2: float = Field(-100, description="Altitude at which 2nd parachute will be deployed")


class RocketConfigModel(BaseModel):
    """Rocket simulation configuration parameters model."""

    aereodynamic: RocketAereodynamicModel = Field(
        default=RocketAereodynamicModel(),
        description="Rocket aerodynamic parameters",
    )

    rocket_engine: RocketEngineModel = Field(
        default=RocketEngineModel(),
        description="Rocket engine parameters",
    )

    parachute: ParachuteModel = Field(
        default=ParachuteModel(),
        description="Parachute parameters",
    )

    loc: Transform = Field(
        default=Transform(point=Point(139.421333, 34.736139)),
        description="Location of launch site",
    )
