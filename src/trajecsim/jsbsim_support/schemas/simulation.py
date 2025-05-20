from typing import Annotated

from pydantic import BaseModel, BeforeValidator

from trajecsim.jsbsim_support.schemas.validator import convert_value_to_list


class JSBSimConfig(BaseModel):
    flight_duration: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    time_step: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    parachute_deploy_delay: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    notify_interval: Annotated[list[float], BeforeValidator(convert_value_to_list)]
    output_rate: Annotated[list[int], BeforeValidator(convert_value_to_list)]
