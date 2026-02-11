from dataclasses import dataclass

from regatta.models.wind import Heading


@dataclass(frozen=True)
class Position:
    x: int
    y: int


_DIRECTION_DELTAS = {
    Heading.NORTH: (0, -1),
    Heading.NORTH_EAST: (1, -1),
    Heading.EAST: (1, 0),
    Heading.SOUTH_EAST: (1, 1),
    Heading.SOUTH: (0, 1),
    Heading.SOUTH_WEST: (-1, 1),
    Heading.WEST: (-1, 0),
    Heading.NORTH_WEST: (-1, -1),
}


def calculate_next_position(current_position: Position, heading: Heading) -> Position:
    dx, dy = _DIRECTION_DELTAS[heading]

    return Position(
        current_position.x + dx,
        current_position.y + dy,
    )
