"""燃料テーブル生成を行うモジュール"""

import numpy as np


def generate_fuel_remaining_table(thrust_table: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Generate the fuel remaining table using the thrust table.

    Args:
        thrust_table (list[tuple[float, float]]): The thrust table.

    Returns:
        list[tuple[float, float]]: The fuel remaining table.
    """
    times = np.array([t for t, _ in thrust_table])
    values = np.array([v for _, v in thrust_table])
    total_impulse = np.sum(values)

    # 正規化された推力値を計算
    normalized_thrust_values = values / total_impulse

    # 累積インパルス率を計算
    cumulative_impulse_fraction = np.cumsum(normalized_thrust_values)

    # 出力テーブルの時間点を構築
    output_table_times_np = np.concatenate(([0.0], times))

    # 消費燃料率の中間値を構築
    consumed_fuel_fraction_intermediate_np = np.concatenate(([0.0], cumulative_impulse_fraction))

    # 残燃料率を計算
    remaining_fuel_fraction_np = 1.0 - consumed_fuel_fraction_intermediate_np

    # タプルのリストを作成
    return [(float(t), float(f)) for t, f in zip(output_table_times_np, remaining_fuel_fraction_np, strict=False)]
