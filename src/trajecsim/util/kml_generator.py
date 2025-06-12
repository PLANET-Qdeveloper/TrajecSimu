"""KMLファイルを生成する."""

import logging
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import simplekml
from fastkml import kml

DEFAULT_LINE_WIDTH = 3
LOGGER = logging.getLogger(__name__)


def merge_kmz_to_kml(existing_kml_path: Path, kmz_path: Path, output_path: Path) -> None:
    # 既存のKMLファイルを読み込み
    with open(existing_kml_path, "r", encoding="utf-8") as f:
        existing_kml = kml.KML()
        existing_kml.from_string(f.read())

    # KMZファイルを読み込み
    with zipfile.ZipFile(kmz_path, "r") as kmz, kmz.open("doc.kml") as kml_file:
        loaded_string = kml_file.read().decode("utf-8")
        loaded_string = loaded_string.replace('xmlns:kml="http://www.opengis.net/kml/2.2"', "")
        kmz_kml = kml.KML()
        kmz_kml.from_string(loaded_string)

    # 新しいKMLオブジェクトを作成
    merged_kml = kml.KML()

    # 既存のKMLの要素を追加
    for feature in existing_kml.features:
        merged_kml.append(feature)

    # KMZの要素を追加
    for feature in kmz_kml.features:
        merged_kml.append(feature)

    # マージされたKMLを保存
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(merged_kml.to_string(prettyprint=True))


class KMLGenerator:
    """KMLファイルを生成する."""

    def __init__(self) -> None:
        """初期化"""
        self.kml = simplekml.Kml()

    def save(self, path: str) -> None:
        """KMLファイルを保存する."""
        self.kml.save(path)

    @staticmethod
    def create_color_gradient(
        start_color: tuple[int, int, int],
        end_color: tuple[int, int, int],
        n: int,
    ) -> list[tuple[int, int, int]]:
        """グラデーションを作成する."""
        start = np.array(start_color)
        end = np.array(end_color)

        # 0から1までのn個の等間隔の値を作成
        t = np.linspace(0, 1, n)

        # 線形補間でグラデーションを作成
        return [tuple(map(int, (1 - t_i) * start + t_i * end)) for t_i in t]

    def add_point(self, point: tuple[float, float], name: str) -> None:
        """点を追加する.

        Args:
            point: 点の座標
            name: 点の名前
            rgb: 点の色
        """
        pnt = self.kml.newpoint(name=name)
        pnt.coords = [(point[0], point[1])]
        pnt.style.iconstyle.icon.href = None
        pnt.style.iconstyle.scale = 0.0

    def add_line(
        self,
        points: list[any],
        name: str,
        rgb: tuple[int, int, int] = (255, 0, 0),
        width: int = 3,
    ) -> None:
        """線を追加する.

        Args:
            points: 点の座標
            name: 線の名前
            rgb: 線の色
            width: 線の幅
        """
        ls = self.kml.newlinestring(name=name)
        ls.coords = [*points]
        ls.style.linestyle.color = simplekml.Color.rgb(rgb[0], rgb[1], rgb[2])
        ls.style.linestyle.width = width
        ls.altitudemode = (
            simplekml.AltitudeMode.relativetoground if len(points[0]) == 3 else simplekml.AltitudeMode.clamptoground
        )

    def generate_groundpoint_polygon(
        self,
        points: list[tuple[float, float]],
        name: str,
        rgb: tuple[int, int, int] = (255, 0, 0),
        width: int = DEFAULT_LINE_WIDTH,
    ) -> None:
        """地面の点のポリゴンを生成する.

        Args:
            points: 点の座標
            name: ポリゴンの名前
            rgb: ポリゴンの色
            width: ポリゴンの幅
        """
        ls = self.kml.newpolygon(name=name)
        ls.outerboundaryis = [*points, points[0]]
        ls.altitudemode = simplekml.AltitudeMode.clamptoground
        ls.style.linestyle.color = simplekml.Color.rgb(rgb[0], rgb[1], rgb[2])
        ls.style.linestyle.width = width
        ls.style.polystyle.fill = 0
        ls.style.polystyle.outline = 1

    def generate_grouped_points_polygons(self, grouped_df: pd.DataFrame) -> None:
        """グループごとの着地点ポリゴンを生成する

        Args:
            grouped_df: グループ化されたDataFrame
        """
        num_groups = len(grouped_df)
        color_gradient = (
            self.create_color_gradient((248, 112, 128), (247, 93, 139), num_groups) if num_groups > 0 else []
        )

        for i, (group_key, group_df) in enumerate(grouped_df):
            # KML expects (longitude, latitude)
            points = [
                (lon, lat) for lon, lat in zip(group_df["landed_longitude"], group_df["landed_latitude"], strict=False)
            ]

            if len(set(points)) <= 3:
                continue

            current_color = color_gradient[i] if color_gradient else (255, 0, 0)

            self.generate_groundpoint_polygon(
                points,
                f"{group_key}",
                rgb=current_color,
            )
            kmz_path = Path(group_df[("launch", "range_kmz")])
            if not kmz_path.exists():
                LOGGER.warning(f"KMLファイルが見つかりません: {kmz_path}")
                continue
