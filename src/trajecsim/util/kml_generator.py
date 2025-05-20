import numpy as np
import simplekml


class KMLGenerator:
    def __init__(self):
        self.kml = simplekml.Kml()

    def save(self, path: str) -> None:
        self.kml.save(path)

    @staticmethod
    def create_color_gradient(start_color, end_color, n):
        start = np.array(start_color)
        end = np.array(end_color)

        # 0から1までのn個の等間隔の値を作成
        t = np.linspace(0, 1, n)

        # 線形補間でグラデーションを作成
        gradient = [tuple(map(int, (1 - t_i) * start + t_i * end)) for t_i in t]

        return gradient

    def add_point(self, point: tuple[float, float], name: str, rgb: tuple[int, int, int] = (255, 0, 0)) -> None:
        pnt = self.kml.newpoint(name=name)
        pnt.coords = [(point[0], point[1])]
        pnt.style.iconstyle.icon.href = None

    def add_line(
        self,
        points: list[any],
        name: str,
        rgb: tuple[int, int, int] = (255, 0, 0),
        width: int = 3,
    ) -> None:
        ls = self.kml.newlinestring(name=name)
        ls.coords = [*points]
        ls.style.linestyle.color = simplekml.Color.rgb(rgb[0], rgb[1], rgb[2])
        ls.style.linestyle.width = width
        ls.altitudemode = (
            simplekml.AltitudeMode.relativetoground if len(points[0]) == 3 else simplekml.AltitudeMode.clamptoground
        )

    def generate_groundpoint_polygon(
        self, points: list[tuple[float, float]], name: str, rgb: tuple[int, int, int] = (255, 0, 0), width: int = 3
    ) -> None:
        ls = self.kml.newpolygon(name=name)
        ls.outerboundaryis = [*points, points[0]]
        ls.altitudemode = simplekml.AltitudeMode.clamptoground
        ls.style.linestyle.color = simplekml.Color.rgb(rgb[0], rgb[1], rgb[2])
        ls.style.linestyle.width = width
        ls.style.polystyle.fill = 0
        ls.style.polystyle.outline = 1

    def generate_grouped_points_polygons(self, grouped_df) -> None:
        """風速ごとの着地点ポリゴンを生成する

        Args:
            grouped_df: 風速でグループ化されたDataFrame
            output_path: 出力先のパス
        """
        num_groups = len(grouped_df)
        color_gradient = (
            self.create_color_gradient((248, 112, 128), (247, 93, 139), num_groups) if num_groups > 0 else []
        )

        for i, (wind_speed, group_df) in enumerate(grouped_df):
            if wind_speed == 0.0:
                continue

            # KML expects (longitude, latitude)
            points = [
                (lon, lat) for lon, lat in zip(group_df["landed_longitude"], group_df["landed_latitude"], strict=False)
            ]

            current_color = color_gradient[i] if color_gradient else (255, 0, 0)

            self.generate_groundpoint_polygon(
                points,
                f"wind_speed: {wind_speed}",
                rgb=current_color,
            )
