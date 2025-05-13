from pydantic import BaseModel


class LiftoffConfig(BaseModel):
    yaw: float = 0.0
    pitch: float = 90.0
    roll: float = 0.0
    latitude: float = 35.0
    longitude: float = 139.0
    elevation: float = 0.0
    winddir: float = 0.0
    vwind: float = 0.0
