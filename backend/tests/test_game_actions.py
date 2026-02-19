import pytest

from regatta.core.game_actions import add_player, choose_starting_position, start_setup
from regatta.models.board import Board, Grid
from regatta.models.game import Game, GamePhase
from regatta.models.position import Position
from regatta.models.wind import Heading, WindDirection
from regatta.models.yacht import Yacht


def make_game(**overrides) -> Game:
    defaults = {
        "id": "mock_game_id",
        "board": Board(
            Grid(5, 5),
            course_marks=[Position(1, 1), Position(2, 2), Position(3, 3)],
            starting_line=(Position(0, 0), Position(1, 1)),
        ),
        "wind_direction": WindDirection.EAST,
    }
    return Game(**{**defaults, **overrides})


@pytest.mark.parametrize(
    "game,player_id,error",
    [
        (make_game(phase=GamePhase.FINISHED), "player_1", "must be in the lobby"),
        (make_game(players=frozenset({"player_1"})), "player_1", "already in the game"),
        (make_game(players=frozenset({f"p{i}" for i in range(6)})), "p7", "max number"),
    ],
)
def test_add_player_sad_path(game, player_id, error):
    with pytest.raises(ValueError, match=error):
        add_player(game, player_id)


def test_add_player_happy():
    game = make_game()
    updated_once = add_player(game, "new_player_id")

    assert len(game.players) == 0
    assert "new_player_id" in updated_once.players
    assert len(updated_once.players) == 1

    updated_twice = add_player(updated_once, "new_player_id_2")
    assert "new_player_id_2" in updated_twice.players
    assert len(updated_twice.players) == 2


@pytest.mark.parametrize(
    "game,error",
    [
        (
            make_game(phase=GamePhase.FINISHED),
            "You must be in the lobby to start the game",
        ),
        (make_game(players=frozenset({"player_1"})), "Minimum of 2 players"),
    ],
)
def test_start_setup_sad_path(game, error):
    with pytest.raises(ValueError, match=error):
        start_setup(game)


def test_start_setup_happy():
    game = make_game(players=frozenset({"player_1", "player_2", "player_3"}))
    started_game = start_setup(game)

    assert started_game.phase == GamePhase.SETUP
    assert set(started_game.setup_order) == game.players
    assert len(started_game.setup_order) == 3
    assert started_game.current_player_index == 0


@pytest.mark.parametrize(
    "game,player_id,position,error",
    [
        (
            make_game(phase=GamePhase.LOBBY),
            "player_1",
            Position(1, 1),
            "Phase must be SETUP",
        ),
        (
            make_game(phase=GamePhase.SETUP, setup_order=["player_2"]),
            "player_1",
            Position(1, 1),
            "It is not player_id player_1's turn",
        ),
        (
            make_game(phase=GamePhase.SETUP, setup_order=["player_1"]),
            "player_1",
            Position(3, 3),
            "Position must be on the starting line",
        ),
        (
            make_game(
                phase=GamePhase.SETUP,
                setup_order=["player_1", "player_2"],
                yachts={"player_2": Yacht(Position(0, 0), heading=WindDirection.WEST)},
                current_player_index=0,
            ),
            "player_1",
            Position(0, 0),
            "Position is already taken",
        ),
    ],
)
def test_choose_starting_position_sad_path(game, player_id, position, error):
    with pytest.raises(ValueError, match=error):
        choose_starting_position(game, player_id, position)
