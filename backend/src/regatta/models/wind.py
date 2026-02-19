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

    def opposite(self) -> "WindDirection":
        return WindDirection((self.value + 180) % 360)


Heading = WindDirection


class PointOfSail(Enum):
    LUFFING = 0
    BEATING = 1
    BEAM_REACHING = 2
    RUNNING = 3
    BROAD_REACHING = 4

    @property
    def speed(self) -> int:
        return _SPEEDS[self]


_SPEEDS = {
    PointOfSail.LUFFING: 0,
    PointOfSail.BEATING: 1,
    PointOfSail.BEAM_REACHING: 2,
    PointOfSail.RUNNING: 2,
    PointOfSail.BROAD_REACHING: 3,
}


_ANGLE_TO_POINT_OF_SAIL = {
    0: PointOfSail.LUFFING,
    45: PointOfSail.BEATING,
    90: PointOfSail.BEAM_REACHING,
    135: PointOfSail.BROAD_REACHING,
    180: PointOfSail.RUNNING,
}


def get_point_of_sail(wind: WindDirection, heading: Heading) -> PointOfSail:
    diff: int = abs(wind.value - heading.value)
    angle: int = min(diff, 360 - diff)

    return _ANGLE_TO_POINT_OF_SAIL[angle]
