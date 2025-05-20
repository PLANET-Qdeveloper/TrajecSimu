"""メインのシミュレーション実行スクリプト"""

import argparse
from pathlib import Path

import jsbsim
import pandas as pd
from tqdm import tqdm

from trajecsim.jsbsim_support.generate_param_xml import generate_param_xml
from trajecsim.jsbsim_support.jsb_runner import run_jsb
from trajecsim.util.kml_generator import KMLGenerator
from trajecsim.util.logger import setup_logging
from trajecsim.util.summarize import summarize_output_info_df


def get_arguments() -> argparse.Namespace:
    """コマンドライン引数をパース

    Returns:
        args: 取得した引数
    """
    parser = argparse.ArgumentParser(description="Trajectory Simulation")
    parser.add_argument(
        "--config_file_path",
        type=str,
        default="data/sample/sample.yaml",
        help="Path to the configuration file",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="data/result",
        help="Output directory",
    )
    args = parser.parse_args()
    return args


def main(config_file_path: str, output_dir: str) -> None:
    """メイン関数"""
    _ = jsbsim.FGFDMExec(None)

    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    logger = setup_logging(output_dir / "log.txt")
    logger.info(f"シミュレーションを開始します: {config_file_path}")
    simulation_df = generate_param_xml(config_file_path)

    logger.info("シミュレーションを実行します")
    tqdm.pandas(desc="シミュレーションを実行中🚀")
    simulation_df = pd.concat(
        [simulation_df, simulation_df.progress_apply(run_jsb, axis=1, output_dir=output_dir / "raw_result")], axis=1
    )

    logger.info("シミュレーションの結果を集計します")
    tqdm.pandas(desc="シミュレーションの結果を集計中")
    simulation_df = pd.concat(
        [simulation_df, simulation_df.progress_apply(summarize_output_info_df, axis=1, output_dir=output_dir)], axis=1
    )

    logger.info("シミュレーションの結果を保存します")
    simulation_df[simulation_df.columns[-6:]].to_csv(output_dir / "summary.csv", index=False)
    simulation_df.select_dtypes(include=["number"]).to_csv(output_dir / "simulation_params.csv", index=False)

    logger.info("KMLファイルを生成します")
    kml_generator = KMLGenerator()
    grouped_by_wind_speed = simulation_df.groupby(("launch", "ground_wind_speed"))
    kml_generator.generate_grouped_points_polygons(grouped_by_wind_speed)

    simulation_df.apply(
        lambda x: kml_generator.add_point(
            (x["landed_longitude"], x["landed_latitude"]),
            x.name,
            (255, 0, 0),
        ),
        axis=1,
    )
    kml_generator.save(output_dir / "result.kml")


if __name__ == "__main__":
    # コマンドライン引数を取得
    args = get_arguments()
    # 引数を取得
    config_file_path = args.config_file_path
    output_dir = args.output_dir
    main(config_file_path, output_dir)
