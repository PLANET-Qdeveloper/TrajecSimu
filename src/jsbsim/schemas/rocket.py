from collections.abc import Sequence
from os import PathLike
from typing import Any, Self

import pandas as pd
from pydantic import BaseModel, field_validator, model_validator


class PQ_ROCKETSchema(BaseModel):
    # Inertia parameters
    inertia_xx: float = 0.0
    inertia_yy: float = 0.0
    inertia_zz: float = 0.0
    inertia_xy: float = 0.0
    inertia_xz: float = 0.0
    inertia_yz: float = 0.0

    # Mass parameters
    dry_weight: float = 0.0
    cg_x: float = 0.0
    cg_y: float = 0.0
    cg_z: float = 0.0

    # Tank parameters
    tank_x: float = 0.0
    tank_y: float = 0.0
    tank_z: float = 0.0
    tank_radius: float = 0.0
    tank_capacity: float = 0.0
    tank_contents: float | None = None
    tank_density: float = 0.0

    # Fuel parameters
    fuel_x: float = 0.0
    fuel_y: float = 0.0
    fuel_z: float = 0.0
    fuel_radius: float = 0.0
    fuel_capacity: float = 0.0
    fuel_contents: float | None = None
    fuel_density: float = 0.0
    fuel_length: float = 0.0
    fuel_after_burn: float = 0.0

    # Parachute parameters
    parachute_full_deploy_time: float = 0.0
    parachute_area: float = 0.0
    parachute_drag_coefficient: float = 0.0

    # Thrust parameters
    thruster_x: float = 0.0
    thruster_y: float = 0.0
    thruster_z: float = 0.0

    # Aerodynamic coefficients
    lift_coefficient_alpha: float = 0.0
    roll_coefficient_beta: float = 0.0
    roll_coefficient_p: float = 0.0
    roll_coefficient_r: float = 0.0
    pitch_coefficient_alpha: float = 0.0
    pitch_coefficient_q: float = 0.0
    yaw_coefficient_beta: float | None = None
    yaw_coefficient_r: float | None = None

    # Tables
    fuel_remaining_table: Sequence[tuple[float, float]] = [(0, 100)]
    thrust_table: Sequence[tuple[float, float]] = [(0, 0)]
    cd0_table: Sequence[tuple[float, float]] = [(0, 0)]
    cdmach_table: Sequence[tuple[float, float]] = [(0, 0)]

    @field_validator("fuel_remaining_table", "thrust_table", "cd0_table", "cdmach_table", mode="before")
    @classmethod
    def validate_tables(cls, v: str | PathLike[Any] | Sequence[tuple[float, float]]) -> Sequence[tuple[float, float]]:
        if isinstance(v, (PathLike, str)):
            # Read CSV content
            input_csv_df = pd.read_csv(v, header="infer")

            # If we have more than 2 columns or column names don't match data types,
            # try reading without header
            if len(input_csv_df.columns) != 2 or not all(
                pd.api.types.is_numeric_dtype(dtype) for dtype in input_csv_df.dtypes
            ):
                input_csv_df = pd.read_csv(v, header=None)
            # Convert to list of tuples
            v = list(zip(input_csv_df.iloc[:, 0], input_csv_df.iloc[:, 1], strict=True))
        if not v:
            return [(0, 0)]
        return v

    @model_validator(mode="after")
    def set_default_values(self) -> Self:
        if self.tank_contents is None:
            self.tank_contents = self.tank_capacity
        if self.fuel_contents is None:
            self.fuel_contents = self.fuel_capacity
        if self.yaw_coefficient_beta is None:
            self.yaw_coefficient_beta = self.pitch_coefficient_alpha
        if self.yaw_coefficient_r is None:
            self.yaw_coefficient_r = self.pitch_coefficient_q
        return self
