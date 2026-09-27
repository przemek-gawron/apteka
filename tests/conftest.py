import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest
from playwright.sync_api import APIRequestContext, Browser, Page, Playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent

USERS = {
    "kierownik": "kierownik123",
    "farmaceuta": "farmaceuta123",
}


def _wait_for_server(url, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url + "/login", timeout=1)
            return
        except OSError:
            time.sleep(0.2)
    raise RuntimeError(f"Serwer {url} nie wystartował w {timeout} s")


@pytest.fixture(scope="session")
def base_url(tmp_path_factory):
    """Adres aplikacji. Jeśli ustawisz BASE_URL, testy użyją już działającego serwera
    (musi mieć APP_ENV=test). W przeciwnym razie serwer startuje automatycznie."""
    if os.environ.get("BASE_URL"):
        yield os.environ["BASE_URL"].rstrip("/")
        return

    port = os.environ.get("TEST_PORT", "5055")
    env = dict(
        os.environ,
        APP_ENV="test",
        PORT=port,
        RESET_DB="1",
        STATS_DELAY_MS="300",
        DATABASE=str(tmp_path_factory.mktemp("db") / "apteka-test.db"),
    )
    server = subprocess.Popen([sys.executable, "run.py"], cwd=PROJECT_ROOT, env=env)
    url = f"http://127.0.0.1:{port}"
    try:
        _wait_for_server(url)
        yield url
    finally:
        server.terminate()
        server.wait(timeout=5)


@pytest.fixture(autouse=True)
def reset_db(playwright: Playwright, base_url):
    """Każdy test zaczyna ze świeżą bazą (te same dane startowe)."""
    ctx = playwright.request.new_context(base_url=base_url)
    response = ctx.post("/api/test/reset")
    assert response.ok, "Reset bazy nie działa — czy serwer ma APP_ENV=test?"
    ctx.dispose()


@pytest.fixture(scope="session")
def auth_states(playwright: Playwright, base_url, tmp_path_factory):
    """Loguje każdego użytkownika RAZ przez API i zapisuje cookies do pliku (storage_state).
    Dzięki temu testy nie muszą za każdym razem klikać w formularz logowania."""
    folder = tmp_path_factory.mktemp("auth")
    states = {}
    for username, password in USERS.items():
        ctx = playwright.request.new_context(base_url=base_url)
        response = ctx.post("/api/login", data={"username": username, "password": password})
        assert response.ok, f"Nie udało się zalogować jako {username}"
        states[username] = folder / f"{username}.json"
        ctx.storage_state(path=states[username])
        ctx.dispose()
    return states


def _page_as(browser: Browser, base_url, state_file):
    context = browser.new_context(base_url=base_url, storage_state=state_file, locale="pl-PL")
    return context, context.new_page()


@pytest.fixture
def farmaceuta_page(browser: Browser, base_url, auth_states) -> Page:
    context, page = _page_as(browser, base_url, auth_states["farmaceuta"])
    yield page
    context.close()


@pytest.fixture
def kierownik_page(browser: Browser, base_url, auth_states) -> Page:
    context, page = _page_as(browser, base_url, auth_states["kierownik"])
    yield page
    context.close()


@pytest.fixture
def api(playwright: Playwright, base_url) -> APIRequestContext:
    """Klient REST API zalogowany jako kierownik."""
    ctx = playwright.request.new_context(base_url=base_url)
    ctx.post("/api/login", data={"username": "kierownik", "password": USERS["kierownik"]})
    yield ctx
    ctx.dispose()
