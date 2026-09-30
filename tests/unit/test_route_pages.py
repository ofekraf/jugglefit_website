"""Regression checks for the URLs printed on QR codes (CLAUDE.md hard rule 1)."""
import pytest

ROUTE_PAGES = ["/created_route", "/run_route", "/live_event"]


@pytest.mark.parametrize("path", ROUTE_PAGES + ["/build_route"])
def test_route_pages_render_with_real_route(client, route_payload, path):
    assert client.get(path, query_string={"route": route_payload}).status_code == 200


@pytest.mark.parametrize("path", ROUTE_PAGES)
def test_route_pages_redirect_without_route(client, path):
    res = client.get(path)
    assert res.status_code == 302
    assert res.location.startswith("/build_route")


@pytest.mark.parametrize("path", ROUTE_PAGES)
def test_route_pages_redirect_on_bad_route(client, path):
    res = client.get(path, query_string={"route": "garbage"})
    assert res.status_code == 302
    assert res.location.startswith("/build_route")


def test_live_event_without_final_keeps_local_tracker(client, route_payload):
    html = client.get("/live_event", query_string={"route": route_payload}).get_data(as_text=True)
    assert 'id="competitorListContainer"' in html
    assert "data-organizer-open" in html
    assert 'id="organizer-count"' in html
    assert 'id="final-grid"' not in html


def test_created_route_has_organizer_dialog(client, route_payload):
    html = client.get("/created_route", query_string={"route": route_payload}).get_data(as_text=True)
    assert "Organizer: Run this live event" in html
    assert 'id="organizer-dialog"' in html
    # No final yet: the dialog asks for the competitors too.
    assert 'id="organizer-count"' in html


def test_organizer_dialog_resumes_when_final_is_live(client, route_payload, admin_final):
    html = client.get("/created_route", query_string={"route": route_payload}).get_data(as_text=True)
    assert "A final is live for this route" in html
    assert 'id="organizer-count"' not in html


def test_banner_follows_active_final(client, route_payload, admin_final):
    page = lambda: client.get("/created_route", query_string={"route": route_payload}).get_data(as_text=True)  # noqa: E731
    assert "The final is live" in page()
    admin_final.post("end")
    assert "The final is live" not in page()


def test_live_event_audience_and_admin_modes(client, route_payload, admin_final):
    audience_html = client.get("/live_event", query_string={"route": route_payload}).get_data(as_text=True)
    assert 'id="final-grid"' in audience_html
    assert "final-admin-bar" not in audience_html
    assert "Organizer: manage this live event" in audience_html

    admin_html = admin_final.client.get("/live_event", query_string={"route": route_payload}).get_data(as_text=True)
    assert "final-admin-bar" in admin_html
    assert 'id="final-restart"' in admin_html
    assert "Organizer: manage this live event" not in admin_html


def test_ended_final_is_shown_by_id(client, route_payload, admin_final):
    admin_final.post("end")
    html = client.get("/live_event", query_string={"route": route_payload,
                                                   "final": admin_final.final_id}).get_data(as_text=True)
    assert 'id="final-grid"' in html
    # Without ?final= the page goes back to the local tracker.
    html = client.get("/live_event", query_string={"route": route_payload}).get_data(as_text=True)
    assert 'id="final-grid"' not in html


def test_final_id_for_another_route_is_ignored(client, admin_final, real_route):
    import dataclasses
    other = dataclasses.replace(real_route, name="Another route").serialize()
    html = client.get("/live_event", query_string={"route": other,
                                                   "final": admin_final.final_id}).get_data(as_text=True)
    assert 'id="final-grid"' not in html
