from playwright.sync_api import Page, expect


def login(page: Page, username: str, password: str):
    page.goto("/login")
    page.get_by_label("Login").fill(username)
    page.get_by_label("Hasło").fill(password)
    page.get_by_role("button", name="Zaloguj się").click()


def test_logowanie_kierownika(page: Page):
    login(page, "kierownik", "kierownik123")

    expect(page).to_have_url("/")
    expect(page.get_by_role("heading", name="Pulpit")).to_be_visible()
    expect(page.get_by_test_id("user-name")).to_have_text("Anna Nowak")
    expect(page.get_by_test_id("user-role")).to_have_text("kierownik")
