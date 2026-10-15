"""Trick feedback on generated routes + generator ordering."""
import pytest

from tests.unit.conftest import get_csrf
from database.db_manager import db_manager
from pylib.classes.prop import Prop
from pylib.route_generator.route_generator import RouteGenerator


@pytest.fixture(autouse=True)
def clean_feedback():
    yield
    with db_manager.cursor(commit=True) as cur:
        cur.execute("DELETE FROM trick_feedback")


def _generate(client):
    form = {
        "route_name": "Test", "prop": "balls", "min_props": 3, "max_props": 5,
        "min_difficulty": 0, "max_difficulty": 40, "route_length": 5, "route_duration": 10,
        "_csrf_token": get_csrf(client),
    }
    res = client.post("/generate_route", data=form)
    assert res.status_code == 302
    return res.location.split("route=", 1)[1]


def _route_param(location_value):
    from urllib.parse import unquote
    return unquote(location_value)


def _vote(client, route, index, vote):
    return client.post("/api/trick_feedback", json={"route": route, "trick_index": index, "vote": vote},
                       headers={"X-CSRF-Token": get_csrf(client)})


def test_generator_orders_easiest_to_hardest():
    for _ in range(20):
        route = RouteGenerator.generate(prop=Prop.Balls, min_props=3, max_props=7,
                                        min_difficulty=0, max_difficulty=60, route_length=6)
        diffs = [t.difficulty for t in route.tricks]
        assert diffs == sorted(diffs)


def test_buttons_only_on_generated_routes(client, route_payload):
    # A shared / past-event route: no feedback UI.
    html = client.get("/created_route", query_string={"route": route_payload}).get_data(as_text=True)
    assert "trick_feedback.js" not in html

    route = _route_param(_generate(client))
    html = client.get("/created_route", query_string={"route": route}).get_data(as_text=True)
    assert "trick_feedback.js" in html
    assert "window.TRICK_FEEDBACK" in html

    # Run route / live event never show it, even for a generated route.
    for path in ("/run_route", "/live_event"):
        assert "trick_feedback.js" not in client.get(path, query_string={"route": route}).get_data(as_text=True)


def test_vote_is_stored_replaced_and_removed(client):
    route = _route_param(_generate(client))
    assert _vote(client, route, 0, "too_easy").status_code == 200
    assert _vote(client, route, 0, "too_hard").status_code == 200   # replaces, not adds
    assert _vote(client, route, 2, "dislike").status_code == 200
    summary = db_manager.get_trick_feedback_summary("balls")
    assert sum(r["total"] for r in summary) == 2
    assert sum(r["too_hard"] for r in summary) == 1 and sum(r["too_easy"] for r in summary) == 0

    # The page restores this browser's votes.
    html = client.get("/created_route", query_string={"route": route}).get_data(as_text=True)
    assert '"0": "too_hard"' in html and '"2": "dislike"' in html

    assert _vote(client, route, 0, None).status_code == 200
    assert sum(r["total"] for r in db_manager.get_trick_feedback_summary("balls")) == 1


def test_vote_rejected_for_non_generated_route(client, route_payload):
    assert _vote(client, route_payload, 0, "too_easy").status_code == 403
    assert db_manager.get_trick_feedback_summary() == []


@pytest.mark.parametrize("index,vote", [(99, "too_easy"), (-1, "too_easy"), (0, "great")])
def test_vote_validation(client, index, vote):
    route = _route_param(_generate(client))
    assert _vote(client, route, index, vote).status_code == 400


def test_feedback_key_ignores_tag_order():
    from blueprints.trick_feedback import feedback_route_key
    from pylib.classes.route import Route
    route = RouteGenerator.generate(prop=Prop.Balls, min_difficulty=0, max_difficulty=100, route_length=8)
    data = route.to_dict()
    for t in data["tricks"]:
        t["tags"] = list(reversed(t["tags"]))
    assert feedback_route_key(Route.from_dict(data)) == feedback_route_key(route)


def test_feedback_does_not_change_tricks(client):
    from hardcoded_database.tricks import ALL_PROPS_TRICKS
    before = [(t.name, t.difficulty) for t in ALL_PROPS_TRICKS[Prop.Balls]]
    route = _route_param(_generate(client))
    for i in range(5):
        _vote(client, route, i, "too_hard")
    assert [(t.name, t.difficulty) for t in ALL_PROPS_TRICKS[Prop.Balls]] == before
