"""XMLレンダリングを行うモジュール"""

from pathlib import Path
from shutil import copy

from jinja2 import Template


def render_template(template: str, render_dict: dict[str, any]) -> str:
    """Render the simulation XML.

    Args:
        template (str): The XML template.
        render_dict (dict[str, any]): The dictionary to render the XML.

    Returns:
        str: The rendered XML.
    """
    template = Template(template)
    return template.render(**render_dict)


def render_and_save_xml_files(
    output_dir: Path,
    rocket_template: str,
    simulation_template: str,
    launch_template: str,
    rocket_param: dict,
    simulation_param: dict,
    launch_param: dict,
    unitconversions_template_path: Path,
) -> None:
    """シミュレーションのXMLファイルをレンダリングして保存する.

    Args:
        output_dir (Path): 出力ディレクトリ.
        rocket_template (str): ロケットのXMLテンプレート.
        simulation_template (str): シミュレーションのXMLテンプレート.
        launch_template (str): 起動のXMLテンプレート.
        rocket_param (dict): ロケットのパラメータ.
        simulation_param (dict): シミュレーションのパラメータ.
        launch_param (dict): 起動のパラメータ.
        unitconversions_template_path (Path): 単位変換のテンプレートパス.
    """
    aircraft_output_dir = output_dir / "aircraft" / "PQ_ROCKET"
    if not aircraft_output_dir.exists():
        aircraft_output_dir.mkdir(parents=True, exist_ok=True)

    rocket_xml = render_template(rocket_template, rocket_param)
    simulation_xml = render_template(simulation_template, simulation_param)
    launch_xml = render_template(launch_template, launch_param)

    with (aircraft_output_dir / "pq_rocket.xml").open("w") as f:
        f.write(rocket_xml)
    with (output_dir / "pq_simulation.xml").open("w") as f:
        f.write(simulation_xml)
    with (aircraft_output_dir / "liftoff.xml").open("w") as f:
        f.write(launch_xml)

    copy(unitconversions_template_path, output_dir / "unitconversions.xml")
