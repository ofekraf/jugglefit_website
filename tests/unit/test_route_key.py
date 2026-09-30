import dataclasses

from pylib.classes.route import Route


def test_key_survives_serialize_round_trip(real_route):
    assert Route.deserialize(real_route.serialize()).key() == real_route.key()


def test_different_routes_have_different_keys(real_route):
    other = dataclasses.replace(real_route, duration_seconds=real_route.duration_seconds + 60)
    assert other.key() != real_route.key()


def test_key_does_not_depend_on_payload_encoding(real_route):
    # Same content, different zlib level -> different base64, same key.
    import json
    import zlib
    from base64 import b64encode
    payload = b64encode(zlib.compress(json.dumps(real_route.to_dict()).encode(), 1)).decode()
    assert payload != real_route.serialize()
    assert Route.deserialize(payload).key() == real_route.key()
