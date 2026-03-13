import random
from dataclasses import replace

from regatta.core.geometry import (
    bounding_box_contains,
    convex_hull,
    is_strictly_inside_hull,
)
from regatta.models.game import Game, GamePhase
from regatta.models.position import Position, calculate_next_position
from regatta.models.wind import (
    Heading,
    PointOfSail,
    detect_maneuver,
    get_point_of_sail,
    get_tack,
)
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

    new_yacht = Yacht(
        position, heading=game.wind_direction.opposite(), position_history=(position,)
    )
    updated_yachts = {**game.yachts, player_id: new_yacht}

    new_index = game.current_player_index + 1

    if new_index >= len(game.setup_order):
        game_ready_to_start = replace(
            game, yachts=updated_yachts, phase=GamePhase.RACING, current_player_index=0
        )
        return start_round(game_ready_to_start)
    else:
        return replace(game, yachts=updated_yachts, current_player_index=new_index)


def start_round(game: Game) -> Game:
    if game.phase != GamePhase.RACING:
        raise ValueError("Must be in RACING phase")

    roll = random.randint(1, 3)
    game = replace(
        game,
        legs_per_turn=roll,
        legs_remaining=roll,
        has_used_puff=False,
        last_event=None,
    )
    player_id = game.setup_order[game.current_player_index]
    penalty = _get_blanket_penalty(game, player_id)

    if penalty == 0:
        return game

    game = replace(game, legs_remaining=max(0, game.legs_remaining - penalty))

    if game.legs_remaining == 0:
        return replace(end_turn(game), last_event="Blanketed! Turn lost.")

    return replace(game, last_event="Partially blanketed — 1 leg lost.")


def move_leg(game: Game, player_id: str, heading: Heading) -> Game:
    if game.phase != GamePhase.RACING:
        raise ValueError("Must be in RACING phase")

    if game.setup_order[game.current_player_index] != player_id:
        raise ValueError(f"It is not player_id {player_id}'s turn")

    if game.legs_remaining == 0:
        raise ValueError("Player has no legs remaining")

    maneuver = detect_maneuver(
        game.wind_direction, game.yachts[player_id].heading, heading
    )

    point_of_sail = get_point_of_sail(game.wind_direction, heading)
    spaces = point_of_sail.speed

    if spaces == 0:
        raise ValueError("Cannot sail directly into the wind")

    # spinnaker bonus
    if game.yachts[player_id].spinnaker and point_of_sail in (
        PointOfSail.RUNNING,
        PointOfSail.BROAD_REACHING,
    ):
        spaces += 1

    prev_marks_rounded = game.yachts[player_id].marks_rounded
    current_marks_rounded = prev_marks_rounded
    current_history = game.yachts[player_id].position_history

    next_position = game.yachts[player_id].position
    for _ in range(spaces):
        candidate = calculate_next_position(next_position, heading)
        if game.board.is_on_course_mark(candidate):
            raise ValueError("Cannot sail through a course mark")
        next_position = candidate
        current_history = current_history + (next_position,)

        if len(current_history) >= 8:
            history_list = list(current_history)
            for mark in game.board.course_marks:
                if mark not in current_marks_rounded and bounding_box_contains(
                    history_list, mark
                ):
                    hull = convex_hull(history_list)
                    if is_strictly_inside_hull(hull, mark):
                        current_marks_rounded = current_marks_rounded | {mark}

        all_marks_rounded = set(game.board.course_marks) <= set(current_marks_rounded)
        if all_marks_rounded and game.board.is_on_starting_line(next_position):
            break

    _check_right_of_way(game, player_id, heading, next_position)

    if not game.board.is_in_bounds(next_position):
        raise ValueError("Position is out of bounds")

    if any(yacht.position == next_position for yacht in game.yachts.values()):
        raise ValueError("Position is occupied")

    updated_yacht = (
        game.yachts[player_id]
        .with_position(next_position)
        .with_heading(heading)
        .with_marks_rounded(current_marks_rounded)
        .with_position_history(current_history)
    )

    updated_yachts = {**game.yachts, player_id: updated_yacht}

    # Check win condition
    all_marks_rounded = set(game.board.course_marks) <= set(current_marks_rounded)
    on_finish_line = game.board.is_on_starting_line(next_position)
    newly_rounded = len(current_marks_rounded) > len(prev_marks_rounded)

    if all_marks_rounded and on_finish_line:
        return replace(
            game,
            yachts=updated_yachts,
            legs_remaining=game.legs_remaining - 1,
            winner=player_id,
            phase=GamePhase.FINISHED,
            last_event=f"{player_id} wins the race!",
        )

    legs_cost = 2 if maneuver else 1

    if newly_rounded:
        last_event: str | None = "Rounded the mark!"
    elif maneuver == "tack":
        last_event = "Tacked — 1 extra leg cost."
    elif maneuver == "jibe":
        last_event = "Jibed — 1 extra leg cost."
    else:
        last_event = game.last_event

    updated_game = replace(
        game,
        yachts=updated_yachts,
        legs_remaining=max(0, game.legs_remaining - legs_cost),
        last_event=last_event,
    )

    if updated_game.legs_remaining == 0:
        return end_turn(updated_game)

    return updated_game


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

    if game.board.is_on_course_mark(new_position):
        raise ValueError("Cannot puff onto a course mark")

    if not game.board.is_in_bounds(new_position):
        raise ValueError("New Position is out of bounds")

    if any(yacht.position == new_position for yacht in game.yachts.values()):
        raise ValueError("Position is occupied")

    new_puff_count = player_yacht.puff_count - 1

    current_marks_rounded = player_yacht.marks_rounded
    current_history = player_yacht.position_history + (new_position,)

    if len(current_history) >= 8:
        history_list = list(current_history)
        for mark in game.board.course_marks:
            if mark not in current_marks_rounded and bounding_box_contains(
                history_list, mark
            ):
                hull = convex_hull(history_list)
                if is_strictly_inside_hull(hull, mark):
                    current_marks_rounded = current_marks_rounded | {mark}

    newly_rounded = len(current_marks_rounded) > len(player_yacht.marks_rounded)
    last_event = "Rounded the mark via puff!" if newly_rounded else game.last_event

    updated_yacht = (
        player_yacht.with_puff_count(new_puff_count)
        .with_position(new_position)
        .with_marks_rounded(current_marks_rounded)
        .with_position_history(current_history)
    )
    updated_yachts = {**game.yachts, player_id: updated_yacht}

    return replace(
        game, yachts=updated_yachts, has_used_puff=True, last_event=last_event
    )


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

    updated_game = replace(
        game, yachts=updated_yachts, legs_remaining=game.legs_remaining - 1
    )

    if updated_game.legs_remaining == 0:
        return end_turn(updated_game)

    return updated_game


def _get_blanket_penalty(game: Game, player_id: str) -> int:
    yacht = game.yachts[player_id]
    windward_1 = calculate_next_position(yacht.position, game.wind_direction)
    windward_2 = calculate_next_position(windward_1, game.wind_direction)

    for other_player, other_yacht in game.yachts.items():
        if other_player == player_id:
            continue
        if other_yacht.position == windward_1:
            return game.legs_remaining
        if other_yacht.spinnaker and other_yacht.position == windward_2:
            return 1
    return 0


def _check_right_of_way(
    game: Game, player_id: str, heading: Heading, destination: Position
) -> None:
    """Raises ValueError if destination violates the opposite tack rule."""
    if get_tack(game.wind_direction, heading) != "port":
        return

    for other_id, other_yacht in game.yachts.items():
        if other_id == player_id:
            continue

        if get_tack(game.wind_direction, other_yacht.heading) != "starboard":
            continue
        starboard_next = calculate_next_position(
            other_yacht.position, other_yacht.heading
        )

        if destination == starboard_next:
            raise ValueError(
                "Right-of-way violation: port-tack yacht must keep clear of "
                "starboard-tack yacht"
            )
