from starlette.testclient import TestClient

from regatta.api.auth import create_access_token
from regatta.main import app
from regatta.ws.connection_manager import connection_manager


def test_ws_connect():
    token = create_access_token()
    with TestClient(app) as client, client.websocket_connect(
        f"/games/mock_game_id/ws?token={token}"
    ):
        assert "mock_game_id" in connection_manager.active_connections


def test_ws_disconnect():
    token = create_access_token()
    with TestClient(app) as client, client.websocket_connect(
        f"/games/mock_game_id/ws?token={token}"
    ):
        pass

    assert connection_manager.active_connections["mock_game_id"] == []
