import pytest

from regatta.models.wind import (
    Heading,
    PointOfSail,
    WindDirection,
    get_point_of_sail,
)


@pytest.mark.parametrize(
    "input_a,input_b,expected",
    [
        (WindDirection.NORTH, Heading.NORTH, PointOfSail.LUFFING),  # 0° - into wind
        (WindDirection.NORTH, Heading.NORTH_EAST, PointOfSail.BEATING),  # 45°
        (WindDirection.NORTH, Heading.EAST, PointOfSail.BEAM_REACHING),  # 90°
        (
            WindDirection.NORTH,
            Heading.SOUTH_EAST,
            PointOfSail.BROAD_REACHING,
        ),  # 135°
        (
            WindDirection.NORTH,
            Heading.SOUTH,
            PointOfSail.RUNNING,
        ),  # 180° - wind at back
        (
            WindDirection.NORTH,
            Heading.NORTH_WEST,
            PointOfSail.BEATING,
        ),  # 315° → 45° (wraparound)
        (WindDirection.EAST, Heading.WEST, PointOfSail.RUNNING),  # 180°
        (WindDirection.SOUTH_WEST, Heading.NORTH_EAST, PointOfSail.RUNNING),  # 180°
    ],
)
def test_get_point_of_sail(input_a, input_b, expected):
    assert get_point_of_sail(input_a, input_b) == expected


@pytest.mark.parametrize(
    "input_a,expected",
    [
        (PointOfSail.LUFFING, 0),
        (PointOfSail.BEATING, 1),
        (PointOfSail.BEAM_REACHING, 2),
        (PointOfSail.RUNNING, 2),
        (PointOfSail.BROAD_REACHING, 3),
    ],
)
def test_point_of_sail_speed(input_a, expected):
    assert input_a.speed == expected
