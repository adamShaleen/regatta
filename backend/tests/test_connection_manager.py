from unittest.mock import AsyncMock

from regatta.ws.connection_manager import ConnectionManager


def test_connect():
    manager = ConnectionManager()
    connection = AsyncMock()

    manager.connect("mock_game_id", connection)
    assert connection in manager.active_connections["mock_game_id"]


def test_disconnect():
    manager = ConnectionManager()
    connection = AsyncMock()

    manager.connect("mock_game_id", connection)
    manager.disconnect("mock_game_id", connection)
    assert connection not in manager.active_connections["mock_game_id"]


async def test_broadcast_sends():
    manager = ConnectionManager()
    connection_1 = AsyncMock()
    connection_2 = AsyncMock()

    manager.connect("mock_game_id", connection_1)
    manager.connect("mock_game_id", connection_2)

    await manager.broadcast("mock_game_id", {"foo": "jazz"})

    connection_1.send_json.assert_called_once_with({"foo": "jazz"})
    connection_2.send_json.assert_called_once_with({"foo": "jazz"})


async def test_broadcast_removes():
    manager = ConnectionManager()
    good_connection = AsyncMock()
    bad_connection = AsyncMock()

    manager.connect("mock_game_id", good_connection)
    manager.connect("mock_game_id", bad_connection)

    bad_connection.send_json.side_effect = Exception("disconnected")

    await manager.broadcast("mock_game_id", {"foo": "jazz"})

    good_connection.send_json.assert_called_once_with({"foo": "jazz"})
    assert bad_connection not in manager.active_connections["mock_game_id"]
