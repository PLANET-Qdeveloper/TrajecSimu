"""シミュレーションの結果をまとめる."""

import math
from pathlib import Path

import geopy.distance
import numpy as np
import pandas as pd
from geopy import Point

from trajecsim.util.kml_generator import KMLGenerator

VGUST = 9.0


def calculate_with_geopy(lat1, lon1, lat2, lon2):
    """
    geopyライブラリを使用した計算

    Args:
        lat1, lon1: 地点1の緯度、経度
        lat2, lon2: 地点2の緯度、経度

    Returns:
        dict: 計算結果
    """
    # 2点を定義
    point1 = Point(lat1, lon1)
    point2 = Point(lat2, lon2)

    # 距離を計算（geodesic距離 - より正確）
    distance = geopy.distance.geodesic(point1, point2).meters

    # 緯度方向の距離（経度を固定）
    lat_distance = geopy.distance.geodesic((lat1, lon1), (lat2, lon1)).meters
    if lat2 < lat1:
        lat_distance = -lat_distance

    # 経度方向の距離（緯度を固定）
    lon_distance = geopy.distance.geodesic((lat1, lon1), (lat1, lon2)).meters
    if lon2 < lon1:
        lon_distance = -lon_distance

    return {
        "distance_m": distance,
        "lat_diff_m": lat_distance,
        "lon_diff_m": lon_distance,
        "lat_diff_degrees": lat2 - lat1,
        "lon_diff_degrees": lon2 - lon1,
    }


def calculate_aoa(row: pd.Series) -> None:
    """AoAを計算する."""
    output_file = row["raw_output_file"]
    output_df = pd.read_csv(output_file)

    alpha = np.radians(output_df["Angle of Attack"])
    beta = np.radians(output_df["Angle of Sideslip"])
    vtrue = output_df["True Velocity"]
    vgust = VGUST

    calculated_df = pd.DataFrame(
        {
            "Angle of Attack(total)": np.degrees(np.arccos(np.cos(alpha) * np.cos(beta))),
            "Angle of Attack(gust)": np.degrees(
                np.arccos(
                    np.cos(beta)
                    * (vtrue * np.cos(alpha) - vgust * np.sin(beta))
                    / np.sqrt(vtrue * vtrue + vgust * vgust * np.cos(beta) * np.cos(beta))
                )
            ),
        }
    )

    # Concatenate the dataframes first
    combined_df = pd.concat([output_df, calculated_df], axis=1)
    # Save to the original output file
    combined_df.to_csv(output_file, index=False)


def get_extrema_analysis(output_info_df: pd.Series) -> pd.DataFrame:
    """シミュレーション結果の極値分析を行う."""
    output_file = output_info_df["raw_output_file"]
    output_df = pd.read_csv(output_file)

    # 列名を短縮名にマッピング
    cols = {
        "Time": "time",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Altitude": "altitude",
        "Angle of Attack(gust)": "angle_of_attack_gust",
        "Angle of Attack(total)": "angle_of_attack_total",
        "Acceleration": "acceleration",
        "Thrust": "thrust",
        "True Velocity": "true_velocity",
        "Ground Velocity": "ground_velocity",
        "Pitch": "pitch_deg",
        "Roll": "roll_deg",
        "Yaw": "yaw_deg",
        "Dynamic Pressure": "dynamic_pressure",
    }

    # データフレームの列名を変更
    df = output_df.rename(columns=cols)

    # 風速を計算（対気速度から対地速度を引いた差の大きさ）
    df["wind_speed"] = abs(df["true_velocity"] - df["ground_velocity"])

    # 気温の計算（標準大気モデル）
    def calculate_temperature(altitude):
        # 標準大気モデル（海面レベル15°C、高度1000mごとに6.5°C下降）
        return 15.0 - 6.5 * (altitude / 1000.0)

    # 気圧の計算（標準大気モデル）
    def calculate_pressure(altitude):
        # 標準大気圧公式（海面レベル1013.25 hPa）
        return 1013.25 * ((288.15 - 0.0065 * altitude) / 288.15) ** 5.256

    df["temperature"] = df["altitude"].apply(calculate_temperature)
    df["pressure"] = df["altitude"].apply(calculate_pressure)

    # 動圧*atan(風速/速度)の計算
    df["qbar_atan_aoa"] = df["dynamic_pressure"] * np.degrees(df["angle_of_attack_gust"])

    # 4つの極値点を見つける
    extrema_points = {}

    # 0. 初期ちてん
    initial_point_idx = df["time"].idxmin()
    extrema_points["initial_point"] = {
        "index": initial_point_idx,
        "value": df.loc[initial_point_idx, "altitude"],
        "metric": "altitude",
    }

    initial_point_lat = df.loc[initial_point_idx, "latitude"]
    initial_point_long = df.loc[initial_point_idx, "longitude"]

    # 1. 最高速度の点
    max_speed_idx = df["true_velocity"].idxmax()
    extrema_points["max_speed"] = {
        "index": max_speed_idx,
        "value": df.loc[max_speed_idx, "true_velocity"],
        "metric": "true_velocity",
    }

    # 2. 最大動圧の点
    max_qbar_idx = df["dynamic_pressure"].idxmax()
    extrema_points["max_dynamic_pressure"] = {
        "index": max_qbar_idx,
        "value": df.loc[max_qbar_idx, "dynamic_pressure"],
        "metric": "dynamic_pressure",
    }

    # 3. 最大加速度の点
    max_accel_idx = df["acceleration"].idxmax()
    extrema_points["max_acceleration"] = {
        "index": max_accel_idx,
        "value": df.loc[max_accel_idx, "acceleration"],
        "metric": "acceleration",
    }

    # 4. 動圧*AoAが最大の点
    max_qbar_atan_idx = df["qbar_atan_aoa"].idxmax()
    extrema_points["max_qbar_atan_aoa"] = {
        "index": max_qbar_atan_idx,
        "value": df.loc[max_qbar_atan_idx, "qbar_atan_aoa"],
        "metric": "qbar_atan_aoa",
    }

    # 5. 最大高度の点
    max_altitude_idx = df["altitude"].idxmax()
    extrema_points["max_altitude"] = {
        "index": max_altitude_idx,
        "value": df.loc[max_altitude_idx, "altitude"],
        "metric": "altitude",
    }

    # 6. 最終ちてん
    final_point_idx = df["time"].idxmax()
    extrema_points["final_point"] = {
        "index": final_point_idx,
        "value": df.loc[final_point_idx, "altitude"],
        "metric": "altitude",
    }

    # 7. パラシュート展開の点
    parachute_deploy_idx = df["parachute_deploy_gain"].idxmax()
    extrema_points["parachute_deploy"] = {
        "index": parachute_deploy_idx,
        "value": df.loc[parachute_deploy_idx, "parachute_deploy_gain"],
        "metric": "parachute_deploy_gain",
    }

    # 各極値点での詳細データを収集
    result_data = []

    for extrema_name, extrema_info in extrema_points.items():
        idx = extrema_info["index"]
        pos_diff = calculate_with_geopy(
            initial_point_lat, initial_point_long, df.loc[idx, "latitude"], df.loc[idx, "longitude"]
        )

        range_m = pos_diff["distance_m"]
        lat_m = pos_diff["lat_diff_m"]
        long_m = pos_diff["lon_diff_m"]

        row_data = {
            "extrema_type": extrema_name,
            "extrema_value": extrema_info["value"],
            "time": df.loc[idx, "time"],
            "thrust": df.loc[idx, "thrust"],
            "acceleration": df.loc[idx, "acceleration"],
            "dynamic_pressure": df.loc[idx, "dynamic_pressure"],
            "angle_of_attack_gust": df.loc[idx, "angle_of_attack_gust"],
            "angle_of_attack_total": df.loc[idx, "angle_of_attack_total"],
            "true_velocity": df.loc[idx, "true_velocity"],
            "altitude": df.loc[idx, "altitude"],
            "temperature": df.loc[idx, "temperature"],
            "pressure": df.loc[idx, "pressure"],
            "latitude": df.loc[idx, "latitude"],
            "longitude": df.loc[idx, "longitude"],
            "lat_m": lat_m,
            "long_m": long_m,
            "range_m": range_m,
        }
        result_data.append(row_data)

    return pd.DataFrame(result_data)


def summarize_output_info_df(output_info_df: pd.Series, output_dir: Path) -> pd.Series:
    """シミュレーションの結果をまとめる."""
    output_file = output_info_df["raw_output_file"]
    output_df = pd.read_csv(output_file)

    altitude_col = "Altitude"
    speed_col = "True Velocity"
    pressure_col = "Dynamic Pressure"
    lat_col = "Latitude"
    long_col = "Longitude"

    launch_clear_height = output_info_df[("launch", "elevation")] + output_info_df[
        ("launch", "launcher_length")
    ] * math.sin(
        output_info_df[("launch", "pitch")] * math.pi / 180,
    )

    launch_clear_speed = output_df[output_df[altitude_col] > launch_clear_height].iloc[0][speed_col]
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
        "launch_clear_speed": launch_clear_speed,
    }
    return pd.Series(summary_row)
