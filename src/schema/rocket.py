"""シミュレーションパラメータの定義"""

import numpy as np
from pydantic import BaseModel, Field, model_validator
from shapely.geometry import Point

from schema.sim_parameter import AeroFinMode
from schema.transform import Transform


class RocketAereodynamicModel(BaseModel):
    """Rocket aerodynamic model."""

    roll_damping: float = Field(
        0.0, description="Stability derivative of rolling moment coefficient (aerodynamic damping)"
    )  # Pitch down moment at 0deg AoA
    pitch_yaw_damping: float = Field(
        0.0, description="Stability derivative of pitching/yawing moment coefficient (aerodynamic damping)"
    )  # Pitch down moment at 0deg AoA

    center_of_pressure: float = Field(
        0.0, description="Center of pressure from nose cone tip [m]"
    )  # Center of pressure from nose cone tip
    drag_coefficient: float = Field(0.0, description="Drag coefficient at mach 0.1, AoA = 0deg")
    lift_curve_slope: float = Field(0.0, description="Lift curve slope. Cl_alpha")
    # Rocket aerodynamic parameters
    aero_fin_mode: AeroFinMode = Field(
        "integ", description="'indiv' for individual fin computation, 'integ' for compute fin-body at once"
    )
    Mach_AOA_dep: bool = Field(
        default=True, description="True if aerodynamic parameter depends on Mach/AOA, False if ignore"
    )


class RocketEngineModel(BaseModel):
    """Rocket engine model."""

    # Rocket engine parameters
    cutoff_time: float = Field(9.3, description="Main Engine Cut Off (meco) time")
    thrust: float = Field(800.0, description="Thrust (const.)")
    curve_fitting: bool = Field(default=True, description="True if curvefitting")
    fitting_order: int = Field(15, description="Order of polynomial")
    thrust_mag_factor: float = Field(1.0, description="Thrust magnification factor")
    time_mag_factor: float = Field(1.0, description="Burn time magnification factor")


class ParachuteModel(BaseModel):
    """Parachute model."""

    # Parachute parameters
    deplou_time_from_ignition: float = Field(1000.0, description="Parachute deployment time from ignition")
    deploy_time_from_apogee: float = Field(1000.0, description="Parachute deployment time from apogee detection")
    drag_coefficient: float = Field(1.0, description="Drag coefficient of 1st parachute")
    area: float = Field(0.5, description="Parachute area of 1st parachute [m^2]")


class RocketShapeModelError(Exception):
    """Rocket shape model validation error."""

    def __init__(self, data: any, name: str) -> None:  # noqa: D107
        super().__init__(f"Invalid data for RocketShapeModel: {name}:{data}")


class RocketShapeModel(BaseModel):
    """Rocket shape model."""

    # Rocket shape parameters
    height: float = Field(2.0, description="Length of rocket body")
    diameter: float = Field(0.1, description="Diameter of rocket body")
    dry_mass: float = Field(0.5, description="Mass of rocket body")
    fill_mass: float = Field(0.1, description="Mass of rocket body with oxidant")
    dry_center: float = Field(0.01, description="Center of mass of rocket body")
    ill_center: float = Field(3, description="Center of mass of rocket body with oxidant")
    moment_of_inertia_dry: np.ndarray = Field(np.ndarray([0, 0, 0]), description="Moment of inertia of rocket body")
    moment_of_inertia_fill: np.ndarray = Field(
        np.ndarray([0, 0, 0]), description="Moment of inertia of rocket body with oxidant"
    )
    launch_lugs_position: np.ndarray = Field(
        np.array([0.0, 0.0, 0.0]), description="Position of launch lugs from nose cone tip"
    )

    @classmethod
    @model_validator(mode="after")
    def validate_rocket_dry_center(cls, v: float) -> float:
        if v < 0.0 or v > cls.rocket_height:
            raise RocketShapeModelError(cls.rocket_height, "rocket_dry_center")
        return v

    @classmethod
    @model_validator(mode="after")
    def validate_rocket_fill_center(cls, v: int) -> int:
        if v < 0 or v > cls.rocket_height:
            raise RocketShapeModelError(cls.rocket_height, "rocket_fill_center")
        return v


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

    parachute: list[ParachuteModel] = Field(
        default=[ParachuteModel()],
        description="Parachute parameters",
    )

    loc: Transform = Field(
        default=Transform(point=Point(139.421333, 34.736139)),
        description="Location of launch site",
    )
