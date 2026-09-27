from playwright.sync_api import Page, expect


def login(page: Page, username="farmaceuta", password="farmaceuta123"):
    page.goto("/login")
    page.get_by_label("Login").fill(username)
    page.get_by_label("Hasło").fill(password)
    page.get_by_role("button", name="Zaloguj się").click()
    expect(page.get_by_role("heading", name="Pulpit")).to_be_visible()


def test_wyszukiwanie_leku(page: Page):
    login(page)
    page.goto("/leki/")

    page.get_by_label("Szukaj").fill("para")
    page.get_by_role("button", name="Filtruj").click()

    # "para" pasuje do substancji czynnej "paracetamol" w 3 lekach
    expect(page.get_by_test_id("drugs-count")).to_have_text("Znaleziono: 3")
    expect(page.locator(".drug-name")).to_have_text(["Apap", "Gripex Max", "Theraflu Extra"])
