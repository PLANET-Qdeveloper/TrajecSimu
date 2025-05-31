"""パラメータ生成のメイン機能を提供するモジュール"""

import logging
import math
from os import cpu_count
from pathlib import Path

import pandas as pd
from omegaconf import DictConfig
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map as tqdm_process_map

from trajecsim.jsbsim_support.param_generator.fuel_table import generate_fuel_remaining_table
from trajecsim.jsbsim_support.param_generator.parameter_product import generate_dicts_product
from trajecsim.jsbsim_support.param_generator.wind_table import generate_wind_table
from trajecsim.jsbsim_support.param_generator.xml_renderer import render_and_save_xml_files
from trajecsim.jsbsim_support.param_generator.yaml_loader import (
    convert_omegaconf_to_schema,
    load_csv_to_dict,
)

LOGGER = logging.getLogger(__name__)
GRAVITY_ACCELERATION = 9.80665
AIR_DENSITY = 1.225


def _tuple_to_str_optional(val: tuple[float, ...] | float) -> str:
    if isinstance(val, float):
        return str(val)
    return "_".join(map(str, val))


def _process_parameter_combination(args: tuple[int, pd.Series, dict[str, str], Path, Path]) -> tuple[int, Path]:
    """個別のパラメータ組み合わせを処理する関数"""
    index, row, templates, rendered_param_dir, unitconversions_template_path = args
    output_dir = rendered_param_dir / f"{index}"
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    rocket_param = row["rocket"].to_dict()
    simulation_param = row["simulation"].to_dict()
    launch_param = row["launch"].to_dict()

    # ランチャーの高さを計算
    # ランチャーの高さは、ランチャーの長さとピッチの角度から計算される
    simulation_param["launcher_height"] = launch_param["elevation"] + launch_param["launcher_length"] * math.sin(
        launch_param["pitch"] * math.pi / 180,
    )
    # 風テーブルの生成
    simulation_param["winds_table"] = generate_wind_table(
        launch_param["ground_wind_dir"],
        launch_param["ground_wind_speed"],
        launch_param["elevation"],
        launch_param["wind_power_factor"],
    )

    # パラシュートの面積を計算
    if not rocket_param.get("parachute_area"):
        rocket_param["parachute_area"] = (
            (
                2
                * (rocket_param["dry_weight"] - rocket_param["fuel_contents"])
                * GRAVITY_ACCELERATION
                / (rocket_param["terminal_velocity"] ** 2 * rocket_param["parachute_drag_coefficient"] * AIR_DENSITY)
            )
            if rocket_param.get("terminal_velocity") != 0
            else 0
        )

    # XMLファイルの生成
    render_and_save_xml_files(
        output_dir,
        templates["rocket"],
        templates["simulation"],
        templates["launch"],
        rocket_param,
        simulation_param,
        launch_param,
        unitconversions_template_path,
    )
    return index, output_dir


def generate_param_xml(params: DictConfig, template_dir: Path | str) -> pd.DataFrame:
    """Generate parameter XML files for the simulation.

    Args:
        params (DictConfig): The parameters to generate the XML files.
        template_dir (Path | str): The path to the template directory.

    Returns:
        pd.DataFrame: DataFrame containing all parameter combinations.
    """
    try:
        rocket_params_schema, simulation_params_schema, launch_params_schema = convert_omegaconf_to_schema(params)
    except KeyError:
        LOGGER.exception(f"パラメータファイルが不正です: {params}")
        raise

    LOGGER.info("テンプレートファイルを読み込みます")
    template_dir = Path(template_dir)
    aircraft_dir = Path("aircraft/PQ_ROCKET")

    try:
        templates = {
            "rocket": (template_dir / aircraft_dir / "pq_rocket.xml.j2").read_text(),
            "simulation": (template_dir / "pq_simulation.xml.j2").read_text(),
            "launch": (template_dir / aircraft_dir / "liftoff.xml.j2").read_text(),
        }
    except FileNotFoundError:
        LOGGER.exception(f"テンプレートファイルが見つかりません: {template_dir}")
        raise

    LOGGER.info("csvファイルの読み込みを行います")
    try:
        rocket_params = load_csv_to_dict(rocket_params_schema.model_dump())
        simulation_params = load_csv_to_dict(simulation_params_schema.model_dump())
        launch_params = load_csv_to_dict(launch_params_schema.model_dump())
    except FileNotFoundError:
        LOGGER.exception("テンプレートで指定された、csvファイルが見つかりません")
        raise

    # 燃料テーブルの生成
    if not rocket_params.get("fuel_remaining_table"):
        rocket_params["fuel_remaining_table"] = [
            generate_fuel_remaining_table(thrust_table) for thrust_table in rocket_params["thrust_table"]
        ]

    # パラメータの組み合わせを生成
    LOGGER.info("パラメータの組み合わせを生成します")
    all_parameter_products = generate_dicts_product(
        {
            "rocket": rocket_params,
            "simulation": simulation_params,
            "launch": launch_params,
        },
    )

    LOGGER.info("XMLファイルの生成を行います")
    rendered_param_dir = Path("temp/jsbsim/param-generated-xml")
    unitconversions_template_path = template_dir / "unitconversions.xml"
    args_list = [
        (index, row, templates, rendered_param_dir, unitconversions_template_path)
        for index, row in tqdm(all_parameter_products.iterrows(), desc="パラメータの組み合わせを生成中")
    ]

    results = tqdm_process_map(
        _process_parameter_combination,
        args_list,
        max_workers=cpu_count(),
        total=len(args_list),
        desc="XMLファイルを生成中",
    )

    # 結果をDataFrameに反映
    for index, output_dir in results:
        all_parameter_products.loc[index, "param_dir"] = output_dir

    return all_parameter_products
