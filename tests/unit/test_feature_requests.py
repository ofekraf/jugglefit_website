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
            "contact": "me@example.com"}
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
    link = "https://jugglefit.com/created_route?route=eJzFlM9u4yAQ"
    rid = _submit(client, category="website_bug", title="Timer broken", contact="private@example.com",
                  page=link).get_json()["id"]
    _set_status(rid, "open")
    item = db_manager.get_feature_request(rid)
    assert item["contact"] == "private@example.com"
    assert item["page"] == link and item["user_agent"]

    html = client.get("/feature_requests").get_data(as_text=True)
    assert "Timer broken" in html and "Reported" in html
    assert "private@example.com" not in html and link not in html
    for row in db_manager.get_public_feature_requests():
        assert not {"contact", "user_agent", "submitter_id", "page"} & set(row)


def test_page_and_user_agent_only_saved_for_bugs(client):
    rid = _submit(client, page="/x").get_json()["id"]
    item = db_manager.get_feature_request(rid)
    assert item["page"] is None and item["user_agent"] is None


@pytest.mark.parametrize("overrides", [
    {"category": "other"}, {"title": "x"}, {"title": "t" * 121}, {"body": "b" * 2001},
    {"contact": "not-an-email"}, {"contact": "12345"}, {"contact": "+1 555 abc 1234"},
    {"contact": "1" * 16}, {"title": 123},
])
def test_validation(client, overrides):
    assert _submit(client, **overrides).status_code == 400
    assert db_manager.get_all_feature_requests() == []


@pytest.mark.parametrize("contact", ["", "me@example.com", "+972 54-123-4567", "(555) 123.4567",
                                     "0541234567"])
def test_contact_is_optional_email_or_phone(client, contact):
    res = _submit(client, contact=contact)
    assert res.status_code == 201
    assert db_manager.get_feature_request(res.get_json()["id"])["contact"] == (contact or None)


def test_bug_page_link_prefilled_from_referrer(client):
    ref = "http://localhost/created_route?route=abc%2Bdef"
    html = client.get("/feature_requests", headers={"Referer": ref}).get_data(as_text=True)
    assert 'value="http://localhost/created_route?route=abc%2Bdef"' in html
    # Other sites are not prefilled
    html = client.get("/feature_requests", headers={"Referer": "https://evil.example/x"}).get_data(as_text=True)
    assert "evil.example" not in html


def test_form_has_no_placeholder_text(client):
    html = client.get("/feature_requests").get_data(as_text=True)
    form = html[html.index('id="fr-form"'):html.index("</form>")]
    assert "placeholder=" not in form


def test_old_contact_email_column_is_migrated(tmp_path, monkeypatch):
    import sqlite3
    from database.db_manager import DBManager
    db_file = tmp_path / "old.db"
    conn = sqlite3.connect(db_file)
    conn.execute("CREATE TABLE feature_requests (id INTEGER PRIMARY KEY, category TEXT, title TEXT, "
                 "body TEXT, page TEXT, contact_email TEXT, user_agent TEXT, submitter_id TEXT, "
                 "status TEXT, created_at INTEGER, updated_at INTEGER)")
    conn.execute("INSERT INTO feature_requests (category, title, contact_email, status) "
                 "VALUES ('website_bug', 'Old', 'old@example.com', 'new')")
    conn.commit()
    conn.close()
    monkeypatch.setenv("SQLITE_DB_DIR", str(tmp_path))
    monkeypatch.setenv("SQLITE_DB_NAME", "old.db")
    DBManager().init_db()
    conn = sqlite3.connect(db_file)
    assert conn.execute("SELECT contact FROM feature_requests").fetchone()[0] == "old@example.com"
    conn.close()


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


def test_upvote_button_is_labelled(client):
    rid = _submit(client).get_json()["id"]
    _set_status(rid, "open")
    html = client.get("/feature_requests").get_data(as_text=True)
    assert '<span class="fr-vote-label">Upvote</span>' in html
    _vote(client, rid)
    html = client.get("/feature_requests").get_data(as_text=True)
    assert '<span class="fr-vote-label">Upvoted</span>' in html


def _cast(client, request_id, vote):
    return client.post(f"/api/feature_requests/{request_id}/vote", json={"vote": vote},
                       headers={"X-CSRF-Token": get_csrf(client)})


def test_dislike_switch_and_undo(client):
    rid = _submit(client).get_json()["id"]
    _set_status(rid, "open")
    other = appmod.app.test_client()
    _cast(other, rid, "up")

    data = _cast(client, rid, "down").get_json()
    assert (data["vote"], data["votes"], data["dislikes"]) == ("down", 1, 1)
    data = _cast(client, rid, "up").get_json()       # switch: dislike -> upvote, never both
    assert (data["votes"], data["dislikes"]) == (2, 0)
    data = _cast(client, rid, "down").get_json()
    assert (data["votes"], data["dislikes"]) == (1, 1)
    data = _cast(client, rid, "none").get_json()     # undo
    assert (data["vote"], data["votes"], data["dislikes"]) == ("none", 1, 0)
    assert _cast(client, rid, "sideways").status_code == 400


def test_dislike_button_state_and_sorting(client):
    liked = _submit(client, title="Liked idea").get_json()["id"]
    disliked = _submit(client, title="Disliked idea").get_json()["id"]
    for rid in (liked, disliked):
        _set_status(rid, "open")
    _cast(client, disliked, "down")
    html = client.get("/feature_requests").get_data(as_text=True)
    assert '<span class="fr-vote-label">Disliked</span>' in html
    assert '<span class="fr-vote-label">Dislike</span>' in html
    # upvotes minus dislikes: 0 beats -1
    assert html.index("Liked idea") < html.index("Disliked idea")


def test_admin_sees_dislikes(client, admin_client):
    rid = _submit(client).get_json()["id"]
    _set_status(rid, "open")
    _cast(client, rid, "down")
    assert "0 upvotes, 1 dislike" in admin_client.get("/feature_requests/admin").get_data(as_text=True)


def test_old_votes_table_gets_value_column(tmp_path, monkeypatch):
    import sqlite3
    from database.db_manager import DBManager
    db_file = tmp_path / "old_votes.db"
    conn = sqlite3.connect(db_file)
    conn.execute("CREATE TABLE feature_votes (request_id INTEGER NOT NULL, voter_id TEXT NOT NULL, "
                 "created_at INTEGER NOT NULL, PRIMARY KEY (request_id, voter_id))")
    conn.execute("INSERT INTO feature_votes VALUES (1, 'old-voter', 1)")
    conn.commit()
    conn.close()
    monkeypatch.setenv("SQLITE_DB_DIR", str(tmp_path))
    monkeypatch.setenv("SQLITE_DB_NAME", "old_votes.db")
    DBManager()
    conn = sqlite3.connect(db_file)
    assert conn.execute("SELECT value FROM feature_votes").fetchone()[0] == 1  # old votes = upvotes
    conn.close()


def test_bugs_cannot_be_voted(client):
    rid = _submit(client, category="website_bug").get_json()["id"]
    _set_status(rid, "open")
    assert _vote(client, rid).status_code == 404
    assert _cast(client, rid, "down").status_code == 404


def test_donate_not_in_navbar_but_page_kept(client):
    assert 'href="/donate"' not in client.get("/").get_data(as_text=True)
    assert client.get("/donate").status_code == 200


def test_admin_off_without_password(client, monkeypatch):
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    assert client.get("/feature_requests/admin").status_code == 404
    assert client.get("/admin").status_code == 404


def test_admin_is_hidden_but_reachable_at_slash_admin(client, admin_password):
    res = client.get("/admin")
    assert res.status_code == 302 and res.location.endswith("/feature_requests/admin")
    for page in ("/", "/feature_requests"):
        assert "/admin" not in client.get(page).get_data(as_text=True)  # never linked
    assert 'name="robots" content="noindex"' in client.get("/feature_requests/admin").get_data(as_text=True)


def test_admin_requires_login(client, admin_password):
    html = client.get("/feature_requests/admin").get_data(as_text=True)
    assert 'name="password"' in html
    assert "<title>Admin" in html and "Admin password" in html
    assert "Organizer" not in html and "Feature Requests - Admin" not in html
    res = client.post("/feature_requests/admin/1", data={"status": "open", "_csrf_token": get_csrf(client)})
    assert res.status_code == 403

    client.post("/feature_requests/admin", data={"password": "wrong", "_csrf_token": get_csrf(client)})
    assert 'name="password"' in client.get("/feature_requests/admin").get_data(as_text=True)


def test_admin_sees_private_info_and_approves(client, admin_client):
    rid = _submit(client, category="website_bug", title="Bug X", contact="+972 54-123-4567",
                  page="https://jugglefit.com/run_route?route=x").get_json()["id"]
    _submit(client, category="website_bug", title="Bug Y", page="javascript:alert(1)")
    html = admin_client.get("/feature_requests/admin").get_data(as_text=True)
    assert "Bug X" in html and 'href="tel:+97254-123-4567"' in html
    assert 'href="https://jugglefit.com/run_route?route=x"' in html
    assert 'href="javascript:' not in html  # unsafe links are shown as text only

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
