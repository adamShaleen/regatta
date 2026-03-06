import asyncio
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    def connect(self, game_id: str, connection: WebSocket) -> None:
        self.active_connections[game_id].append(connection)

    def disconnect(self, game_id: str, connection: WebSocket) -> None:
        self.active_connections[game_id].remove(connection)

    async def _attempt_broadcast(
        self, game_id: str, connection: WebSocket, message: dict
    ) -> None:
        try:
            await connection.send_json(message)
        except Exception:
            self.disconnect(game_id, connection)

    async def broadcast(self, game_id: str, message: dict) -> None:
        await asyncio.gather(
            *[
                self._attempt_broadcast(game_id, connection, message)
                for connection in self.active_connections[game_id]
            ]
        )


connection_manager = ConnectionManager()
