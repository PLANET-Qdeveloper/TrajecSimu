from pathlib import Path

import pandas as pd

from trajecsim.util.kml_generator import KMLGenerator


def summarize_output_info_df(output_info_df: pd.Series, output_dir: Path) -> pd.Series:
    output_file = output_info_df["raw_output_file"]
    output_df = pd.read_csv(output_file)

    altitude_col = "/fdm/jsbsim/position/h-sl-meters"
    speed_col = "velocities/vtrue-ms"
    pressure_col = "aero/qbar-Pa"
    lat_col = "/fdm/jsbsim/position/lat-gc-deg"
    long_col = "/fdm/jsbsim/position/long-gc-deg"

    max_altitude = output_df[altitude_col].max()
    max_speed = output_df[speed_col].max()
    max_pressure = output_df[pressure_col].max()
    landed_lat = output_df[lat_col].iloc[-1]
    landed_long = output_df[long_col].iloc[-1]

    # KMLファイルの生成
    kml_dir = output_dir / "flight_path"
    kml_dir.mkdir(parents=True, exist_ok=True)

    kml_generator = KMLGenerator()

    coordinates_3d = list(zip(output_df[long_col], output_df[lat_col], output_df[altitude_col], strict=False))
    coordinates_2d = list(zip(output_df[long_col], output_df[lat_col], strict=False))

    kml_generator.add_line(coordinates_3d, "flight_path", (255, 0, 0))
    kml_generator.add_line(coordinates_2d, "flight_path", (0, 255, 0))
    kml_generator.save(kml_dir / f"{output_info_df.name}.kml")

    summary_row = {
        "max_altitude": max_altitude,
        "max_speed": max_speed,
        "landed_latitude": landed_lat,
        "landed_longitude": landed_long,
        "max_pressure": max_pressure,
    }
    return pd.Series(summary_row)
