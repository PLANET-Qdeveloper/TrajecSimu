"""JSBSimのシミュレーションを実行する."""

import logging
from os import PathLike, environ
from pathlib import Path
from shutil import copy
from typing import Any

import jsbsim
import pandas as pd

# Get the directory where this script is located
WORKING_DIR = Path("temp/")
LOGGER = logging.getLogger(__name__)


def run_jsb(
    simulation_param_df: pd.Series | dict[str, Any], output_dir: PathLike[Any] | str, file_name_prefix: str = ""
) -> pd.Series:
    """JSBSimのシミュレーションを実行する.

    Args:
        simulation_param_df (pd.Series | dict[str, Any]): シミュレーションパラメータ.
        output_dir (PathLike[Any] | str): 出力ディレクトリ.

    Returns:
        pd.Series: シミュレーションの結果.
    """
    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(str(simulation_param_df.loc["param_dir"].iloc[0]))
    environ["JSBSIM_DEBUG"] = "0"
    fdm = jsbsim.FGFDMExec(str(temp_dir))
    # Disable debug output
    fdm.set_debug_level(0)
    fdm.load_script("pq_simulation.xml")
    fdm.run_ic()
    while fdm.run():
        pass

    output_file = output_dir / f"{simulation_param_df.name}_{file_name_prefix}_.csv"
    copy(
        temp_dir / "pq_rocket_output_raw.csv",
        output_file,
    )
    return pd.Series({"raw_output_file": output_file})
