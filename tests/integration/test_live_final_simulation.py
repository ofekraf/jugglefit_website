"""Fictional live final against a real server (scripts/simulate_final.py).

- local: starts gunicorn like production (2 workers x 4 threads) on a temp
  DB, so SQLite reads/writes across worker processes are covered.
- remote: only when JUGGLEFIT_BASE_URL and JUGGLEFIT_ADMIN_PASSWORD are set,
  e.g. against OCI before an event (also exercises the nginx cache).

Run with: pytest -m integration
"""
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from simulate_final import run_simulation  # noqa: E402

pytestmark = pytest.mark.integration

LOCAL_PASSWORD = "simulation-password"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def local_server(tmp_path, monkeypatch):
    # Talk to the local gunicorn directly, not through an HTTP(S)_PROXY
    # from the environment (corporate or tooling proxies can reject it).
    monkeypatch.setenv("NO_PROXY", "127.0.0.1,localhost")
    monkeypatch.setenv("no_proxy", "127.0.0.1,localhost")
    port = _free_port()
    env = {
        **os.environ,
        "FLASK_ENV": "development",  # production sets Secure cookies, which plain http drops
        "SECRET_KEY": "simulation-secret",
        "SQLITE_DB_DIR": str(tmp_path),
        "ADMIN_PASSWORD": LOCAL_PASSWORD,
        # Print a Python traceback into the log if a worker crashes.
        "PYTHONFAULTHANDLER": "1",
    }
    log_path = tmp_path / "gunicorn.log"
    log_file = open(log_path, "w")
    # macOS system SQLite (/usr/lib/libsqlite3.dylib) segfaults in a forked
    # worker once the parent has used SQLite, which --preload does. Linux
    # (production) is fine, so only drop --preload on macOS; the test still
    # runs 2 worker processes on one DB file.
    preload = [] if sys.platform == "darwin" else ["--preload"]
    proc = subprocess.Popen(
        [sys.executable, "-m", "gunicorn", "--bind", f"127.0.0.1:{port}",
         "--workers", "2", "--threads", "4", *preload, "wsgi:app"],
        cwd=REPO_ROOT, env=env, stdout=log_file, stderr=subprocess.STDOUT,
    )
    base_url = f"http://127.0.0.1:{port}"
    try:
        deadline = time.monotonic() + 30
        while True:
            try:
                if requests.get(f"{base_url}/health", timeout=1).status_code == 200:
                    break
            except requests.RequestException:
                pass
            if proc.poll() is not None or time.monotonic() > deadline:
                pytest.fail(f"gunicorn did not start:\n{log_path.read_text()[-2000:]}")
            time.sleep(0.3)
        yield base_url
    finally:
        proc.terminate()
        proc.wait(timeout=10)
        log_file.close()
        # Shown by pytest when the test fails.
        print(f"--- gunicorn log (tail) ---\n{log_path.read_text()[-3000:]}")


def test_simulated_final_on_local_gunicorn(local_server):
    report = run_simulation(local_server, LOCAL_PASSWORD, competitors=5, viewers=15,
                            tricks=6, duration_s=12, poll_interval_s=1, max_p95_s=4,
                            cleanup=True, seed=1)
    print(report.text())
    assert report.ok, report.text()


@pytest.mark.skipif(not (os.environ.get("JUGGLEFIT_BASE_URL") and os.environ.get("JUGGLEFIT_ADMIN_PASSWORD")),
                    reason="set JUGGLEFIT_BASE_URL and JUGGLEFIT_ADMIN_PASSWORD to run against a deployed server")
def test_simulated_final_on_remote_server():
    report = run_simulation(os.environ["JUGGLEFIT_BASE_URL"], os.environ["JUGGLEFIT_ADMIN_PASSWORD"],
                            competitors=6, viewers=int(os.environ.get("JUGGLEFIT_SIM_VIEWERS", 20)),
                            duration_s=60, cleanup=True)
    print(report.text())
    assert report.ok, report.text()


# Audience sizes at the browser's real poll interval (3 s + up to 1 s jitter).
# No nginx cache here, so every poll reaches gunicorn: this is the worst case
# for the app itself. The dev machine is much faster than the 1 GB OCI VM, so
# confirm on OCI with the remote test before an event.
@pytest.mark.parametrize("viewers", [50, 150, 300])
def test_load_on_local_gunicorn(local_server, viewers):
    report = run_simulation(local_server, LOCAL_PASSWORD, competitors=8, viewers=viewers,
                            tricks=10, duration_s=30, poll_interval_s=3, max_p95_s=8,
                            cleanup=True, seed=2)
    print(report.text())
    assert report.ok, report.text()

