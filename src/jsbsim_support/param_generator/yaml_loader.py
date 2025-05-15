"""YAMLファイルの読み込みと変換を行うモジュール"""

from pathlib import Path

import pandas as pd
from omegaconf import DictConfig, ListConfig, OmegaConf

from jsbsim_support.schemas.launch import LaunchConfig
from jsbsim_support.schemas.rocket import PQ_ROCKETSchema
from jsbsim_support.schemas.simulation import JSBSimConfig


def load_yaml_parameters(yaml_path: Path | str) -> DictConfig | ListConfig:
    """Load the YAML parameters from the given path.

    Args:
        yaml_path (Path | str): The path to the YAML file.

    Raises:
        FileNotFoundError: If the YAML file does not exist.

    Returns:
        DictConfig | ListConfig: The YAML parameters.
    """
    yaml_path = Path(yaml_path)
    if not yaml_path.exists():
        raise FileNotFoundError(yaml_path)
    return OmegaConf.load(yaml_path)


def convert_omegaconf_to_schema(
    params: DictConfig | ListConfig,
) -> tuple[PQ_ROCKETSchema, JSBSimConfig, LaunchConfig]:
    """Convert the YAML parameters to the schema.

    Args:
        params (DictConfig | ListConfig): The YAML parameters.

    Raises:
        KeyError: If the YAML parameters are missing required keys.

    Returns:
        tuple[PQ_ROCKETSchema, JSBSimConfig, LaunchConfig]: The converted parameters.
    """
    required_keys = ["rocket", "simulation", "launch"]
    missing_keys = [key for key in required_keys if key not in params]
    if missing_keys:
        raise KeyError(missing_keys)

    rocket_params = PQ_ROCKETSchema(**params.rocket)
    simulation_params = JSBSimConfig(**params.simulation)
    launch_params = LaunchConfig(**params.launch)
    return rocket_params, simulation_params, launch_params


def load_csv_to_tuple_list(csv_path: Path | str) -> list[tuple[float, float]]:
    """Load the CSV file to a list of tuples.

    Args:
        csv_path (Path | str): The path to the CSV file.

    Returns:
        list[tuple[str, float]]: The list of tuples.
    """
    if not Path(csv_path).exists():
        raise FileNotFoundError(csv_path)

    # まず先頭行だけ読み込んで内容を確認
    df_temp = pd.read_csv(csv_path, header=None, nrows=1)

    # 最初の行に非数値があるかチェック
    first_row = df_temp.iloc[0]
    is_all_numeric = True

    for value in first_row:
        # 数値に変換できるかテスト
        try:
            if pd.notna(value):  # NaN値でない場合
                float(value)
        except (ValueError, TypeError):
            # 変換できない場合は非数値
            is_all_numeric = False
            break

    # 適切なheader設定でCSVを再読み込み
    df_csv = pd.read_csv(csv_path, header=None) if is_all_numeric else pd.read_csv(csv_path, header=0)

    # DataFrameをタプルのリストに変換
    return [tuple(row) for row in df_csv.to_numpy()]


def load_csv_to_dict(param_dict: any) -> dict[str, any]:
    """Load the CSV file to a dictionary.

    Args:
        param_dict (Any): The dictionary to load the CSV file to.

    Returns:
        dict[str, Any]: The dictionary.
    """
    if isinstance(param_dict, dict):
        # 辞書の場合、各値を再帰的に処理
        return {key: load_csv_to_dict(value) for key, value in param_dict.items()}
    elif isinstance(param_dict, list):
        # リストの場合、各項目を再帰的に処理
        return [load_csv_to_dict(item) for item in param_dict]
    elif isinstance(param_dict, (Path, str)):
        # 数値の場合、2倍にする
        return load_csv_to_tuple_list(param_dict)
    else:
        # その他の型の場合、そのまま返す
        return param_dict
