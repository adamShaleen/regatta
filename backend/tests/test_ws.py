from starlette.testclient import TestClient

from regatta.main import app
from regatta.ws.connection_manager import connection_manager


def test_ws_connect():
    with TestClient(app) as client, client.websocket_connect("/games/mock_game_id/ws"):
        assert "mock_game_id" in connection_manager.active_connections


def test_ws_disconnect():
    with TestClient(app) as client, client.websocket_connect("/games/mock_game_id/ws"):
        pass

    assert connection_manager.active_connections["mock_game_id"] == []
