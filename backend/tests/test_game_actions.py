import pytest

from regatta.core.game_actions import (
    add_player,
    choose_starting_position,
    end_turn,
    lower_spinnaker,
    move_leg,
    raise_spinnaker,
    start_round,
    start_setup,
    use_puff,
)
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


def test_choose_starting_position_happy():
    larger_board = Board(
        Grid(5, 5),
        course_marks=[Position(2, 2)],
        starting_line=(Position(0, 0), Position(3, 0)),
    )

    one_player = make_game(
        board=larger_board,
        phase=GamePhase.SETUP,
        setup_order=["player_1", "player_2", "player_3"],
        yachts={"player_1": Yacht(Position(0, 0), heading=WindDirection.WEST)},
        current_player_index=1,
    )

    two_players = choose_starting_position(one_player, "player_2", Position(1, 0))

    assert "player_2" in two_players.yachts
    assert two_players.phase == GamePhase.SETUP
    assert two_players.current_player_index == 2
    assert two_players.yachts["player_2"].position == Position(1, 0)
    assert two_players.yachts["player_2"].heading == WindDirection.WEST

    all_players = choose_starting_position(two_players, "player_3", Position(2, 0))
    assert "player_3" in all_players.yachts
    assert all_players.phase == GamePhase.RACING
    assert all_players.current_player_index == 0


def test_start_round_sad_path():
    with pytest.raises(ValueError, match="Must be in RACING phase"):
        start_round(make_game(phase=GamePhase.FINISHED))


def test_start_round_happy():
    before_start = make_game(phase=GamePhase.RACING)
    started = start_round(before_start)

    assert not started.has_used_puff
    assert 1 <= started.legs_per_turn <= 3
    assert started.legs_remaining == started.legs_per_turn


@pytest.mark.parametrize(
    "game,player_id,direction,error",
    [
        (
            make_game(phase=GamePhase.FINISHED),
            "player_1",
            Heading.EAST,
            "Must be in RACING phase",
        ),
        (
            make_game(phase=GamePhase.RACING, setup_order=["player_2"]),
            "player_1",
            Heading.EAST,
            "It is not player_id player_1's turn",
        ),
        (
            make_game(
                phase=GamePhase.RACING, setup_order=["player_1"], legs_remaining=0
            ),
            "player_1",
            Heading.EAST,
            "Player has no legs remaining",
        ),
        (
            make_game(
                phase=GamePhase.RACING,
                setup_order=["player_1"],
                legs_remaining=1,
                yachts={"player_1": Yacht(Position(2, 4), Heading.SOUTH)},
            ),
            "player_1",
            Heading.SOUTH,
            "Position is out of bounds",
        ),
        (
            make_game(
                phase=GamePhase.RACING,
                setup_order=["player_1"],
                legs_remaining=1,
                yachts={
                    "player_1": Yacht(Position(1, 2), Heading.EAST),
                    "player_2": Yacht(Position(1, 4), Heading.EAST),
                },
            ),
            "player_1",
            Heading.SOUTH,
            "Position is occupied",
        ),
    ],
)
def test_move_leg_sad_paths(game, player_id, direction, error):
    with pytest.raises(ValueError, match=error):
        move_leg(game, player_id, direction)


def test_move_leg_happy():
    starting_game_state = make_game(
        phase=GamePhase.RACING,
        setup_order=["player_1", "player_2"],
        legs_remaining=1,
        yachts={
            "player_1": Yacht(Position(1, 1), Heading.EAST),
            "player_2": Yacht(Position(2, 2), Heading.EAST),
        },
    )

    after_move = move_leg(starting_game_state, "player_1", Heading.SOUTH)
    assert after_move.yachts["player_1"].position == Position(1, 3)
    assert after_move.legs_remaining == 0


def test_move_leg_rounds_mark():
    game = make_game(
        phase=GamePhase.RACING,
        setup_order=["player_1"],
        legs_remaining=1,
        yachts={"player_1": Yacht(Position(2, 0), Heading.EAST)},
    )

    after_move = move_leg(game, "player_1", Heading.SOUTH)

    assert after_move.yachts["player_1"].position == Position(2, 2)
    assert Position(2, 2) in after_move.yachts["player_1"].marks_rounded


def test_move_leg_win():
    game = make_game(
        phase=GamePhase.RACING,
        setup_order=["player_1"],
        legs_remaining=1,
        yachts={
            "player_1": Yacht(
                Position(1, 3),
                Heading.EAST,
                marks_rounded=frozenset({Position(2, 2), Position(3, 3)}),
            )
        },
    )

    # Moving NORTH with EAST wind = BEAM_REACHING = 2 spaces
    # (1, 3) → (1, 1) which is a course mark AND on finish line
    after_move = move_leg(game, "player_1", Heading.NORTH)

    assert Position(1, 1) in after_move.yachts["player_1"].marks_rounded
    assert after_move.winner == "player_1"
    assert after_move.phase == GamePhase.FINISHED


def test_move_leg_no_win_without_all_marks():
    game = make_game(
        phase=GamePhase.RACING,
        setup_order=["player_1"],
        legs_remaining=1,
        yachts={
            "player_1": Yacht(
                Position(1, 3),
                Heading.EAST,
                marks_rounded=frozenset({Position(2, 2)}),  # missing (3,3)
            )
        },
    )

    after_move = move_leg(game, "player_1", Heading.NORTH)

    assert after_move.winner is None
    assert after_move.phase == GamePhase.RACING


def test_move_leg_spinnaker_bonus():
    # Wind EAST, moving WEST = RUNNING (2 spaces) + spinnaker (+1) = 3 spaces
    game = make_game(
        phase=GamePhase.RACING,
        setup_order=["player_1"],
        legs_remaining=1,
        yachts={"player_1": Yacht(Position(3, 2), Heading.EAST, spinnaker=True)},
    )

    after_move = move_leg(game, "player_1", Heading.WEST)

    # 3 spaces WEST: (3,2) → (0,2)
    assert after_move.yachts["player_1"].position == Position(0, 2)


@pytest.mark.parametrize(
    "game,error",
    [
        (make_game(phase=GamePhase.SETUP), "Must be in RACING phase"),
        (
            make_game(phase=GamePhase.RACING, legs_remaining=1),
            "Player still has legs remaining",
        ),
    ],
)
def test_end_turn_sad_paths(game, error):
    with pytest.raises(ValueError, match=error):
        end_turn(game)


def test_end_turn_happy():
    mid_round = make_game(
        phase=GamePhase.RACING,
        setup_order=["player_1", "player_2", "player_3"],
        current_player_index=0,
        legs_per_turn=2,
        legs_remaining=0,
        has_used_puff=True,
    )

    after_p1 = end_turn(mid_round)

    assert after_p1.current_player_index == 1
    assert after_p1.legs_remaining == 2  # same as legs_per_turn
    assert after_p1.legs_per_turn == 2  # unchanged mid-round
    assert not after_p1.has_used_puff

    end_of_round = make_game(
        phase=GamePhase.RACING,
        setup_order=["player_1", "player_2"],
        current_player_index=1,  # last player
        legs_per_turn=2,
        legs_remaining=0,
    )

    new_round = end_turn(end_of_round)

    assert new_round.current_player_index == 0  # wrapped
    assert 1 <= new_round.legs_per_turn <= 3  # new roll
    assert new_round.legs_remaining == new_round.legs_per_turn


@pytest.mark.parametrize(
    "game,player_id,direction,error",
    [
        (
            make_game(phase=GamePhase.FINISHED),
            "player_1",
            Heading.WEST,
            "Must be in RACING phase",
        ),
        (
            make_game(phase=GamePhase.RACING, setup_order=["player_2"]),
            "player_1",
            Heading.EAST,
            "It is not player_id player_1's turn",
        ),
        (
            make_game(
                phase=GamePhase.RACING, setup_order=["player_1"], has_used_puff=True
            ),
            "player_1",
            Heading.EAST,
            "Puffs have already been used",
        ),
        (
            make_game(
                phase=GamePhase.RACING,
                setup_order=["player_1"],
                yachts={
                    "player_1": Yacht(
                        Position(1, 1), heading=Heading.EAST, puff_count=0
                    )
                },
            ),
            "player_1",
            Heading.EAST,
            "Player is out of Puffs",
        ),
        (
            make_game(
                phase=GamePhase.RACING,
                setup_order=["player_1"],
                yachts={"player_1": Yacht(Position(6, 6), Heading.WEST)},
            ),
            "player_1",
            Heading.EAST,
            "New Position is out of bounds",
        ),
        (
            make_game(
                phase=GamePhase.RACING,
                setup_order=["player_1", "player_2"],
                current_player_index=0,
                yachts={
                    "player_1": Yacht(Position(1, 1), Heading.EAST),
                    "player_2": Yacht(Position(2, 1), Heading.EAST),
                },
            ),
            "player_1",
            Heading.EAST,
            "Position is occupied",
        ),
    ],
)
def test_use_puff_sad_paths(game, player_id, direction, error):
    with pytest.raises(ValueError, match=error):
        use_puff(game, player_id, direction)


def test_use_puff_happy():
    game = make_game(
        phase=GamePhase.RACING,
        setup_order=["player_1", "player_2"],
        current_player_index=0,
        yachts={
            "player_1": Yacht(Position(1, 1), heading=Heading.EAST),
            "player_2": Yacht(Position(2, 2), heading=Heading.EAST),
        },
    )

    after_puff = use_puff(game, "player_1", direction=Heading.EAST)

    assert after_puff.has_used_puff
    assert after_puff.yachts["player_1"].puff_count == 1
    assert after_puff.yachts["player_1"].position == Position(2, 1)


@pytest.mark.parametrize(
    "game,player_id,error",
    [
        (
            make_game(phase=GamePhase.FINISHED),
            "player_1",
            "Must be in RACING phase",
        ),
        (
            make_game(phase=GamePhase.RACING, setup_order=["player_2"]),
            "player_1",
            "It is not player_id player_1's turn",
        ),
        (
            make_game(
                phase=GamePhase.RACING,
                setup_order=["player_1"],
                yachts={
                    "player_1": Yacht(Position(1, 1), Heading.EAST, spinnaker=True)
                },
            ),
            "player_1",
            "Spinnaker is already raised",
        ),
    ],
)
def test_raise_spinnaker_sad_paths(game, player_id, error):
    with pytest.raises(ValueError, match=error):
        raise_spinnaker(game, player_id)


def test_raise_spinnaker_happy():
    game = make_game(
        phase=GamePhase.RACING,
        setup_order=["player_1"],
        yachts={"player_1": Yacht(Position(1, 1), Heading.EAST)},
    )

    after_raised = raise_spinnaker(game, "player_1")

    assert after_raised.yachts["player_1"].spinnaker


@pytest.mark.parametrize(
    "game,player_id,error",
    [
        (
            make_game(phase=GamePhase.FINISHED),
            "player_1",
            "Must be in RACING phase",
        ),
        (
            make_game(phase=GamePhase.RACING, setup_order=["player_2"]),
            "player_1",
            "It is not player_id player_1's turn",
        ),
        (
            make_game(
                phase=GamePhase.RACING,
                setup_order=["player_1"],
                yachts={
                    "player_1": Yacht(Position(1, 1), Heading.EAST, spinnaker=False)
                },
            ),
            "player_1",
            "Spinnaker is already lowered",
        ),
        (
            make_game(
                phase=GamePhase.RACING,
                setup_order=["player_1"],
                legs_remaining=0,
                yachts={
                    "player_1": Yacht(Position(1, 1), Heading.EAST, spinnaker=True)
                },
            ),
            "player_1",
            "Player has no legs remaining",
        ),
    ],
)
def test_lower_spinnaker_sad_paths(game, player_id, error):
    with pytest.raises(ValueError, match=error):
        lower_spinnaker(game, player_id)


def test_lower_spinnaker_happy():
    game = make_game(
        phase=GamePhase.RACING,
        setup_order=["player_1"],
        legs_remaining=1,
        yachts={"player_1": Yacht(Position(1, 1), Heading.EAST, spinnaker=True)},
    )

    after_lowered = lower_spinnaker(game, "player_1")

    assert not after_lowered.yachts["player_1"].spinnaker
    assert after_lowered.legs_remaining == 0  # was 1, now 0
