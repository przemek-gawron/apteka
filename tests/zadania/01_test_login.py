from playwright.sync_api import Page, expect


def test_login(page: Page):
    page.goto("http://127.0.0.1:5000/login?next=/")
    login_input = page.get_by_role("textbox", name="Login")
    password_input = page.get_by_role("textbox", name="Hasło")
    login_input.fill("kierownik")
    password_input.fill("kierownik123")
    login_button = page.get_by_role("button", name="Zaloguj się")
    login_button.click()
    anna_nowak = page.get_by_text("Anna Nowak")
    kierownik = page.get_by_text("Kierownik")
    expect(anna_nowak).to_be_visible()
    expect(kierownik).to_be_visible()
