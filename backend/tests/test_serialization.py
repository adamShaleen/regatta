import json

from regatta.serialization.game_serializer import deserialize_game, serialize_game
from tests.test_game_actions import make_game


def test_round_trip():
    game = make_game()

    serialized_game = serialize_game(game)
    deserialized_game = deserialize_game(serialized_game)

    assert deserialized_game == game


def test_serialized_form_is_json_compatible():
    game = make_game()
    json.dumps(serialize_game(game))  # raises if not JSON-safe
