class LandingRange:
    """Class for calculating the landing range of an launch site"""

    def __init__(self, config: dict):
        self.config = config

    def landing_range(
        self,
        latitude: float,
        longitude: float,
    ) -> float:
        raise NotImplementedError
