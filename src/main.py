"""メインのシミュレーション実行スクリプト"""

import argparse
import os
from pathlib import Path

import jsbsim
import pandas as pd
from joblib import Parallel, delayed
from tqdm import tqdm

from trajecsim.jsbsim_support.generate_param_xml import generate_param_xml
from trajecsim.jsbsim_support.jsb_runner import run_jsb
from trajecsim.jsbsim_support.param_generator.yaml_loader import load_yaml_parameters
from trajecsim.util.kml_generator import KMLGenerator
from trajecsim.util.logger import setup_logging, tqdm_joblib
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
    parser.add_argument(
        "--template_dir",
        type=str,
        default="src/trajecsim/jsbsim_support/param-xml-template",
        help="Template directory",
    )
    return parser.parse_args()


def main(config_file_path: str, output_dir: str, template_dir: str) -> None:
    """メイン関数"""
    _ = jsbsim.FGFDMExec(None)

    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    logger = setup_logging(output_dir / "log.txt")
    logger.info(f"シミュレーションを開始します: {config_file_path}")

    logger.info(f"パラメータを {config_file_path} から読み込みます")

    try:
        params = load_yaml_parameters(config_file_path)
    except FileNotFoundError:
        logger.exception(f"パラメータファイルが見つかりません: {config_file_path}")
        raise

    all_params_keys = list(params.launch.keys()) + list(params.simulation.keys()) + list(params.rocket.keys())
    kml_group_by = params.misc.kml_group_by
    if not all(group_key in all_params_keys for group_key in kml_group_by):
        invalid_keys = [key for key in kml_group_by if key not in all_params_keys]
        logger.exception(f"KMLファイルを生成するためのキーが不正です: {invalid_keys}")
        raise ValueError(invalid_keys)

    simulation_df = generate_param_xml(params, template_dir)

    logger.info("シミュレーションを実行します")
    with tqdm_joblib(tqdm(desc="シミュレーションを実行中🚀", total=len(simulation_df))):
        results = Parallel(n_jobs=os.cpu_count())(
            delayed(run_jsb)(row, output_dir / "raw_result") for _, row in simulation_df.iterrows()
        )

    results_df = pd.DataFrame(results, index=simulation_df.index)
    simulation_df = pd.concat([simulation_df, results_df], axis=1)

    logger.info("シミュレーションの結果を集計します")
    tqdm.pandas(desc="シミュレーションの結果を集計中")
    simulation_df = pd.concat(
        [simulation_df, simulation_df.progress_apply(summarize_output_info_df, axis=1, output_dir=output_dir)],
        axis=1,
    )

    logger.info("シミュレーションの結果を保存します")
    simulation_df[simulation_df.columns[-6:]].to_csv(output_dir / "summary.csv", index=False)
    simulation_df.select_dtypes(include=["number"]).to_csv(output_dir / "simulation_params.csv", index=False)

    logger.info("KMLファイルを生成します")
    for group_key in kml_group_by:
        kml_generator = KMLGenerator()
        group_keys = [col for col in simulation_df.columns if group_key in col]
        grouped_by_group_key = simulation_df.groupby(group_keys)
        kml_generator.generate_grouped_points_polygons(grouped_by_group_key)

        simulation_df.apply(
            lambda x, kg=kml_generator: kg.add_point(
                (x["landed_longitude"], x["landed_latitude"]),
                x.name,
            ),
            axis=1,
        )
        kml_generator.save(output_dir / f"result_{group_key}.kml")


if __name__ == "__main__":
    # コマンドライン引数を取得
    args = get_arguments()
    # 引数を取得
    config_file_path = args.config_file_path
    output_dir = args.output_dir
    template_dir = args.template_dir
    main(config_file_path, output_dir, template_dir)
