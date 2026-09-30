from database.db_manager import db_manager


def _create(final_id, route_key="key-1", names=("A", "B"), now_ms=1000, is_test=False):
    db_manager.create_final(final_id=final_id, route_key=route_key, route_payload="payload",
                            admin_token_hash="hash", names=list(names), now_ms=now_ms,
                            is_test=is_test)


def test_create_and_get_active_final():
    _create("f1")
    active = db_manager.get_active_final_by_route_key("key-1")
    assert active["id"] == "f1"
    assert [c["name"] for c in db_manager.get_final_competitors("f1")] == ["A", "B"]
    assert db_manager.get_active_final_by_route_key("other-key") is None


def test_new_final_for_same_route_ends_the_old_one():
    _create("f1")
    _create("f2", now_ms=2000)
    assert db_manager.get_active_final_by_route_key("key-1")["id"] == "f2"
    old = db_manager.get_final("f1")
    assert old["status"] == "ended"
    assert old["ended_at"] == 2000


def test_move_logs_one_event_and_bumps_version():
    _create("f1")
    competitor = db_manager.get_final_competitors("f1")[0]
    db_manager.start_final("f1", now_ms=1500)
    version_before = db_manager.get_final("f1")["version"]

    version = db_manager.move_competitor("f1", competitor["id"], 1, now_ms=2000, client_at=1990)

    assert version == version_before + 1
    events = db_manager.get_final_events("f1")
    assert events[-1]["from_stage"] == 0
    assert events[-1]["to_stage"] == 1
    assert events[-1]["at"] == 2000
    assert events[-1]["client_at"] == 1990
    assert db_manager.get_final_competitors("f1")[0]["stage"] == 1


def test_move_to_same_stage_is_not_logged():
    _create("f1")
    competitor = db_manager.get_final_competitors("f1")[0]
    events_before = len(db_manager.get_final_events("f1"))
    version_before = db_manager.get_final("f1")["version"]
    assert db_manager.move_competitor("f1", competitor["id"], 0, now_ms=2000) == version_before
    assert len(db_manager.get_final_events("f1")) == events_before


def test_move_rejects_competitor_of_another_final():
    _create("f1")
    _create("f2", route_key="key-2")
    other = db_manager.get_final_competitors("f2")[0]
    assert db_manager.move_competitor("f1", other["id"], 1, now_ms=2000) is None


def test_start_one_then_all_logs_each_start_once():
    _create("f1", names=("A", "B", "C"))
    a, b, c = db_manager.get_final_competitors("f1")
    db_manager.start_final("f1", now_ms=1000, competitor_id=a["id"])
    db_manager.start_final("f1", now_ms=2000)
    started = {x["id"]: x["started_at"] for x in db_manager.get_final_competitors("f1")}
    assert started == {a["id"]: 1000, b["id"]: 2000, c["id"]: 2000}
    assert len(db_manager.get_final_events("f1")) == 3
    assert db_manager.get_final("f1")["started_at"] == 1000


def test_end_final():
    _create("f1")
    db_manager.end_final("f1", now_ms=5000)
    assert db_manager.get_final("f1")["status"] == "ended"
    assert db_manager.get_active_final_by_route_key("key-1") is None


def test_delete_only_removes_test_finals():
    _create("real")
    _create("sim", route_key="key-2", is_test=True)
    assert db_manager.delete_test_final("real") is False
    assert db_manager.delete_test_final("sim") is True
    assert db_manager.get_final("real") is not None
    assert db_manager.get_final("sim") is None
    assert db_manager.get_final_competitors("sim") == []
