import math

from geopy.distance import geodesic

from trajecsim.landing_range.landing_range import LandingRange

CENTER_LATITUDE = 40.2468027777777778
CENTER_LONGITUDE = 139.987536111111111
CIRCLE_RADIUS = 2000

LINE_POINT_1_LATITUDE = 40.225331
LINE_POINT_1_LONGITUDE = 140.000024
LINE_POINT_2_LATITUDE = 40.273697
LINE_POINT_2_LONGITUDE = 140.012675

EARTH_RADIUS = 6371000 * 2


class NoshiroSea(LandingRange):
    """Class for calculating the landing range of Noshiro Airport"""

    def __init__(self, config: dict = {}):
        super().__init__(config)

    def landing_range(self, latitude: float, longitude: float) -> float:
        distance_from_center = (
            CIRCLE_RADIUS - geodesic((latitude, longitude), (CENTER_LATITUDE, CENTER_LONGITUDE)).meters
        )
        distance_from_line = (
            (
                (LINE_POINT_2_LATITUDE - LINE_POINT_1_LATITUDE) * longitude
                - (LINE_POINT_2_LONGITUDE - LINE_POINT_1_LONGITUDE) * latitude
                + (LINE_POINT_2_LONGITUDE * LINE_POINT_1_LATITUDE - LINE_POINT_1_LONGITUDE * LINE_POINT_2_LATITUDE)
            )
            / math.sqrt(
                (LINE_POINT_2_LATITUDE - LINE_POINT_1_LATITUDE) ** 2
                + (LINE_POINT_2_LONGITUDE - LINE_POINT_1_LONGITUDE) ** 2
            )
            * EARTH_RADIUS
            * math.pi
            / 180
        )
        point_side = (LINE_POINT_2_LONGITUDE - LINE_POINT_1_LONGITUDE) * (latitude - LINE_POINT_1_LATITUDE) - (
            LINE_POINT_2_LATITUDE - LINE_POINT_1_LATITUDE
        ) * (longitude - LINE_POINT_1_LONGITUDE)
        distance_from_line = distance_from_line if point_side > 0 else -distance_from_line
        return min(distance_from_center, distance_from_line)
