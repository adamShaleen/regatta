import random
from dataclasses import replace

from regatta.models.game import Game, GamePhase
from regatta.models.position import Position, calculate_next_position
from regatta.models.wind import Heading, PointOfSail, get_point_of_sail
from regatta.models.yacht import Yacht


def add_player(game: Game, player_id: str) -> Game:
    if game.phase != GamePhase.LOBBY:
        raise ValueError("You must be in the lobby to add new players")
    if player_id in game.players:
        raise ValueError("Player is already in the game")
    if len(game.players) >= 6:
        raise ValueError("There are already the max number of players in the game")

    updated_players = game.players | {player_id}
    return replace(game, players=updated_players)


def start_setup(game: Game) -> Game:
    if game.phase != GamePhase.LOBBY:
        raise ValueError("You must be in the lobby to start the game")
    if len(game.players) < 2:
        raise ValueError("Minimum of 2 players")

    shuffled_player_order = random.sample(list(game.players), len(game.players))

    return replace(
        game,
        setup_order=shuffled_player_order,
        phase=GamePhase.SETUP,
        current_player_index=0,
    )


def choose_starting_position(game: Game, player_id: str, position: Position) -> Game:
    if game.phase != GamePhase.SETUP:
        raise ValueError("Phase must be SETUP")

    if game.setup_order[game.current_player_index] != player_id:
        raise ValueError(f"It is not player_id {player_id}'s turn")

    if not game.board.is_on_starting_line(position):
        raise ValueError("Position must be on the starting line")

    if any(yacht.position == position for yacht in game.yachts.values()):
        raise ValueError("Position is already taken")

    new_yacht = Yacht(position, heading=game.wind_direction.opposite())
    updated_yachts = {**game.yachts, player_id: new_yacht}

    new_index = game.current_player_index + 1

    if new_index >= len(game.setup_order):
        return replace(
            game, yachts=updated_yachts, phase=GamePhase.RACING, current_player_index=0
        )
    else:
        return replace(game, yachts=updated_yachts, current_player_index=new_index)


def start_round(game: Game) -> Game:
    if game.phase != GamePhase.RACING:
        raise ValueError("Must be in RACING phase")

    roll = random.randint(1, 3)
    return replace(game, legs_per_turn=roll, legs_remaining=roll, has_used_puff=False)


def move_leg(game: Game, player_id: str, heading: Heading) -> Game:
    if game.phase != GamePhase.RACING:
        raise ValueError("Must be in RACING phase")

    if game.setup_order[game.current_player_index] != player_id:
        raise ValueError(f"It is not player_id {player_id}'s turn")

    if game.legs_remaining == 0:
        raise ValueError("Player has no legs remaining")

    point_of_sail = get_point_of_sail(game.wind_direction, heading)
    spaces = point_of_sail.speed

    # spinnaker bonus
    if game.yachts[player_id].spinnaker and point_of_sail in (
        PointOfSail.RUNNING,
        PointOfSail.BROAD_REACHING,
    ):
        spaces += 1

    next_position = game.yachts[player_id].position
    for _ in range(spaces):
        next_position = calculate_next_position(next_position, heading)

    if not game.board.is_in_bounds(next_position):
        raise ValueError("Position is out of bounds")

    if any(yacht.position == next_position for yacht in game.yachts.values()):
        raise ValueError("Position is occupied")

    updated_yacht = game.yachts[player_id].with_position(next_position)

    # Check if landed on a course mark
    if game.board.is_on_course_mark(next_position):
        new_marks = updated_yacht.marks_rounded | {next_position}
        updated_yacht = updated_yacht.with_marks_rounded(new_marks)

    updated_yachts = {**game.yachts, player_id: updated_yacht}

    # Check win condition
    all_marks_rounded = set(game.board.course_marks) <= set(updated_yacht.marks_rounded)
    on_finish_line = game.board.is_on_starting_line(next_position)

    if all_marks_rounded and on_finish_line:
        return replace(
            game,
            yachts=updated_yachts,
            legs_remaining=game.legs_remaining - 1,
            winner=player_id,
            phase=GamePhase.FINISHED,
        )

    return replace(game, yachts=updated_yachts, legs_remaining=game.legs_remaining - 1)


def end_turn(game: Game) -> Game:
    if game.phase != GamePhase.RACING:
        raise ValueError("Must be in RACING phase")

    if game.legs_remaining > 0:
        raise ValueError("Player still has legs remaining")

    next_index = game.current_player_index + 1
    legs_per_turn = game.legs_per_turn

    if next_index >= len(game.setup_order):
        next_index = 0
        legs_per_turn = random.randint(1, 3)

    return replace(
        game,
        current_player_index=next_index,
        legs_per_turn=legs_per_turn,
        legs_remaining=legs_per_turn,
        has_used_puff=False,
    )


def use_puff(game: Game, player_id: str, direction: Heading) -> Game:
    if game.phase != GamePhase.RACING:
        raise ValueError("Must be in RACING phase")

    if game.setup_order[game.current_player_index] != player_id:
        raise ValueError(f"It is not player_id {player_id}'s turn")

    if game.has_used_puff:
        raise ValueError("Puffs have already been used")

    player_yacht = game.yachts[player_id]

    if player_yacht.puff_count == 0:
        raise ValueError("Player is out of Puffs")

    new_position = calculate_next_position(player_yacht.position, direction)

    if not game.board.is_in_bounds(new_position):
        raise ValueError("New Position is out of bounds")

    if any(yacht.position == new_position for yacht in game.yachts.values()):
        raise ValueError("Position is occupied")

    new_puff_count = player_yacht.puff_count - 1

    updated_yacht = player_yacht.with_puff_count(new_puff_count).with_position(
        new_position
    )
    updated_yachts = {**game.yachts, player_id: updated_yacht}

    return replace(game, yachts=updated_yachts, has_used_puff=True)


def raise_spinnaker(game: Game, player_id: str) -> Game:
    if game.phase != GamePhase.RACING:
        raise ValueError("Must be in RACING phase")

    if game.setup_order[game.current_player_index] != player_id:
        raise ValueError(f"It is not player_id {player_id}'s turn")

    if game.yachts[player_id].spinnaker:
        raise ValueError("Spinnaker is already raised")

    updated_yacht = game.yachts[player_id].with_spinnaker(True)
    updated_yachts = {**game.yachts, player_id: updated_yacht}

    return replace(game, yachts=updated_yachts)


def lower_spinnaker(game: Game, player_id: str) -> Game:
    if game.phase != GamePhase.RACING:
        raise ValueError("Must be in RACING phase")

    if game.setup_order[game.current_player_index] != player_id:
        raise ValueError(f"It is not player_id {player_id}'s turn")

    if not game.yachts[player_id].spinnaker:
        raise ValueError("Spinnaker is already lowered")

    if game.legs_remaining == 0:
        raise ValueError("Player has no legs remaining")

    updated_yacht = game.yachts[player_id].with_spinnaker(False)
    updated_yachts = {**game.yachts, player_id: updated_yacht}

    updated_legs_remaining = game.legs_remaining - 1

    return replace(game, yachts=updated_yachts, legs_remaining=updated_legs_remaining)
