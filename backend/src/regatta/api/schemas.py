from pydantic import BaseModel


class AddPlayerRequest(BaseModel):
    player_id: str


class ChooseStartingPositionRequest(BaseModel):
    player_id: str
    x: int
    y: int


class MoveLegRequest(BaseModel):
    player_id: str
    heading: int


class UsePuffRequest(BaseModel):
    player_id: str
    direction: int


class SpinnakerRequest(BaseModel):
    player_id: str


class PositionResponse(BaseModel):
    x: int
    y: int


class YachtResponse(BaseModel):
    position: PositionResponse
    heading: int
    spinnaker: bool
    puff_count: int
    marks_rounded: list[PositionResponse]
    position_history: list[PositionResponse]


class GridResponse(BaseModel):
    width: int
    height: int


class BoardResponse(BaseModel):
    grid: GridResponse
    course_marks: list[PositionResponse]
    starting_line: list[PositionResponse]  # 2 element list


class GameResponse(BaseModel):
    id: str
    board: BoardResponse
    wind_direction: int
    players: list[str]
    yachts: dict[str, YachtResponse]
    phase: str
    setup_order: list[str]
    current_player_index: int
    legs_per_turn: int
    legs_remaining: int
    has_used_puff: bool
    winner: str | None
