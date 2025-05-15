"""パラメータ生成のメイン機能を提供するモジュール"""

from pathlib import Path

import pandas as pd

from jsbsim_support.param_generator.fuel_table import generate_fuel_remaining_table
from jsbsim_support.param_generator.parameter_product import generate_dicts_product
from jsbsim_support.param_generator.wind_table import generate_wind_table
from jsbsim_support.param_generator.xml_renderer import render_and_save_xml_files
from jsbsim_support.param_generator.yaml_loader import (
    convert_omegaconf_to_schema,
    load_csv_to_dict,
    load_yaml_parameters,
)


def generate_param_xml(yaml_path: Path | str) -> pd.DataFrame:
    """Generate parameter XML files for the simulation.

    Args:
        yaml_path (Path | str): The path to the YAML configuration file.

    Returns:
        pd.DataFrame: DataFrame containing all parameter combinations.
    """
    params = load_yaml_parameters(yaml_path)
    rocket_params_schema, simulation_params_schema, launch_params_schema = convert_omegaconf_to_schema(params)

    # テンプレートファイルの読み込み
    template_dir = Path("src/jsbsim_support/param-xml-template")
    aircraft_dir = Path("aircraft/PQ_ROCKET")
    rocket_template = (template_dir / aircraft_dir / "pq_rocket.xml.j2").read_text()
    simulation_template = (template_dir / "pq_simulation.xml.j2").read_text()
    launch_template = (template_dir / aircraft_dir / "liftoff.xml.j2").read_text()

    # パラメータの読み込み
    rocket_params = load_csv_to_dict(rocket_params_schema.model_dump())
    simulation_params = load_csv_to_dict(simulation_params_schema.model_dump())
    launch_params = load_csv_to_dict(launch_params_schema.model_dump())

    # 燃料テーブルの生成
    if not rocket_params.get("fuel_remaining_table"):
        rocket_params["fuel_remaining_table"] = [
            generate_fuel_remaining_table(thrust_table) for thrust_table in rocket_params["thrust_table"]
        ]

    # 風テーブルの生成
    if not launch_params.get("winds_table"):
        del launch_params["winds_table"]

    # パラメータの組み合わせを生成
    all_parameter_products = generate_dicts_product(
        {
            "rocket": rocket_params,
            "simulation": simulation_params,
            "launch": launch_params,
        }
    )

    # 各パラメータの組み合わせに対してXMLファイルを生成
    rendered_param_dir = Path("temp/jsbsim/param-generated-xml")
    for index, row in all_parameter_products.iterrows():
        output_dir = rendered_param_dir / f"{index}"
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        all_parameter_products.loc[index, "param_dir"] = output_dir

        rocket_param = row["rocket"].to_dict()
        simulation_param = row["simulation"].to_dict()
        launch_param = row["launch"].to_dict()

        # 風テーブルの生成
        if not launch_param.get("winds_table"):
            simulation_param["winds_table"] = generate_wind_table(
                launch_param["ground_wind_dir"],
                launch_param["ground_wind_speed"],
                launch_param["elevation"],
                launch_param["wind_power_factor"],
            )
        else:
            simulation_params["winds_table"] = launch_params["winds_table"]

        # XMLファイルの生成
        render_and_save_xml_files(
            output_dir,
            rocket_template,
            simulation_template,
            launch_template,
            rocket_param,
            simulation_param,
            launch_param,
        )

    return all_parameter_products
