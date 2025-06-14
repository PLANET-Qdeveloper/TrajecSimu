"""ロケットのパラメータのスキーマ."""

from typing import Annotated, Self

from pydantic import BaseModel, BeforeValidator, FilePath, model_validator

from trajecsim.jsbsim_support.schemas.validator import convert_value_to_list, convert_value_to_list_optional


class PqRocketSchema(BaseModel):
    """ロケットのパラメータ"""

    projected_frontal_area: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    wing_span: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    wing_chord: Annotated[list[float], BeforeValidator(convert_value_to_list)]

    # Inertia parameters
    inertia_xx: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    inertia_yy: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    inertia_zz: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    inertia_xy: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    inertia_xz: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    inertia_yz: Annotated[list[float], BeforeValidator(convert_value_to_list)]

    # Mass parameters
    dry_weight: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    cg_x: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    cg_y: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    cg_z: Annotated[list[float], BeforeValidator(convert_value_to_list)]

    cp_x: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    cp_y: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    cp_z: Annotated[list[float], BeforeValidator(convert_value_to_list)]

    diameter: Annotated[list[float], BeforeValidator(convert_value_to_list)]

    # Tank parameters
    tank_x: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    tank_y: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    tank_z: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    tank_drain_x: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    tank_drain_y: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    tank_drain_z: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    tank_radius: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    tank_capacity: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    tank_contents: Annotated[list[float], BeforeValidator(convert_value_to_list_optional)] = []
    tank_density: Annotated[list[float], BeforeValidator(convert_value_to_list)]

    # Fuel parameters
    fuel_x: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    fuel_y: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    fuel_z: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    fuel_drain_x: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    fuel_drain_y: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    fuel_drain_z: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    fuel_radius: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    fuel_capacity: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    fuel_contents: Annotated[list[float], BeforeValidator(convert_value_to_list_optional)] = []
    fuel_density: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    fuel_length: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    fuel_after_burn: Annotated[list[float], BeforeValidator(convert_value_to_list)]

    # Parachute parameters
    parachute_full_deploy_time: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    parachute_area: Annotated[list[float], BeforeValidator(convert_value_to_list_optional)] = []
    terminal_velocity: Annotated[list[float], BeforeValidator(convert_value_to_list_optional)] = []
    parachute_drag_coefficient: Annotated[list[float], BeforeValidator(convert_value_to_list)]

    # Thrust parameters
    thruster_x: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    thruster_y: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    thruster_z: Annotated[list[float], BeforeValidator(convert_value_to_list)]

    # Aerodynamic coefficients
    lift_coefficient_alpha: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    side_coefficient_beta: Annotated[list[float], BeforeValidator(convert_value_to_list_optional)] = []
    roll_damping_coefficient: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    pitch_damping_coefficient: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    pitch_coefficient_alpha: Annotated[list[float], BeforeValidator(convert_value_to_list)]

    yaw_damping_coefficient: Annotated[list[float], BeforeValidator(convert_value_to_list_optional)] = []
    yaw_coefficient_beta: Annotated[list[float], BeforeValidator(convert_value_to_list_optional)] = []
    # Tables
    fuel_remaining_table: Annotated[list[FilePath], BeforeValidator(convert_value_to_list_optional)] = []
    thrust_table: Annotated[list[FilePath], BeforeValidator(convert_value_to_list)]
    cd0_table: Annotated[list[FilePath], BeforeValidator(convert_value_to_list)]
    cdmach_table: Annotated[list[FilePath], BeforeValidator(convert_value_to_list)]

    @model_validator(mode="after")
    def set_default_values(self) -> Self:
        """一部パラメータはデフォルト値がある"""
        if not self.tank_contents:
            self.tank_contents = self.tank_capacity  # 満タンを仮定
        if not self.fuel_contents:
            self.fuel_contents = self.fuel_capacity  # 満タンを仮定
        if not self.side_coefficient_beta:
            self.side_coefficient_beta = self.lift_coefficient_alpha  # ロケットはピッチ、ヨー対称
        if not self.yaw_damping_coefficient:
            self.yaw_damping_coefficient = self.roll_damping_coefficient
        if not self.yaw_coefficient_beta:
            self.yaw_coefficient_beta = self.side_coefficient_beta
        if not (self.parachute_area or self.terminal_velocity):
            raise ValueError("parachute_areaまたはterminal_velocityがひとつも指定されていません")
        return self
