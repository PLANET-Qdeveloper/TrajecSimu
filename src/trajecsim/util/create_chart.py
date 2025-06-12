from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# seaborn のインポートを追加（オプション）
try:
    import seaborn as sns

    sns.set_style("whitegrid")  # seabornのスタイルを直接設定
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False


def create_time_series_plots(
    output_info_df: pd.Series,
):
    """
    Create time series plots for all columns in the CSV file.

    Args:
        csv_path (str): Path to the input CSV file
        output_dir (str): Directory to save the plots
    """

    output_file = output_info_df["raw_output_file"]
    # Read the CSV file
    output_dir = Path(Path(output_file).parent)
    df = pd.read_csv(output_file)

    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Set style - 修正版
    if not SEABORN_AVAILABLE:
        # seabornが利用できない場合は、matplotlib の built-in スタイルを使用
        plt.style.use("default")  # または "ggplot", "bmh", "classic" など
        # グリッドスタイルを手動で設定
        plt.rcParams["axes.grid"] = True
        plt.rcParams["grid.alpha"] = 0.3
        plt.rcParams["axes.axisbelow"] = True

    # Create plots for each column except 'Time'
    for column in df.columns:
        if column == "Time":
            continue

        plt.figure(figsize=(12, 6))
        plt.plot(df["Time"], df[column], linewidth=1)

        # Customize plot
        plt.title(f"{column} vs Time")
        plt.xlabel("Time")
        plt.ylabel(column)
        plt.grid(True, alpha=0.3)

        # Save plot
        plt.savefig(output_path / f"{column}_vs_time.png", dpi=300, bbox_inches="tight")
        plt.close()


if __name__ == "__main__":
    # Example usage
    csv_path = "data/result/raw_result/rocket_terminal_velocity=0.0__.csv"
    output_dir = "data/result/plots"
    create_time_series_plots(csv_path, output_dir)
