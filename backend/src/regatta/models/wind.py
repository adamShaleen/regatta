from enum import Enum
from typing import Literal


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


def get_tack(
    wind: WindDirection, heading: Heading
) -> Literal["starboard", "port"] | None:
    diff = (wind.value - heading.value) % 360

    if diff == 0 or diff == 180:
        return None
    return "starboard" if diff < 180 else "port"


def detect_maneuver(
    wind: WindDirection, old_heading: Heading, new_heading: Heading
) -> Literal["tack", "jibe"] | None:
    if old_heading == new_heading:
        return None

    old_tack = get_tack(wind, old_heading)
    new_tack = get_tack(wind, new_heading)

    if old_tack is None or new_tack is None or old_tack == new_tack:
        return None

    # Headings are on different tacks — determine whether the bow (tack) or
    # stern (jibe) crossed through the wind axis.
    clockwise_distance = (new_heading.value - old_heading.value) % 360
    clockwise_to_upwind = (wind.value - old_heading.value) % 360

    if clockwise_distance <= 180:
        # Shorter arc is clockwise from old to new
        return "tack" if clockwise_to_upwind <= clockwise_distance else "jibe"
    else:
        # Shorter arc is counterclockwise from old to new
        counter_clockwise_distance = 360 - clockwise_distance
        counter_clockwise_to_upwind = (old_heading.value - wind.value) % 360
        return (
            "tack"
            if counter_clockwise_to_upwind <= counter_clockwise_distance
            else "jibe"
        )
