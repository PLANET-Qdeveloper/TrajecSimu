from os import PathLike
from pathlib import Path
from shutil import copy
from typing import Any

import jsbsim
import pandas as pd

from jsbsim_support.generate_param_xml import generate_param_xml

# Get the directory where this script is located
WORKING_DIR = Path("temp/")


def run_jsb(simulation_param_df: pd.Series | dict[str, Any], output_dir: PathLike[Any] | str) -> pd.Series:
    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(str(simulation_param_df.loc["param_dir"].iloc[0]))
    fdm = jsbsim.FGFDMExec(str(temp_dir))
    fdm.load_script("pq_simulation.xml")

    fdm.run_ic()

    while fdm.run():
        pass
    output_file = output_dir / f"{simulation_param_df.name}_pq_rocket_output_raw.csv"
    copy(
        temp_dir / "pq_rocket_output_raw.csv",
        output_file,
    )
    return pd.Series({"raw_output_file": output_file})
