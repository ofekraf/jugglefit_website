import csv
import io

from pylib.utils.final_log import CSV_HEADER, FINISHED_LABEL, build_log_rows, finish_times, to_csv

TRICKS = ["t1", "t2", "t3"]
COMPETITORS = [{"id": 1, "name": "Ann"}, {"id": 2, "name": "Ben"}]


def _event(competitor_id, from_stage, to_stage, at, client_at=None):
    return {"competitor_id": competitor_id, "from_stage": from_stage, "to_stage": to_stage,
            "at": at, "client_at": client_at}


def test_rows_and_durations_use_client_time():
    events = [
        _event(1, None, 0, at=10_000, client_at=0),
        _event(1, 0, 1, at=99_000, client_at=5_000),   # sent late; client time is used
        _event(1, 1, 2, at=99_500, client_at=12_500),
        _event(1, 2, 3, at=99_900, client_at=20_000),
    ]
    rows = build_log_rows(events, COMPETITORS, TRICKS)
    assert [(r[0], r[1], r[2], r[5]) for r in rows] == [
        ("Ann", "1", "t1", "5.000"),
        ("Ann", "2", "t2", "7.500"),
        ("Ann", "3", "t3", "7.500"),
        ("Ann", "", FINISHED_LABEL, ""),
    ]
    assert rows[0][3] == "1970-01-01T00:00:00.000+00:00"


def test_take_back_is_a_later_re_entry():
    events = [
        _event(2, None, 0, at=0),
        _event(2, 0, 1, at=1_000),
        _event(2, 1, 0, at=2_000),   # admin took Ben back
        _event(2, 0, 1, at=4_000),
    ]
    rows = build_log_rows(events, COMPETITORS, TRICKS)
    assert [(r[1], r[5]) for r in rows] == [("1", "1.000"), ("2", "1.000"), ("1", "2.000"), ("2", "")]
    assert all(r[0] == "Ben" for r in rows)


def test_competitor_without_events_has_no_rows():
    assert build_log_rows([], COMPETITORS, TRICKS) == []


def test_finish_times_follow_the_latest_move():
    events = [_event(1, 2, 3, at=100), _event(2, 2, 3, at=200), _event(2, 3, 2, at=300)]
    assert finish_times(events, route_length=3) == {1: 100}


def test_to_csv_has_header():
    parsed = list(csv.reader(io.StringIO(to_csv([["Ann", "1", "t, with comma", "", "", ""]]))))
    assert parsed[0] == CSV_HEADER
    assert parsed[1][2] == "t, with comma"
