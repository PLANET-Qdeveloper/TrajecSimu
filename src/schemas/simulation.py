"""Simulation parameter schema module"""

from enum import Enum
from typing import List, Literal, Optional, Union

import numpy as np
from pydantic import BaseModel, Field, validator

# Constants
DEFAULT_DT = 0.05
DEFAULT_T_MAX = 6000  # 100*60 seconds
DEFAULT_N_RECORD = 500
DEFAULT_INTEGRATION = "lsoda_odeint"


class IntegrationMethod(str, Enum):
    """Enum for integration methods"""

    LSODA_ODEINT = "lsoda_odeint"
    # Add other integration methods as needed


class NumericalParameters(BaseModel):
    """Numerical executive parameters"""

    dt: float = Field(DEFAULT_DT, description="Time step for numerical integration")
    t_max: float = Field(DEFAULT_T_MAX, description="Maximum simulation time")
    N_record: float = Field(DEFAULT_N_RECORD, description="Number of data points to record")
    integ: IntegrationMethod = Field(DEFAULT_INTEGRATION, description="Integration method")
