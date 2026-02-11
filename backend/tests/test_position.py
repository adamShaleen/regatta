import pytest

from regatta.models.position import Position, calculate_next_position
from regatta.models.wind import Heading


@pytest.mark.parametrize(
    "input_a,input_b,expected",
    [
        (Position(0, 0), Heading.NORTH, Position(0, -1)),
        (Position(0, 0), Heading.NORTH_EAST, Position(1, -1)),
        (Position(0, 0), Heading.EAST, Position(1, 0)),
        (Position(0, 0), Heading.SOUTH_EAST, Position(1, 1)),
        (Position(0, 0), Heading.SOUTH, Position(0, 1)),
        (Position(0, 0), Heading.SOUTH_WEST, Position(-1, 1)),
        (Position(0, 0), Heading.WEST, Position(-1, 0)),
        (Position(0, 0), Heading.NORTH_WEST, Position(-1, -1)),
        (Position(1, -1), Heading.NORTH, Position(1, -2)),
    ],
)
def test_calculate_next_position(input_a, input_b, expected):
    assert calculate_next_position(input_a, input_b) == expected
