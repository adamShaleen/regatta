from dataclasses import dataclass, field
from enum import Enum

from regatta.models.board import Board
from regatta.models.wind import WindDirection
from regatta.models.yacht import Yacht


class GamePhase(Enum):
    LOBBY = "LOBBY"
    SETUP = "SETUP"
    RACING = "RACING"
    FINISHED = "FINISHED"


@dataclass(frozen=True)
class Game:
    # core
    id: str
    board: Board
    wind_direction: WindDirection
    players: frozenset[str] = field(default_factory=frozenset)
    yachts: dict[str, Yacht] = field(default_factory=dict)

    # Phase tracking
    phase: GamePhase = GamePhase.LOBBY
    setup_order: list[str] = field(default_factory=list)
    current_player_index: int = 0

    # Turn state
    spaces_remaining: int = 0
    has_used_puff: bool = False

    # End state
    winner: str | None = None
