from tests.unit.conftest import get_csrf


# --- create ---------------------------------------------------------------
def test_create_is_disabled_without_admin_password(client, monkeypatch, route_payload):
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    res = client.post("/api/finals", json={"password": "x", "route": route_payload,
                                           "competitor_count": 2},
                      headers={"X-CSRF-Token": get_csrf(client)})
    assert res.status_code == 404


def test_create_rejects_wrong_password(client, create_final):
    assert create_final(client, password="wrong").status_code == 403


def test_create_requires_csrf(client, admin_password, route_payload):
    res = client.post("/api/finals", json={"password": admin_password, "route": route_payload,
                                           "competitor_count": 2})
    assert res.status_code == 403


def test_create_validates_input(client, create_final):
    assert create_final(client, route="not-a-route").status_code == 400
    assert create_final(client, competitor_count=0).status_code == 400
    assert create_final(client, competitor_count=31).status_code == 400
    assert create_final(client, competitor_count="3").status_code == 400


def test_create_fills_missing_names(client, create_final):
    data = create_final(client, competitor_count=3, names=["  Ann  ", ""]).get_json()
    state = client.get(f"/api/finals/{data['final_id']}/state").get_json()
    assert [c["name"] for c in state["competitors"]] == ["Ann", "Competitor 2", "Competitor 3"]


def test_creator_session_is_admin(client, create_final):
    data = create_final(client).get_json()
    assert data["resumed"] is False
    assert data["live_url"].startswith("/live_event?route=")
    assert f"final={data['final_id']}" in data["live_url"]
    res = client.post(f"/api/finals/{data['final_id']}/start", json={},
                      headers={"X-CSRF-Token": get_csrf(client)})
    assert res.status_code == 200


# --- resume + start over ----------------------------------------------------
def test_password_resumes_live_final_on_another_device(admin_final, create_final):
    import app as appmod
    competitor_id = admin_final.state()["competitors"][0]["id"]
    admin_final.post("start")
    admin_final.post("move", competitor_id=competitor_id, to_stage=2)

    phone = appmod.app.test_client()
    res = create_final(phone, competitor_count=7)
    assert res.status_code == 200
    data = res.get_json()
    assert data["resumed"] is True
    assert data["final_id"] == admin_final.final_id
    # Progress is kept and the phone is now admin too.
    assert admin_final.state()["competitors"][0]["stage"] == 2
    assert len(admin_final.state()["competitors"]) == 3
    res = phone.post(f"/api/finals/{admin_final.final_id}/move",
                     json={"competitor_id": competitor_id, "to_stage": 3},
                     headers={"X-CSRF-Token": get_csrf(phone)})
    assert res.status_code == 200


def test_resume_needs_the_password(admin_final, create_final):
    import app as appmod
    assert create_final(appmod.app.test_client(), password="wrong").status_code == 403


def test_start_over_keeps_names_and_resets_progress(admin_final, audience):
    competitor_id = admin_final.state()["competitors"][0]["id"]
    admin_final.post("start")
    admin_final.post("move", competitor_id=competitor_id, to_stage=2)

    res = admin_final.post("restart")
    assert res.status_code == 201
    new_id = res.get_json()["final_id"]
    assert new_id != admin_final.final_id
    assert admin_final.state()["status"] == "ended"

    new_state = admin_final.client.get(f"/api/finals/{new_id}/state").get_json()
    assert [c["name"] for c in new_state["competitors"]] == ["Ann", "Ben", "Cat"]
    assert all(c["stage"] == 0 and c["started_at"] is None for c in new_state["competitors"])
    # The admin session carries over to the new final.
    res = admin_final.client.post(f"/api/finals/{new_id}/start", json={},
                                  headers={"X-CSRF-Token": admin_final.csrf})
    assert res.status_code == 200


def test_start_over_needs_admin(audience):
    assert audience.post("restart").status_code == 403


# --- admin link -----------------------------------------------------------
def test_admin_link_redirects_to_live_event_without_token(client, create_final):
    data = create_final(client).get_json()
    token = data["admin_url"].rsplit("/", 1)[1]
    res = client.get(data["admin_url"])
    assert res.status_code == 302
    assert res.location.startswith("/live_event?route=")
    assert f"final={data['final_id']}" in res.location
    assert token not in res.location


def test_bad_admin_token_is_rejected(client, create_final):
    data = create_final(client).get_json()
    assert client.get(f"/final/admin/{data['final_id']}/wrong-token").status_code == 404
    assert client.get("/final/admin/no-such-final/token").status_code == 404


# --- admin actions --------------------------------------------------------
def test_admin_actions_need_admin_session(audience):
    competitor_id = audience.state()["competitors"][0]["id"]
    assert audience.post("start").status_code == 403
    assert audience.post("move", competitor_id=competitor_id, to_stage=1).status_code == 403
    assert audience.post("rename", competitor_id=competitor_id, name="X").status_code == 403
    assert audience.post("end").status_code == 403
    assert audience.client.get(f"/api/finals/{audience.final_id}/log.csv").status_code == 403


def test_move_requires_start(admin_final):
    competitor_id = admin_final.state()["competitors"][0]["id"]
    assert admin_final.post("move", competitor_id=competitor_id, to_stage=1).status_code == 409


def test_move_validates_stage(admin_final):
    state = admin_final.state()
    competitor_id = state["competitors"][0]["id"]
    admin_final.post("start")
    assert admin_final.post("move", competitor_id=competitor_id, to_stage=-1).status_code == 400
    assert admin_final.post("move", competitor_id=competitor_id,
                            to_stage=state["route_length"] + 1).status_code == 400
    assert admin_final.post("move", competitor_id=competitor_id,
                            to_stage=state["route_length"]).status_code == 200
    assert admin_final.post("move", competitor_id=999999, to_stage=1).status_code == 400


def test_move_is_visible_to_audience(admin_final, audience):
    competitor_id = admin_final.state()["competitors"][1]["id"]
    admin_final.post("start")
    assert admin_final.post("move", competitor_id=competitor_id, to_stage=2).status_code == 200
    stages = {c["id"]: c["stage"] for c in audience.state()["competitors"]}
    assert stages[competitor_id] == 2


def test_finished_at_is_reported(admin_final):
    state = admin_final.state()
    competitor_id = state["competitors"][0]["id"]
    admin_final.post("start")
    admin_final.post("move", competitor_id=competitor_id, to_stage=state["route_length"])
    competitor = admin_final.state()["competitors"][0]
    assert competitor["finished_at"] is not None
    admin_final.post("move", competitor_id=competitor_id, to_stage=state["route_length"] - 1)
    assert admin_final.state()["competitors"][0]["finished_at"] is None


def test_rename(admin_final, audience):
    competitor_id = admin_final.state()["competitors"][0]["id"]
    assert admin_final.post("rename", competitor_id=competitor_id, name="  Dana ").status_code == 200
    assert audience.state()["competitors"][0]["name"] == "Dana"
    assert admin_final.post("rename", competitor_id=competitor_id, name=" ").status_code == 400


def test_state_since_returns_204_when_unchanged(admin_final, audience):
    version = audience.state()["version"]
    url = f"/api/finals/{audience.final_id}/state?since={version}"
    assert audience.client.get(url).status_code == 204
    admin_final.post("start")
    assert audience.client.get(url).status_code == 200


def test_state_of_unknown_final_is_404(client):
    assert client.get("/api/finals/nope/state").status_code == 404


def test_ended_final_rejects_moves_but_keeps_log(admin_final):
    competitor_id = admin_final.state()["competitors"][0]["id"]
    admin_final.post("start")
    assert admin_final.post("end").status_code == 200
    assert admin_final.state()["status"] == "ended"
    assert admin_final.post("move", competitor_id=competitor_id, to_stage=1).status_code == 409
    assert admin_final.client.get(f"/api/finals/{admin_final.final_id}/log.csv").status_code == 200


def test_client_clock_far_off_is_ignored(admin_final):
    from database.db_manager import db_manager
    competitor_id = admin_final.state()["competitors"][0]["id"]
    admin_final.post("start", client_at=1)
    admin_final.post("move", competitor_id=competitor_id, to_stage=1, client_at=True)
    events = db_manager.get_final_events(admin_final.final_id)
    assert all(e["client_at"] is None for e in events)


# --- delete (simulation cleanup) -------------------------------------------
def test_delete_only_works_for_test_finals(admin_final, create_final, real_route):
    import dataclasses
    assert admin_final.post("delete").status_code == 403

    client = admin_final.client
    other_route = dataclasses.replace(real_route, name="Simulation route").serialize()
    data = create_final(client, route=other_route, test=True).get_json()
    res = client.post(f"/api/finals/{data['final_id']}/delete",
                      headers={"X-CSRF-Token": get_csrf(client)})
    assert res.status_code == 200
    assert client.get(f"/api/finals/{data['final_id']}/state").status_code == 404
