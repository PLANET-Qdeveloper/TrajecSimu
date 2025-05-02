"""Engine parameters for rocket simulation."""

from enum import Enum
from typing import Self

from pydantic import BaseModel, Field, model_validator

# Engine parameters
DEFAULT_T_MECO = 9.3  # seconds
DEFAULT_THRUST = 800.0  # constant thrust
DEFAULT_THRUST_INPUT_TYPE = "curve_const_t"
DEFAULT_CURVE_FITTING = True
DEFAULT_FITTING_ORDER = 15
DEFAULT_THRUST_MAG_FACTOR = 1.0
DEFAULT_TIME_MAG_FACTOR = 1.0


class ThrustInputType(str, Enum):
    """Enum for thrust input types"""

    RECTANGLE = "rectangle"
    CURVE_CONST_T = "curve_const_t"
    TIME_CURVE = "time_curve"


class ThrustParameters(BaseModel):
    """Engine thrust parameters"""

    thrust_input_type: ThrustInputType = Field(DEFAULT_THRUST_INPUT_TYPE, description="Type of thrust input")
    thrust_mag_factor: float = Field(DEFAULT_THRUST_MAG_FACTOR, description="Thrust magnitude scaling factor")
    time_mag_factor: float = Field(DEFAULT_TIME_MAG_FACTOR, description="Time scaling factor for thrust")

    # For rectangle thrust
    t_MECO: float | None = Field(DEFAULT_T_MECO, description="Time of main engine cut-off in seconds")
    thrust: float | None = Field(DEFAULT_THRUST, description="Constant thrust value in Newtons")

    # For curve thrust
    thrust_dt: float | None = Field(None, description="Time step for constant time thrust curves")
    thrust_filename: str | None = Field(None, description="Filename for thrust curve data")
    curve_fitting: bool = Field(DEFAULT_CURVE_FITTING, description="Flag for curve fitting")
    fitting_order: int = Field(DEFAULT_FITTING_ORDER, description="Order of polynomial fitting")

    @model_validator(mode="after")
    def check_thrust_input_type(self) -> Self:
        """Check thrust input type and validate parameters accordingly."""
        if self.thrust_input_type == ThrustInputType.RECTANGLE and (self.thrust is None or self.t_MECO is None):
            msg = "thrust and t_MECO must be provided for rectangle thrust type"
            raise ValueError(msg)
        if self.thrust_input_type == ThrustInputType.CURVE_CONST_T and (self.thrust_filename is None):
            msg = "thrust_filename must be provided for curve thrust types"
            raise ValueError(msg)
        if self.thrust_input_type == ThrustInputType.TIME_CURVE and (
            self.thrust_input_type == ThrustInputType.CURVE_CONST_T and self.thrust_dt is None
        ):
            msg = "thrust_dt must be provided for curve_const_t thrust type"
            raise ValueError(msg)
