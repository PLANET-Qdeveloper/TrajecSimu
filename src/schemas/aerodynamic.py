from enum import Enum
from typing import Self

from pydantic import BaseModel, Field, field_validator

# Rocket aerodynamics
DEFAULT_AERO_FIN_MODE = "integ"
DEFAULT_CD0 = 0.6
DEFAULT_CMP = 0.0
DEFAULT_CMQ = -4.0
DEFAULT_CL_ALPHA = 12.0  # 1/rad
DEFAULT_MACH_AOA_DEP = True

# Parachute parameters
DEFAULT_T_DEPLOY = 1000.0  # seconds from ignition
DEFAULT_T_PARA_DELAY = 1000.0  # seconds from apogee detection
DEFAULT_CD_PARA = 1.0
DEFAULT_S_PARA = 0.5  # square meters
DEFAULT_ALT_PARA = -100.0  # meters


class AeroFinMode(str, Enum):
    """Enum for aerodynamic fin modes"""

    INTEG = "integ"
    INDIV = "indiv"


class AerodynamicParameters(BaseModel):
    """Aerodynamic parameters"""

    aero_fin_mode: AeroFinMode = Field(DEFAULT_AERO_FIN_MODE, description="Aerodynamic fin calculation mode")
    Cd0: float = Field(DEFAULT_CD0, description="Zero-angle drag coefficient")
    Cmp: float = Field(DEFAULT_CMP, description="Pitch moment coefficient")
    Cmq: float = Field(DEFAULT_CMQ, description="Pitch damping moment coefficient")
    Cl_alpha: float = Field(DEFAULT_CL_ALPHA, description="Lift coefficient per angle of attack (1/rad)")
    Mach_AOA_dep: bool = Field(DEFAULT_MACH_AOA_DEP, description="Flag for Mach/Angle of Attack dependence")
    CP_body: float | None = Field(None, description="Center of pressure of body in meters from reference")


class ParachuteStageParameter(BaseModel):
    """Parachute parameters"""

    t_deploy: float = Field(DEFAULT_T_DEPLOY, description="Parachute deployment time in seconds")
    t_para_delay: float = Field(
        DEFAULT_T_PARA_DELAY, description="Parachute deployment delay after apogee detection or previous parachute"
    )
    Cd_para: float = Field(DEFAULT_CD_PARA, description="Parachute drag coefficient")
    S_para: float = Field(DEFAULT_S_PARA, description="Parachute area in square meters")
    alt_para: float = Field(
        DEFAULT_ALT_PARA,
        description="Altitude for parachute deployment in meters from the apogee or previous parachute",
    )


class ParachuteParameters(BaseModel):
    """Parachute parameters"""

    parachutes = Field(
        default=[ParachuteStageParameter()],
        description="List of parachute parameters for each stage",
    )

    @field_validator("parachutes")
    @classmethod
    def check_parachute_count(cls, parachutes: list[ParachuteStageParameter]) -> Self:
        """Check the number of parachutes"""
        if len(parachutes) < 1:
            msg = "At least one parachute is required"
            raise ValueError(msg)
        return parachutes
