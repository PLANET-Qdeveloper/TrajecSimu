"""メインのシミュレーション実行スクリプト"""

import argparse
import os
import shutil
import stat
import time
from pathlib import Path

import pandas as pd
from joblib import Parallel, delayed
from tqdm import tqdm

from trajecsim.jsbsim_support.generate_param_xml import generate_param_xml
from trajecsim.jsbsim_support.jsb_runner import run_jsb
from trajecsim.jsbsim_support.param_generator.yaml_loader import load_yaml_parameters
from trajecsim.util.create_chart import create_time_series_plots
from trajecsim.util.kml_generator import KMLGenerator
from trajecsim.util.logger import setup_logging, tqdm_joblib
from trajecsim.util.summarize import (
    calculate_acceleration,
    calculate_aoa,
    delete_final_point,
    generate_final_points_dataframe,
    get_extrema_analysis,
    summarize_output_info_df,
)


def get_arguments() -> argparse.Namespace:
    """コマンドライン引数をパース

    Returns:
        args: 取得した引数
    """
    parser = argparse.ArgumentParser(description="Trajectory Simulation")
    parser.add_argument(
        "--config_file_path",
        type=str,
        default="data/input/landed_area.yaml",
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
    parser.add_argument(
        "--chart_output",
        type=bool,
        default=False,
        help="Output charts",
    )
    parser.add_argument(
        "--point_output",
        type=bool,
        default=False,
        help="Output points",
    )
    return parser.parse_args()


def clear_directory_safe(directory: Path, logger) -> None:
    """安全にディレクトリをクリアする（Windows対応、権限エラー対応）

    Args:
        directory: クリアするディレクトリ
        logger: ロガー
    """
    if not directory.exists():
        return

    logger.info(f"出力ディレクトリをクリアします: {directory}")

    max_retries = 3
    retry_delay = 0.5

    for attempt in range(max_retries):
        try:

            def handle_remove_readonly(func, path, exc):
                """読み取り専用ファイルを削除できるようにする（Windows対応）"""
                if os.path.exists(path):
                    os.chmod(path, stat.S_IWRITE)
                    func(path)

            for item in directory.iterdir():
                if item.is_file():
                    # ファイルの場合、読み取り専用属性を解除してから削除
                    try:
                        item.chmod(stat.S_IWRITE)
                        item.unlink()
                    except PermissionError:
                        # Windowsで使用中のファイルの場合、少し待ってから再試行
                        time.sleep(retry_delay)
                        item.chmod(stat.S_IWRITE)
                        item.unlink()
                elif item.is_dir():
                    # ディレクトリの場合、再帰的に削除
                    shutil.rmtree(item, onerror=handle_remove_readonly)

            logger.info("出力ディレクトリのクリアが完了しました")
            break

        except (PermissionError, OSError) as e:
            logger.warning(f"ディレクトリクリア試行 {attempt + 1}/{max_retries} 失敗: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # 指数バックオフ
            else:
                logger.error(f"ディレクトリクリアに失敗しました。手動でクリアしてください: {directory}")
                raise


def main(
    config_file_path: str | Path,
    output_dir: str | Path,
    template_dir: str | Path,
    chart_output: bool,
    point_output: bool,
) -> None:
    """メイン関数"""
    output_dir = Path(output_dir)

    # 出力ディレクトリを作成（存在しない場合）
    output_dir.mkdir(parents=True, exist_ok=True)

    logger = setup_logging(output_dir / "log.txt")
    logger.info(f"シミュレーションを開始します: {config_file_path}")

    # ディレクトリを再作成
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"パラメータを {config_file_path} から読み込みます")

    try:
        params = load_yaml_parameters(config_file_path)
    except FileNotFoundError:
        logger.exception(f"パラメータファイルが見つかりません: {config_file_path}")
        raise

    all_params_keys = list(params.launch.keys()) + list(params.simulation.keys()) + list(params.rocket.keys())
    kml_group_by = params.misc.kml_group_by
    result_each = params.misc.result_each
    landing_range_script = params.misc.landing_range_script

    if not all(group_key in all_params_keys for group_key in kml_group_by):
        invalid_keys = [key for key in kml_group_by if key not in all_params_keys]
        logger.exception(f"kml_group_byキーが不正です: {invalid_keys}")
        raise ValueError(invalid_keys)
    if not all(result_key in all_params_keys for result_key in result_each):
        invalid_keys = [key for key in result_each if key not in all_params_keys]
        logger.exception(f"result_eachキーが不正です: {invalid_keys}")
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

    for result_key in tqdm(result_each, desc="シミュレーションの結果を集計中"):
        result_keys = [col for col in simulation_df.columns if result_key in col]
        result_df = simulation_df.groupby(result_keys)
        for group_key, group_df in result_df:
            result_output_dir = output_dir / result_key / str(group_key)
            if not result_output_dir.exists():
                result_output_dir.mkdir(parents=True, exist_ok=True)
            tqdm.pandas(
                desc=f"AoAを計算中: {result_key} = {group_key}",
                total=len(group_df),
                leave=False,
            )
            group_df.progress_apply(
                delete_final_point,
                axis=1,
            )
            group_df.progress_apply(
                calculate_aoa,
                axis=1,
            )
            group_df.progress_apply(
                calculate_acceleration,
                axis=1,
            )
            tqdm.pandas(
                desc=f"シミュレーションの結果を集計中: {result_key} = {group_key}",
                total=len(group_df),
                leave=False,
            )
            group_df = pd.concat(
                [
                    group_df,
                    group_df.progress_apply(
                        summarize_output_info_df,
                        axis=1,
                        output_dir=result_output_dir,
                    ),
                ],
                axis=1,
            )

            extrema_results = group_df.progress_apply(
                get_extrema_analysis,
                axis=1,
                landing_range_script=landing_range_script,
            )

            extrema_df = pd.concat(
                [df for df in extrema_results if isinstance(df, pd.DataFrame) and not df.empty], ignore_index=True
            )

            if chart_output:
                group_df.progress_apply(
                    create_time_series_plots,
                    axis=1,
                )

            logger.info("シミュレーションの結果を保存します")
            # Export complete extrema_df with all columns
            extrema_df.to_csv(
                result_output_dir / "extrema.csv",
                index=False,
                float_format="%.6f",  # Use 6 decimal places for float values
                encoding="utf-8",  # Ensure proper encoding
            )

            logger.info("KMLファイルを生成します")
            for kml_group_key in kml_group_by:
                kml_generator = KMLGenerator()
                group_keys = [col for col in group_df.columns if kml_group_key in col]
                grouped_by_group_key = group_df.groupby(group_keys)

                kml_generator.generate_grouped_points_polygons(grouped_by_group_key, point_output)
                final_points_df = generate_final_points_dataframe(grouped_by_group_key)
                representation_df = grouped_by_group_key.first()
                kmz_path = representation_df[("launch", "range_kmz")].iloc[0]
                if not kmz_path.exists():
                    continue
                final_points_df.to_csv(result_output_dir / "final_points.csv", index=False)

                kml_output_path = result_output_dir / f"result_{kml_group_key}.kml"
                kml_generator.save(kml_output_path)


if __name__ == "__main__":
    # コマンドライン引数を取得
    args = get_arguments()
    # 引数を取得
    config_file_path = args.config_file_path
    output_dir = args.output_dir
    template_dir = args.template_dir
    chart_output = args.chart_output
    point_output = args.point_output
    main(config_file_path, output_dir, template_dir, chart_output, point_output)
