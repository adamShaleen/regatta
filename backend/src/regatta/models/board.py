from dataclasses import dataclass

from regatta.models.position import Position


def _sign(n: int) -> int:
    if n > 0:
        return 1
    elif n < 0:
        return -1
    return 0


@dataclass
class Grid:
    width: int
    height: int

    def is_in_bounds(self, position: Position) -> bool:
        return 0 <= position.x < self.width and 0 <= position.y < self.height


@dataclass
class Board:
    grid: Grid
    course_marks: list[Position]
    starting_line: tuple[Position, Position]

    def is_in_bounds(self, position: Position) -> bool:
        return self.grid.is_in_bounds(position)

    def is_on_course_mark(self, position: Position) -> bool:
        return position in self.course_marks

    def get_starting_line_positions(self) -> list[Position]:
        point_a, point_b = self.starting_line

        dx = point_b.x - point_a.x
        dy = point_b.y - point_a.y

        step_x = _sign(dx)
        step_y = _sign(dy)

        current = point_a
        positions = [current]

        while current != point_b:
            current = Position(current.x + step_x, current.y + step_y)
            positions.append(current)

        return positions

    def is_on_starting_line(self, position: Position) -> bool:
        return position in self.get_starting_line_positions()
