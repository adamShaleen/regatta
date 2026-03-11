from regatta.models.board import Board, Grid
from regatta.models.game import Game, GamePhase
from regatta.models.position import Position
from regatta.models.wind import WindDirection
from regatta.models.yacht import Yacht


def _serialize_position(position: Position) -> dict:
    return {"x": position.x, "y": position.y}


def _deserialize_position(d: dict) -> Position:
    return Position(x=d["x"], y=d["y"])


def _serialize_yacht(yacht: Yacht) -> dict:
    marks_rounded = sorted(
        [_serialize_position(mark) for mark in yacht.marks_rounded],
        key=lambda p: (p["x"], p["y"]),
    )

    return {
        "position": _serialize_position(yacht.position),
        "heading": yacht.heading.value,
        "spinnaker": yacht.spinnaker,
        "puff_count": yacht.puff_count,
        "marks_rounded": marks_rounded,
        "position_history": [_serialize_position(p) for p in yacht.position_history],
    }


def _deserialize_yacht(d: dict) -> Yacht:
    return Yacht(
        position=_deserialize_position(d["position"]),
        heading=WindDirection(d["heading"]),
        spinnaker=d["spinnaker"],
        puff_count=d["puff_count"],
        marks_rounded=frozenset(
            [_deserialize_position(position) for position in d["marks_rounded"]]
        ),
        position_history=tuple(
            _deserialize_position(p) for p in d.get("position_history", [])
        ),
    )


def _serialize_grid(grid: Grid) -> dict:
    return {"width": grid.width, "height": grid.height}


def _deserialize_grid(d: dict) -> Grid:
    return Grid(width=d["width"], height=d["height"])


def _serialize_board(board: Board) -> dict:
    position_1, position_2 = board.starting_line

    return {
        "grid": _serialize_grid(board.grid),
        "course_marks": [
            _serialize_position(position) for position in board.course_marks
        ],
        "starting_line": [
            _serialize_position(position_1),
            _serialize_position(position_2),
        ],
    }


def _deserialize_board(d: dict) -> Board:
    return Board(
        grid=_deserialize_grid(d["grid"]),
        course_marks=[
            _deserialize_position(position) for position in d["course_marks"]
        ],
        starting_line=(
            _deserialize_position(d["starting_line"][0]),
            _deserialize_position(d["starting_line"][1]),
        ),
    )


def serialize_game(game: Game) -> dict:
    return {
        "id": game.id,
        "board": _serialize_board(game.board),
        "wind_direction": game.wind_direction.value,
        "players": sorted(game.players),
        "yachts": {
            player_id: _serialize_yacht(yacht)
            for player_id, yacht in game.yachts.items()
        },
        "phase": game.phase.value,
        "setup_order": game.setup_order,
        "current_player_index": game.current_player_index,
        "legs_per_turn": game.legs_per_turn,
        "legs_remaining": game.legs_remaining,
        "has_used_puff": game.has_used_puff,
        "winner": game.winner,
    }


def deserialize_game(d: dict) -> Game:
    return Game(
        id=d["id"],
        board=_deserialize_board(d["board"]),
        wind_direction=WindDirection(d["wind_direction"]),
        players=frozenset(d["players"]),
        yachts={
            player_id: _deserialize_yacht(yacht)
            for player_id, yacht in d["yachts"].items()
        },
        phase=GamePhase(d["phase"]),
        setup_order=d["setup_order"],
        current_player_index=d["current_player_index"],
        legs_per_turn=d["legs_per_turn"],
        legs_remaining=d["legs_remaining"],
        has_used_puff=d["has_used_puff"],
        winner=d["winner"],
    )
