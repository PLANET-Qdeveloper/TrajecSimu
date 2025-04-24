"""Location schema."""

import numpy as np
import quaternion
from pydantic import BaseModel, field_validator
from shapely import Point


class TransformValidateError(Exception):
    """Location validation error."""

    def __init__(self, data: any) -> None:  # noqa: D107
        super().__init__(f"Invalid data for Location: {data}")


class TransformQuaternionError(Exception):
    """Location validation error."""

    def __init__(self, data: any) -> None:  # noqa: D107
        super().__init__(f"Invalid data for Location: {data}")


class Transform(BaseModel):
    """Location model."""

    point: Point
    quartanion: quaternion.quaternion | None = None
    location_name: str | None = None

    @classmethod
    @field_validator("point")
    def validate_point(cls, v: Point | list[str] | dict[str, str]) -> Point:
        """Validate point.

        Args:
            v: Point or list of strings or dict of strings

        Returns:
            Point: validated point
        """
        if isinstance(v, Point):
            return v
        if isinstance(v, list):
            return Point([float(coord) for coord in v])
        if isinstance(v, dict):
            if "lat" in v and "lon" in v:
                return Point([float(v["lon"]), float(v["lat"])])
            if "latitude" in v and "longitude" in v:
                return Point([float(v["longitude"]), float(v["latitude"])])
            raise TransformValidateError(v)
        raise TransformValidateError(v)

    def get_euler(self) -> np.ndarray:
        """Get Euler angles from quaternion.

        Returns:
            np.ndarray: Euler angles
        """
        if self.quartanion is None:
            raise TransformQuaternionError(self)
        return quaternion.as_euler_angles(self.quartanion)
