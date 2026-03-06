from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from regatta.ws.connection_manager import connection_manager

router = APIRouter()


@router.websocket("/{game_id}/ws")
async def websocket_endpoint(game_id: str, connection: WebSocket) -> None:
    await connection.accept()
    connection_manager.connect(game_id, connection)

    try:
        while True:
            await connection.receive_text()  # keep connection alive
    except WebSocketDisconnect:
        connection_manager.disconnect(game_id, connection)
