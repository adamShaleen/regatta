import pytest

from regatta.models.board import Board, Grid, _sign
from regatta.models.position import Position


@pytest.fixture
def board():
    return Board(
        Grid(5, 5),
        [Position(1, 1), Position(2, 2), Position(3, 3)],
        (Position(0, 0), Position(3, 3)),
    )


@pytest.mark.parametrize(
    "input_a,expected",
    [(1, 1), (-1, -1), (0, 0)],
)
def test_sign(input_a, expected):
    assert _sign(input_a) == expected


def test_grid():
    grid = Grid(2, 2)
    assert grid.width == 2
    assert grid.height == 2
    assert not grid.is_in_bounds(Position(3, 3))
    assert grid.is_in_bounds(Position(1, 1))


def test_board():
    board = Board(
        Grid(5, 5),
        [Position(1, 1), Position(2, 2), Position(3, 3)],
        (Position(0, 0), Position(1, 1)),
    )

    assert board.grid == Grid(5, 5)
    assert board.course_marks == [Position(1, 1), Position(2, 2), Position(3, 3)]
    assert board.starting_line == (Position(0, 0), Position(1, 1))


def test_board_is_in_bounds(board):
    assert not board.is_in_bounds(Position(6, 6))
    assert board.is_in_bounds(Position(3, 3))


def test_board_is_on_course_mark(board):
    assert board.is_on_course_mark(Position(1, 1))
    assert not board.is_on_course_mark(Position(4, 5))


def test_board_get_starting_line_positions(board):
    assert board.get_starting_line_positions() == [
        Position(0, 0),
        Position(1, 1),
        Position(2, 2),
        Position(3, 3),
    ]


def test_board_is_on_starting_line(board):
    assert board.is_on_starting_line(Position(0, 0))
    assert board.is_on_starting_line(Position(2, 2))
    assert not board.is_on_starting_line(Position(4, 4))
