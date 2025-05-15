from pathlib import Path

import pandas as pd

from util.kml_generator import KMLGenerator


def summarize_output_info_df(output_info_df: pd.Series, output_dir: Path) -> pd.Series:
    output_file = output_info_df["raw_output_file"]
    output_df = pd.read_csv(output_file)
    max_altitude_df = output_df.loc[output_df["/fdm/jsbsim/position/h-sl-meters"].idxmax()]
    max_speed_df = output_df.loc[output_df["velocities/vtrue-ms"].idxmax()]
    max_pressure_df = output_df.loc[output_df["aero/qbar-Pa"].idxmax()]
    landed_df = output_df.iloc[-1]

    kml_dir = output_dir / "flight_path"
    kml_dir.mkdir(parents=True, exist_ok=True)

    kml_generator = KMLGenerator()
    kml_generator.add_line(
        [
            (
                row["/fdm/jsbsim/position/long-gc-deg"],
                row["/fdm/jsbsim/position/lat-gc-deg"],
                row["/fdm/jsbsim/position/h-sl-meters"],
            )
            for _, row in output_df.iterrows()
        ],
        "flight_path",
        (255, 0, 0),
    )
    kml_generator.add_line(
        [
            (
                row["/fdm/jsbsim/position/long-gc-deg"],
                row["/fdm/jsbsim/position/lat-gc-deg"],
            )
            for _, row in output_df.iterrows()
        ],
        "flight_path",
        (0, 255, 0),
    )
    kml_generator.save(kml_dir / f"{output_info_df.name}.kml")
    kml_generator.save(kml_dir / f"{output_info_df.name}.kml")

    summary_row = {
        "max_altitude": max_altitude_df["/fdm/jsbsim/position/h-sl-meters"],
        "max_speed": max_speed_df["velocities/vtrue-ms"],
        "landed_latitude": landed_df["/fdm/jsbsim/position/lat-gc-deg"],
        "landed_longitude": landed_df["/fdm/jsbsim/position/long-gc-deg"],
        "max_pressure": max_pressure_df["aero/qbar-Pa"],
    }
    return pd.Series(summary_row)
