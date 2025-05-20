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
) -> None:
    """Render and save XML files for the simulation.

    Args:
        output_dir (Path): The output directory.
        rocket_template (str): The rocket XML template.
        simulation_template (str): The simulation XML template.
        launch_template (str): The launch XML template.
        rocket_param (dict): The rocket parameters.
        simulation_param (dict): The simulation parameters.
        launch_param (dict): The launch parameters.
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

    copy(
        Path("src/trajecsim/jsbsim_support/param-xml-template/unitconversions.xml"), output_dir / "unitconversions.xml"
    )
