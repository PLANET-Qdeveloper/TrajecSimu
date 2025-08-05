from geopy.distance import geodesic
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points

from trajecsim.landing_range.landing_range import LandingRange

POLYGON_COORDINATES = [
    (40.26149300294178, 140.0094791592612),
    (40.2642602688727, 139.9932398872506),
    (40.26460197870949, 139.9909318144494),
    (40.26479085228271, 139.987341377515),
    (40.26433616899444, 139.9822728225093),
    (40.26299626432305, 139.9772825248559),
    (40.26199299246836, 139.9749085824227),
    (40.26086444600114, 139.9728365038179),
    (40.25942370332147, 139.9707401748826),
    (40.25768975453263, 139.9687716646912),
    (40.25623515050533, 139.9674723780254),
    (40.2542151641483, 139.9660514425467),
    (40.25321298436799, 139.9655135448727),
    (40.25217003129539, 139.9650383050235),
    (40.25108666779969, 139.9646461338833),
    (40.24955206871581, 139.9642513745098),
    (40.24773454477712, 139.9640056563258),
    (40.24539983694682, 139.9640511121102),
    (40.24374397618987, 139.9643229542895),
    (40.2425575973181, 139.9646499711443),
    (40.24051201896022, 139.9654720128462),
    (40.2397071808194, 139.9658925750851),
    (40.23887443488726, 139.9663943856586),
    (40.23809058315737, 139.9669364758578),
    (40.23665050758729, 139.9680927149552),
    (40.23501881430268, 139.9697393127221),
    (40.23327859167702, 139.9720099153484),
    (40.2318726711675, 139.9743989893189),
    (40.23049586884894, 139.9776040232665),
    (40.22954585557037, 139.9808509371636),
    (40.22916933193805, 139.9828861110256),
    (40.22887535311624, 139.9845918728399),
    (40.22617410359279, 140.0002466848887),
]


class NoshiroSea(LandingRange):
    """Class for calculating the landing range of Noshiro Sea using polygon boundary"""

    def __init__(self, config: dict | None = None) -> None:
        """Initialize the NoshiroSea landing range calculator."""
        if config is None:
            config = {}
        super().__init__(config)
        # ShapelyのPolygonは (経度, 緯度) の順で座標を保持
        self.polygon = Polygon([(lon, lat) for lat, lon in POLYGON_COORDINATES])
        # 内部の点から境界までの距離を計算するために、あらかじめ境界線オブジェクトを取得
        self.boundary = self.polygon.boundary

    def landing_range(self, latitude: float, longitude: float) -> float:
        """
        ポリゴンの境界までの距離を計算します。
        点がポリゴンの内側にあれば正の値、外側にあれば負の値を返します。
        """
        point = Point(longitude, latitude)

        is_inside = self.polygon.contains(point)

        if is_inside:
            # 点が内側にある場合、境界線 (boundary) への距離を計算
            target_geometry = self.boundary
        else:
            # 点が外側にある場合、ポリゴン (polygon) への距離を計算
            # (これは実質的に境界線への距離と同じ)
            target_geometry = self.polygon

        # 対象ジオメトリ上の最近傍点を取得
        # nearest_pointsは (ジオメトリ上の最近傍点, 元の点) のタプルを返す
        nearest_p_on_geom = nearest_points(target_geometry, point)[0]

        # 測地線距離をメートル単位で計算
        distance = geodesic(
            (latitude, longitude),  # 元の点の座標 (緯度, 経度)
            (nearest_p_on_geom.y, nearest_p_on_geom.x),  # 最近傍点の座標 (緯度, 経度)
        ).meters

        # 内側なら正の距離、外側なら負の距離を返す
        return distance if is_inside else -distance
