import random
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from regatta.api.deps import get_current_user, get_db
from regatta.api.schemas import (
    AddPlayerRequest,
    ChooseStartingPositionRequest,
    GameResponse,
    MoveLegRequest,
    SpinnakerRequest,
    UsePuffRequest,
)
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
from regatta.db.models import GameRow
from regatta.models.board import Board, Grid
from regatta.models.game import Game
from regatta.models.position import Position
from regatta.models.wind import Heading, WindDirection
from regatta.serialization.game_serializer import deserialize_game, serialize_game
from regatta.ws.connection_manager import connection_manager

router = APIRouter(
    prefix="/games", tags=["games"], dependencies=[Depends(get_current_user)]
)


async def _get_game_or_404(game_id: uuid.UUID, db: AsyncSession) -> GameRow:
    game_row = await db.get(GameRow, game_id)
    if not game_row:
        raise HTTPException(status_code=404)
    return game_row


async def _save_game(game_row: GameRow, game: Game, db: AsyncSession) -> GameResponse:
    serialized_game = serialize_game(game)
    game_row.state = serialized_game

    await db.commit()
    await connection_manager.broadcast(str(game_row.id), serialized_game)

    return GameResponse.model_validate(serialized_game)


@router.post("/", response_model=GameResponse)
async def create_game(db: AsyncSession = Depends(get_db)):
    board = Board(
        grid=Grid(28, 20),
        course_marks=[
            Position(random.randint(10, 18), random.randint(1, 4)),
        ],
        starting_line=(Position(8, 19), Position(20, 19)),
    )

    game = Game(
        id=str(uuid.uuid4()),
        board=board,
        wind_direction=random.choice(list(WindDirection)),
    )
    serialized_game = serialize_game(game)
    game_row = GameRow(id=uuid.UUID(game.id), state=serialized_game)

    db.add(game_row)
    await db.commit()

    return GameResponse.model_validate(serialized_game)


@router.get("/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> GameResponse:
    game_row = await _get_game_or_404(game_id, db)
    return GameResponse.model_validate(game_row.state)


@router.post("/{game_id}/players", response_model=GameResponse)
async def add_player_to_game(
    game_id: uuid.UUID, request: AddPlayerRequest, db: AsyncSession = Depends(get_db)
) -> GameResponse:
    game_row = await _get_game_or_404(game_id, db)
    deserialized_game = deserialize_game(game_row.state)

    try:
        updated_game = add_player(deserialized_game, request.player_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    return await _save_game(game_row, updated_game, db)


@router.post("/{game_id}/start", response_model=GameResponse)
async def begin_setup(
    game_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> GameResponse:
    game_row = await _get_game_or_404(game_id, db)
    deserialized_game = deserialize_game(game_row.state)

    try:
        updated_game = start_setup(deserialized_game)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    return await _save_game(game_row, updated_game, db)


@router.post("/{game_id}/starting-position", response_model=GameResponse)
async def choose_start(
    game_id: uuid.UUID,
    request: ChooseStartingPositionRequest,
    db: AsyncSession = Depends(get_db),
) -> GameResponse:
    game_row = await _get_game_or_404(game_id, db)
    deserialized_game = deserialize_game(game_row.state)

    try:
        updated_game = choose_starting_position(
            deserialized_game, request.player_id, Position(request.x, request.y)
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    return await _save_game(game_row, updated_game, db)


@router.post("/{game_id}/round", response_model=GameResponse)
async def start_game_round(
    game_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> GameResponse:
    game_row = await _get_game_or_404(game_id, db)
    deserialized_game = deserialize_game(game_row.state)

    try:
        updated_game = start_round(deserialized_game)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    return await _save_game(game_row, updated_game, db)


@router.post("/{game_id}/move", response_model=GameResponse)
async def make_move(
    game_id: uuid.UUID,
    request: MoveLegRequest,
    db: AsyncSession = Depends(get_db),
) -> GameResponse:
    game_row = await _get_game_or_404(game_id, db)
    deserialized_game = deserialize_game(game_row.state)

    try:
        updated_game = move_leg(
            deserialized_game, request.player_id, Heading(request.heading)
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    return await _save_game(game_row, updated_game, db)


@router.post("/{game_id}/end-turn", response_model=GameResponse)
async def end_player_turn(
    game_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> GameResponse:
    game_row = await _get_game_or_404(game_id, db)
    deserialized_game = deserialize_game(game_row.state)

    try:
        updated_game = end_turn(deserialized_game)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    return await _save_game(game_row, updated_game, db)


@router.post("/{game_id}/puff", response_model=GameResponse)
async def puff(
    game_id: uuid.UUID,
    request: UsePuffRequest,
    db: AsyncSession = Depends(get_db),
) -> GameResponse:
    game_row = await _get_game_or_404(game_id, db)
    deserialized_game = deserialize_game(game_row.state)

    try:
        updated_game = use_puff(
            deserialized_game, request.player_id, WindDirection(request.direction)
        )

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    return await _save_game(game_row, updated_game, db)


@router.post("/{game_id}/spinnaker/raise", response_model=GameResponse)
async def spinnaker_raise(
    game_id: uuid.UUID,
    request: SpinnakerRequest,
    db: AsyncSession = Depends(get_db),
) -> GameResponse:
    game_row = await _get_game_or_404(game_id, db)
    deserialized_game = deserialize_game(game_row.state)

    try:
        updated_game = raise_spinnaker(deserialized_game, request.player_id)

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    return await _save_game(game_row, updated_game, db)


@router.post("/{game_id}/spinnaker/lower", response_model=GameResponse)
async def spinnaker_lower(
    game_id: uuid.UUID,
    request: SpinnakerRequest,
    db: AsyncSession = Depends(get_db),
) -> GameResponse:
    game_row = await _get_game_or_404(game_id, db)
    deserialized_game = deserialize_game(game_row.state)

    try:
        updated_game = lower_spinnaker(deserialized_game, request.player_id)

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    return await _save_game(game_row, updated_game, db)
