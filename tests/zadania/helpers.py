from playwright.sync_api import Page, expect


def login(page: Page, username="kierownik", password="kierownik123"):
    page.goto("/login")
    page.get_by_label("Login").fill(username)
    page.get_by_label("Hasło").fill(password)
    page.get_by_role("button", name="Zaloguj się").click()
    expect(page.get_by_role("heading", name="Pulpit")).to_be_visible()
