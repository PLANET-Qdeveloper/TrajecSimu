"""メインのシミュレーション実行スクリプト"""

import argparse

from Scripts.interface import TrajecSimu_UI


def get_arguments() -> argparse.Namespace:
    """コマンドライン引数をパース

    Returns:
        args: 取得した引数
    """
    parser = argparse.ArgumentParser(description="Trajectory Simulation")
    parser.add_argument(
        "--config_file_path",
        type=str,
        default="data/Parameters_csv/24noshiro.csv",
        help="Path to the configuration file",
    )
    parser.add_argument(
        "--launch_site_name",
        type=str,
        default="noshiro",
        help="Name of the simulation instance",
    )
    args = parser.parse_args()
    return args


def main(config_file_path: str, launch_site_name: str) -> None:
    """メイン関数"""

    # create an instance
    mysim = TrajecSimu_UI(config_file_path, launch_site_name)
    # run the simulation
    mysim.run_loop(1, 1, 1)


if __name__ == "__main__":
    # コマンドライン引数を取得
    args = get_arguments()
    # 引数を取得
    config_file_path = args.config_file_path
    launch_site_name = args.launch_site_name
    main(config_file_path, launch_site_name)
