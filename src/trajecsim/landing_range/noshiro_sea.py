from geopy.distance import geodesic

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

    def _point_in_polygon(self, latitude: float, longitude: float) -> bool:
        """Check if a point is inside the polygon using ray casting algorithm."""
        point = (latitude, longitude)
        n = len(POLYGON_COORDINATES)
        inside = False

        p1_lat, p1_lon = POLYGON_COORDINATES[0]
        for i in range(1, n + 1):
            p2_lat, p2_lon = POLYGON_COORDINATES[i % n]
            if point[1] > min(p1_lon, p2_lon):
                if point[1] <= max(p1_lon, p2_lon):
                    if point[0] <= max(p1_lat, p2_lat):
                        if p1_lon != p2_lon:
                            xinters = (point[1] - p1_lon) * (p2_lat - p1_lat) / (p2_lon - p1_lon) + p1_lat
                        if p1_lat == p2_lat or point[0] <= xinters:
                            inside = not inside
            p1_lat, p1_lon = p2_lat, p2_lon

        return inside

    def _distance_to_polygon_boundary(self, latitude: float, longitude: float) -> float:
        """Calculate the minimum distance from a point to the polygon boundary using geopy."""
        point = (latitude, longitude)
        min_distance = float("inf")

        for i in range(len(POLYGON_COORDINATES)):
            p1 = POLYGON_COORDINATES[i]
            p2 = POLYGON_COORDINATES[(i + 1) % len(POLYGON_COORDINATES)]

            # Calculate distance to line segment
            distance = self._distance_to_line_segment(point, p1, p2)
            min_distance = min(min_distance, distance)

        return min_distance

    def _distance_to_line_segment(
        self, point: tuple[float, float], line_start: tuple[float, float], line_end: tuple[float, float]
    ) -> float:
        """Calculate the distance from a point to a line segment using geopy."""
        # Calculate distances to endpoints
        dist_to_start = geodesic(point, line_start).meters
        dist_to_end = geodesic(point, line_end).meters

        # Calculate the projection of the point onto the line
        line_length = geodesic(line_start, line_end).meters
        if line_length == 0:
            return dist_to_start

        # Use dot product to find the projection point
        lat_diff = line_end[0] - line_start[0]
        lon_diff = line_end[1] - line_start[1]
        point_lat_diff = point[0] - line_start[0]
        point_lon_diff = point[1] - line_start[1]

        # Calculate the parameter t for the projection
        t = (point_lat_diff * lat_diff + point_lon_diff * lon_diff) / (lat_diff * lat_diff + lon_diff * lon_diff)

        if t < 0:
            return dist_to_start
        if t > 1:
            return dist_to_end

        # Calculate the projection point
        proj_lat = line_start[0] + t * lat_diff
        proj_lon = line_start[1] + t * lon_diff
        projection_point = (proj_lat, proj_lon)

        return geodesic(point, projection_point).meters

    def landing_range(self, latitude: float, longitude: float) -> float:
        """Calculate landing range value (positive inside polygon, negative outside)."""
        is_inside = self._point_in_polygon(latitude, longitude)
        distance_to_boundary = self._distance_to_polygon_boundary(latitude, longitude)

        return distance_to_boundary if is_inside else -distance_to_boundary
