from enum import Enum


class WindDirection(Enum):
    NORTH = 0
    NORTH_EAST = 45
    EAST = 90
    SOUTH_EAST = 135
    SOUTH = 180
    SOUTH_WEST = 225
    WEST = 270
    NORTH_WEST = 315


BoatHeading = WindDirection


class PointOfSail(Enum):
    LUFFING = 0
    BEATING = 1
    BEAM_REACHING = 2
    RUNNING = 3
    BROAD_REACHING = 4

    @property
    def speed(self) -> int:
        speeds = {
            PointOfSail.LUFFING: 0,
            PointOfSail.BEATING: 1,
            PointOfSail.BEAM_REACHING: 2,
            PointOfSail.RUNNING: 2,
            PointOfSail.BROAD_REACHING: 3,
        }
        return speeds[self]


def get_point_of_sail(wind: WindDirection, boat_heading: BoatHeading) -> PointOfSail:
    diff: int = abs(wind.value - boat_heading.value)
    angle: int = min(diff, 360 - diff)

    angle_to_point_of_sail = {
        0: PointOfSail.LUFFING,
        45: PointOfSail.BEATING,
        90: PointOfSail.BEAM_REACHING,
        135: PointOfSail.BROAD_REACHING,
        180: PointOfSail.RUNNING,
    }

    return angle_to_point_of_sail[angle]
