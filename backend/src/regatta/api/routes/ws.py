from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from regatta.api.auth import decode_token
from regatta.ws.connection_manager import connection_manager

router = APIRouter()


@router.websocket("/{game_id}/ws")
async def websocket_endpoint(
    game_id: str, connection: WebSocket, token: str = Query(...)
) -> None:
    try:
        decode_token(token)
    except Exception:
        await connection.close(code=1008)
        return

    await connection.accept()
    connection_manager.connect(game_id, connection)

    try:
        while True:
            await connection.receive_text()  # keep connection alive
    except WebSocketDisconnect:
        connection_manager.disconnect(game_id, connection)
