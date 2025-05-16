from typing import Annotated, Self

from pydantic import BaseModel, BeforeValidator, FilePath, model_validator

from jsbsim_support.schemas.validator import convert_value_to_list, convert_value_to_list_optional


class PQ_ROCKETSchema(BaseModel):
    wing_area: Annotated[list[float], BeforeValidator(convert_value_to_list)]

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
    parachute_area: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    parachute_drag_coefficient: Annotated[list[float], BeforeValidator(convert_value_to_list)]

    # Thrust parameters
    thruster_x: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    thruster_y: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    thruster_z: Annotated[list[float], BeforeValidator(convert_value_to_list)]

    # Aerodynamic coefficients
    lift_coefficient_alpha: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    roll_coefficient_beta: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    roll_coefficient_p: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    roll_coefficient_r: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    pitch_coefficient_alpha: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    pitch_coefficient_q: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    yaw_coefficient_beta: Annotated[list[float], BeforeValidator(convert_value_to_list_optional)] = []
    yaw_coefficient_r: Annotated[list[float], BeforeValidator(convert_value_to_list_optional)] = []

    # Tables
    fuel_remaining_table: Annotated[list[FilePath], BeforeValidator(convert_value_to_list_optional)] = []
    thrust_table: Annotated[list[FilePath], BeforeValidator(convert_value_to_list)]
    cd0_table: Annotated[list[FilePath], BeforeValidator(convert_value_to_list)]
    cdmach_table: Annotated[list[FilePath], BeforeValidator(convert_value_to_list)]

    @model_validator(mode="after")
    def set_default_values(self) -> Self:
        if not self.tank_contents:
            self.tank_contents = self.tank_capacity
        if not self.fuel_contents:
            self.fuel_contents = self.fuel_capacity
        if not self.yaw_coefficient_beta:
            self.yaw_coefficient_beta = self.pitch_coefficient_alpha
        if not self.yaw_coefficient_r:
            self.yaw_coefficient_r = self.pitch_coefficient_q
        return self
