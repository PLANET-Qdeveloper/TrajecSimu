"""起動のパラメータのスキーマ."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, FilePath

from trajecsim.jsbsim_support.schemas.validator import convert_value_to_list, convert_value_to_list_optional


class LaunchConfig(BaseModel):
    """打場パラメータ"""

    yaw: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    pitch: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    roll: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    latitude: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    longitude: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    elevation: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    wind_power_factor: Annotated[list[float], BeforeValidator(convert_value_to_list_optional)] = []
    winds_table: Annotated[list[FilePath], BeforeValidator(convert_value_to_list_optional)] = []
    ground_wind_dir: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    ground_wind_speed: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    launcher_length: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    range_kmz: Annotated[list[FilePath], BeforeValidator(convert_value_to_list_optional)] = []
