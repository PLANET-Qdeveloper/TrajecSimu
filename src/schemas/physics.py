from enum import Enum
from typing import List, Literal, Optional, Union

import numpy as np
from pydantic import BaseModel, Field, computed_field, field_validator


class MassParameters(BaseModel):
    """Mass and center of gravity parameters"""

    m_dry: float = Field(..., description="Dry mass of the rocket in kg")
    m_prop: float = Field(..., description="Propellant mass in kg")
    CG_dry: float = Field(..., description="Center of gravity of dry rocket in meters from reference")
    CG_prop: float = Field(..., description="Center of gravity of propellant in meters from reference")
    MOI_dry_x: float = Field(..., description="Moment of inertia of dry rocket about x-axis")
    MOI_dry_y: float = Field(..., description="Moment of inertia of dry rocket about y-axis")
    MOI_dry_z: float = Field(..., description="Moment of inertia of dry rocket about z-axis")
    MOI_prop_x: float = Field(..., description="Moment of inertia of propellant about x-axis")
    MOI_prop_y: float = Field(..., description="Moment of inertia of propellant about y-axis")
    MOI_prop_z: float = Field(..., description="Moment of inertia of propellant about z-axis")

    @computed_field
    @property
    def MOI_dry(self) -> np.ndarray:
        """Moment of inertia of dry rocket as a 3x3 matrix"""
        return np.array([[self.MOI_dry_x, 0, 0], [0, self.MOI_dry_y, 0], [0, 0, self.MOI_dry_z]])

    @computed_field
    @property
    def MOI_prop(self) -> np.ndarray:
        """Moment of inertia of propellant as a 3x3 matrix"""
        return np.array([[self.MOI_prop_x, 0, 0], [0, self.MOI_prop_y, 0], [0, 0, self.MOI_prop_z]])


class LugParameters(BaseModel):
    """Launch lug parameters"""

    lugs: list[float] = Field(
        default=[0.0],
        description="Launch lug positions from nose cone tip in meters",
    )

    @field_validator("lugs")
    @classmethod
    def check_lug_positions(cls, v: list[float]) -> list[float]:
        """Check that lug positions are in ascending order"""
        if len(v) < 2:
            msg = "At least two lug positions are required"
            raise ValueError(msg)
        if not all(v[i] < v[i + 1] for i in range(len(v) - 1)):
            msg = "Lug positions must be in ascending order"
            raise ValueError(msg)
        return v
