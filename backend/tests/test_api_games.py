from httpx import AsyncClient, Response


async def exhaust_legs(
    client: AsyncClient, game_id: str, player_id: str, heading: int
) -> None:
    response: Response = await client.post(
        f"/games/{game_id}/move",
        json={"player_id": player_id, "heading": heading},
    )
    assert response.status_code == 200, response.json()
    while response.json()["legs_remaining"] > 0:
        response = await client.post(
            f"/games/{game_id}/move",
            json={"player_id": player_id, "heading": heading},
        )
        assert response.status_code == 200, response.json()


async def test_create_game(client: AsyncClient):
    response: Response = await client.post("/games/")
    assert response.status_code == 200

    data = response.json()
    assert data["phase"] == "LOBBY"
    assert data["players"] == []


async def test_full_game_happy_path(client: AsyncClient):
    game: Response = await client.post("/games/")
    assert game.status_code == 200

    game_data = game.json()
    game_id = game_data["id"]

    get_game: Response = await client.get(f"/games/{game_id}")
    assert get_game.status_code == 200

    add_player_1: Response = await client.post(
        f"/games/{game_id}/players",
        json={"player_id": "player_1"},
    )
    assert add_player_1.status_code == 200
    assert add_player_1.json()["players"] == ["player_1"]

    add_player_2: Response = await client.post(
        f"/games/{game_id}/players",
        json={"player_id": "player_2"},
    )
    assert add_player_2.status_code == 200
    assert "player_1" in add_player_2.json()["players"]
    assert "player_2" in add_player_2.json()["players"]

    setup: Response = await client.post(f"/games/{game_id}/start")

    assert setup.status_code == 200
    setup_data = setup.json()
    assert setup_data["phase"] == "SETUP"

    ordered_players = setup_data["setup_order"]

    position_1: Response = await client.post(
        f"/games/{game_id}/starting-position",
        json={"player_id": ordered_players[0], "x": 8, "y": 19},
    )
    assert position_1.status_code == 200
    assert position_1.json()["phase"] == "SETUP"

    position_2: Response = await client.post(
        f"/games/{game_id}/starting-position",
        json={"player_id": ordered_players[1], "x": 9, "y": 19},
    )
    assert position_2.status_code == 200
    assert position_2.json()["phase"] == "RACING"

    start_round: Response = await client.post(f"/games/{game_id}/round")
    assert start_round.status_code == 200

    await exhaust_legs(client, game_id, ordered_players[0], 45)
    end_turn_1: Response = await client.post(f"/games/{game_id}/end-turn")
    assert end_turn_1.status_code == 200

    await exhaust_legs(client, game_id, ordered_players[1], 45)
    end_turn_2: Response = await client.post(f"/games/{game_id}/end-turn")
    assert end_turn_2.status_code == 200

    puff_1: Response = await client.post(
        f"/games/{game_id}/puff",
        json={"player_id": ordered_players[0], "direction": 45},
    )
    assert puff_1.status_code == 200, puff_1.json()
    puff_data = puff_1.json()
    assert puff_data["has_used_puff"]

    spin_up: Response = await client.post(
        f"/games/{game_id}/spinnaker/raise", json={"player_id": ordered_players[0]}
    )
    assert spin_up.status_code == 200
    assert spin_up.json()["yachts"][ordered_players[0]]["spinnaker"]

    spin_down: Response = await client.post(
        f"/games/{game_id}/spinnaker/lower", json={"player_id": ordered_players[0]}
    )
    assert spin_down.status_code == 200
    assert not spin_down.json()["yachts"][ordered_players[0]]["spinnaker"]


async def test_get_game_not_found(client: AsyncClient) -> None:
    response = await client.get("/games/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


async def test_add_duplicate_player_returns_422(client: AsyncClient) -> None:
    game = await client.post("/games/")
    game_id = game.json()["id"]

    await client.post(f"/games/{game_id}/players", json={"player_id": "player_1"})

    response = await client.post(
        f"/games/{game_id}/players", json={"player_id": "player_1"}
    )
    assert response.status_code == 422
