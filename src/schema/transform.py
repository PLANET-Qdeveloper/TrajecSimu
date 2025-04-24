"""Location schema."""

import numpy as np
from pydantic import BaseModel, field_validator
from scipy.spatial.transform import Rotation


def calculate_rotation_vector(azimuth: float, elevation: float, degrees: bool = True) -> np.ndarray:
    """Calculate rotation vector from azimuth and elevation angles.

    Parameters:
    -----------
    azimuth : float
        Azimuth angle (rotation around the z-axis, 0 is North/+y, increases clockwise)
    elevation : float
        Elevation angle (angle above the horizontal plane)
    degrees : bool, optional
        If True, input angles are in degrees, otherwise in radians

    Returns:
    --------
    rotation_vector : numpy.ndarray
        3D rotation vector where the direction represents the axis of rotation
        and the magnitude represents the angle of rotation in radians
    """
    # Convert to radians if needed
    if degrees:
        azimuth = np.radians(azimuth)
        elevation = np.radians(elevation)

    # Calculate the axis of rotation (as a unit vector)
    axis_x = -np.sin(azimuth)
    axis_y = np.cos(azimuth)
    axis_z = 0.0

    # Create rotation around vertical axis (azimuth)
    vertical_rotation = np.array([0, 0, 1]) * azimuth

    # Create rotation around horizontal axis (elevation)
    horizontal_axis = np.array([axis_x, axis_y, axis_z])
    horizontal_rotation = horizontal_axis * elevation

    # Combine rotations using Rodriguez formula
    # This is a simplified approach - for a complete solution,
    # consider using quaternions or rotation matrices
    return vertical_rotation + horizontal_rotation


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

    point: np.ndarray
    rotation: Rotation | None = None

    @classmethod
    @field_validator("point")
    def validate_point(cls, v: np.ndarray | list[str]) -> np.ndarray:
        """Validate point.

        Args:
            v: Point or list of strings or dict of strings

        Returns:
            Point: validated point
        """
        if isinstance(v, np.ndarray):
            if v.shape != (3,):
                raise TransformValidateError(v)
            return v
        if isinstance(v, list):
            return np.ndarray([float(coord) for coord in v])
        raise TransformValidateError(v)

    @classmethod
    @field_validator("rotation")
    def validate_rotation(cls, v: Rotation | np.ndarray | list | None) -> Rotation:
        """Validate rotation.

        Args:
            v: Rotation or None

        Returns:
            Rotation: validated rotation
        """
        if v is None:
            return Rotation.from_euler("xyz", [0, 0, 0], degrees=True)
        if isinstance(v, (np.ndarray, list)):
            if isinstance(v, list):
                v = np.array(v)
            if v.shape == (4,):
                return Rotation.from_quat(v)
            if v.shape == (3,):
                return Rotation.from_euler("xyz", v, degrees=True)
            if v.shape == (2,):
                return Rotation.from_euler("xyz", calculate_rotation_vector(v[0], v[1]), degrees=True)
        if isinstance(v, Rotation):
            return v
        raise TransformValidateError(v)

    def get_euler(self) -> np.ndarray:
        """Get Euler angles from quaternion.

        Returns:
            np.ndarray: Euler angles
        """
        if self.quartanion is None:
            raise TransformQuaternionError(self)
        return
