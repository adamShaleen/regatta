import random
from dataclasses import replace

from regatta.models.game import Game, GamePhase
from regatta.models.position import Position
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
