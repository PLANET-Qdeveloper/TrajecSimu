from collections.abc import Sequence
from os import PathLike
from typing import Any

import pandas as pd
from pydantic import BaseModel, field_validator


class JSBSimConfig(BaseModel):
    flight_duration: float = 60
    time_step: float = 0.01
    winds_dir_table: Sequence[tuple[float, float]] = []
    winds_speed_table: Sequence[tuple[float, float]] = []
    parachute_deploy_delay: float = 3.0
    notify_interval: float = 5.0
    output_rate: int = 100

    @field_validator("winds_dir_table", "winds_speed_table", mode="before")
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
