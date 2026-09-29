"""Fixtures for the in-process app tests.

The DB singleton and the trick registry initialize at import time, so the
environment must point at a temp DB *before* ``app`` is imported.
"""
import os
import re
import tempfile
from dataclasses import dataclass
from typing import Any, Dict

os.environ["SQLITE_DB_DIR"] = tempfile.mkdtemp(prefix="jugglefit-test-db-")
os.environ["FLASK_ENV"] = "development"

import pytest  # noqa: E402

import app as appmod  # noqa: E402
from database.db_manager import db_manager  # noqa: E402
from hardcoded_database.events.past_events.Y2025.EJC2025 import EJC2025  # noqa: E402

ADMIN_PASSWORD = "test-password"
_CSRF_RE = re.compile(r'<meta name="csrf-token" content="([^"]+)"')


def get_csrf(client) -> str:
    html = client.get("/").get_data(as_text=True)
    return _CSRF_RE.search(html).group(1)


@dataclass
class FinalClient:
    """A test client bound to one final, with its CSRF token."""
    client: Any
    final_id: str
    csrf: str

    def post(self, action: str, **body):
        return self.client.post(f"/api/finals/{self.final_id}/{action}", json=body,
                                headers={"X-CSRF-Token": self.csrf})

    def state(self) -> Dict[str, Any]:
        return self.client.get(f"/api/finals/{self.final_id}/state").get_json()


@pytest.fixture
def client():
    return appmod.app.test_client()


@pytest.fixture
def real_route():
    return EJC2025.results[0].route


@pytest.fixture
def route_payload(real_route):
    return real_route.serialize()


@pytest.fixture(autouse=True)
def clean_finals():
    yield
    with db_manager.cursor(commit=True) as cur:
        cur.execute("DELETE FROM finals")


@pytest.fixture
def admin_password(monkeypatch):
    monkeypatch.setenv("ADMIN_PASSWORD", ADMIN_PASSWORD)
    return ADMIN_PASSWORD


@pytest.fixture
def create_final(admin_password, route_payload):
    """create_final(client, **overrides) -> response of POST /api/finals"""
    def _create(client, **overrides):
        body = {"password": admin_password, "route": route_payload, "competitor_count": 3}
        body.update(overrides)
        return client.post("/api/finals", json=body, headers={"X-CSRF-Token": get_csrf(client)})
    return _create


@pytest.fixture
def admin_final(create_final):
    """A final created by, and administered from, a fresh client."""
    client = appmod.app.test_client()
    data = create_final(client, names=["Ann", "Ben", "Cat"]).get_json()
    client.get(data["admin_url"])
    return FinalClient(client, data["final_id"], get_csrf(client))


@pytest.fixture
def audience(admin_final):
    """A second client on the same final, with no admin session."""
    client = appmod.app.test_client()
    return FinalClient(client, admin_final.final_id, get_csrf(client))
