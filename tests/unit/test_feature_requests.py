"""Feature requests / bug reports: submit, review, public list, votes, privacy."""
import pytest

import app as appmod
from database.db_manager import db_manager
from tests.unit.conftest import get_csrf


@pytest.fixture(autouse=True)
def clean_requests():
    yield
    with db_manager.cursor(commit=True) as cur:
        cur.execute("DELETE FROM feature_votes")
        cur.execute("DELETE FROM feature_requests")


def _submit(client, **overrides):
    body = {"category": "website_feature", "title": "Dark mode", "body": "Please",
            "email": "me@example.com"}
    body.update(overrides)
    return client.post("/api/feature_requests", json=body, headers={"X-CSRF-Token": get_csrf(client)})


def _set_status(request_id, status):
    item = db_manager.get_feature_request(request_id)
    db_manager.update_feature_request(request_id, status=status, title=item["title"],
                                      body=item["body"], now_ms=1)


def _vote(client, request_id, voted=True):
    return client.post(f"/api/feature_requests/{request_id}/vote", json={"voted": voted},
                       headers={"X-CSRF-Token": get_csrf(client)})


@pytest.fixture
def admin_client(admin_password):
    client = appmod.app.test_client()
    client.post("/feature_requests/admin", data={"password": admin_password,
                                                 "_csrf_token": get_csrf(client)})
    return client


def test_page_renders_with_categories(client):
    html = client.get("/feature_requests").get_data(as_text=True)
    for label in ("Website feature", "Website bug", "Live event idea"):
        assert label in html
    assert "Ideas &amp; Bug Reports" in client.get("/").get_data(as_text=True)  # navbar link


def test_new_request_is_not_public_until_approved(client):
    res = _submit(client, title="Secret new idea")
    assert res.status_code == 201
    rid = res.get_json()["id"]
    assert "Secret new idea" not in client.get("/feature_requests").get_data(as_text=True)

    _set_status(rid, "planned")
    html = client.get("/feature_requests").get_data(as_text=True)
    assert "Secret new idea" in html and "Planned" in html

    _set_status(rid, "hidden")
    assert "Secret new idea" not in client.get("/feature_requests").get_data(as_text=True)


def test_private_fields_never_public(client):
    rid = _submit(client, category="website_bug", title="Timer broken", email="private@example.com",
                  page="/created_route").get_json()["id"]
    _set_status(rid, "open")
    item = db_manager.get_feature_request(rid)
    assert item["contact_email"] == "private@example.com"
    assert item["page"] == "/created_route" and item["user_agent"]

    html = client.get("/feature_requests").get_data(as_text=True)
    assert "Timer broken" in html and "Reported" in html
    assert "private@example.com" not in html
    for row in db_manager.get_public_feature_requests():
        assert not {"contact_email", "user_agent", "submitter_id", "page"} & set(row)


def test_page_and_user_agent_only_saved_for_bugs(client):
    rid = _submit(client, page="/x").get_json()["id"]
    item = db_manager.get_feature_request(rid)
    assert item["page"] is None and item["user_agent"] is None


@pytest.mark.parametrize("overrides", [
    {"category": "other"}, {"title": "x"}, {"title": "t" * 121}, {"body": "b" * 2001},
    {"email": "not-an-email"}, {"title": 123},
])
def test_validation(client, overrides):
    assert _submit(client, **overrides).status_code == 400
    assert db_manager.get_all_feature_requests() == []


def test_email_is_optional(client):
    assert _submit(client, email="").status_code == 201


def test_honeypot_is_silently_dropped(client):
    assert _submit(client, website="http://spam").status_code == 201
    assert db_manager.get_all_feature_requests() == []


def test_daily_limit(client):
    for i in range(5):
        assert _submit(client, title=f"Idea {i}").status_code == 201
    assert _submit(client, title="One too many").status_code == 429


def test_csrf_required(client):
    res = client.post("/api/feature_requests", json={"category": "website_feature", "title": "Hello"})
    assert res.status_code == 403


def test_vote_toggle_one_per_browser(client):
    rid = _submit(client).get_json()["id"]
    assert _vote(client, rid).status_code == 404        # not approved yet
    _set_status(rid, "open")
    assert _vote(client, rid).get_json()["votes"] == 1
    assert _vote(client, rid).get_json()["votes"] == 1  # same browser: still 1
    other = appmod.app.test_client()
    assert _vote(other, rid).get_json()["votes"] == 2
    assert _vote(client, rid, voted=False).get_json()["votes"] == 1


def test_bugs_cannot_be_voted(client):
    rid = _submit(client, category="website_bug").get_json()["id"]
    _set_status(rid, "open")
    assert _vote(client, rid).status_code == 404


def test_admin_off_without_password(client, monkeypatch):
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    assert client.get("/feature_requests/admin").status_code == 404


def test_admin_requires_login(client, admin_password):
    html = client.get("/feature_requests/admin").get_data(as_text=True)
    assert 'name="password"' in html
    res = client.post("/feature_requests/admin/1", data={"status": "open", "_csrf_token": get_csrf(client)})
    assert res.status_code == 403

    client.post("/feature_requests/admin", data={"password": "wrong", "_csrf_token": get_csrf(client)})
    assert 'name="password"' in client.get("/feature_requests/admin").get_data(as_text=True)


def test_admin_sees_private_info_and_approves(client, admin_client):
    rid = _submit(client, category="website_bug", title="Bug X", email="me@example.com").get_json()["id"]
    html = admin_client.get("/feature_requests/admin").get_data(as_text=True)
    assert "Bug X" in html and "me@example.com" in html

    res = admin_client.post(f"/feature_requests/admin/{rid}",
                            data={"status": "done", "title": "Bug X (fixed)", "body": "",
                                  "action": "save", "_csrf_token": get_csrf(admin_client)})
    assert res.status_code == 302
    assert db_manager.get_feature_request(rid)["status"] == "done"
    html = client.get("/feature_requests").get_data(as_text=True)
    assert "Bug X (fixed)" in html and "Fixed" in html

    admin_client.post(f"/feature_requests/admin/{rid}",
                      data={"action": "delete", "_csrf_token": get_csrf(admin_client)})
    assert db_manager.get_feature_request(rid) is None


def test_admin_filters(client, admin_client):
    _submit(client, category="website_bug", title="A bug")
    _submit(client, category="live_event_idea", title="An idea")
    html = admin_client.get("/feature_requests/admin?category=website_bug").get_data(as_text=True)
    assert "A bug" in html and "An idea" not in html
