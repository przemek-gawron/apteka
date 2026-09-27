import pytest
from playwright.sync_api import Page, expect

from pages import LoginPage


def test_login_success(page: Page):
    login_page = LoginPage(page)
    login_page.goto()
    login_page.login("farmaceuta", "farmaceuta123")

    expect(page).to_have_url("/")  # base_url + "/"
    expect(page.get_by_role("heading", name="Pulpit")).to_be_visible()
    expect(page.get_by_test_id("user-name")).to_have_text("Jan Kowalski")


@pytest.mark.parametrize(
    "username, password, message",
    [
        ("farmaceuta", "zlehaslo", "Nieprawidłowy login lub hasło."),
        ("nieistnieje", "farmaceuta123", "Nieprawidłowy login lub hasło."),
        ("", "", "Podaj login i hasło."),
    ],
)
def test_login_invalid(page: Page, username, password, message):
    login_page = LoginPage(page)
    login_page.goto()
    login_page.login(username, password)

    expect(login_page.error).to_have_text(message)
    expect(page).to_have_url("/login")


def test_redirects_to_login_when_not_logged_in(page: Page):
    page.goto("/leki/")

    expect(page).to_have_url("/login?next=/leki/")


def test_logout(farmaceuta_page: Page):
    farmaceuta_page.goto("/")
    farmaceuta_page.get_by_role("button", name="Wyloguj").click()

    expect(farmaceuta_page.get_by_test_id("flash-info")).to_have_text("Wylogowano.")
    farmaceuta_page.goto("/")
    expect(farmaceuta_page).to_have_url("/login?next=/")
