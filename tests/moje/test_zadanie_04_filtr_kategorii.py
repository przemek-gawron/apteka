from playwright.sync_api import Page, expect


def login(page: Page, username="farmaceuta", password="farmaceuta123"):
    page.goto("/login")
    page.get_by_label("Login").fill(username)
    page.get_by_label("Hasło").fill(password)
    page.get_by_role("button", name="Zaloguj się").click()
    expect(page.get_by_role("heading", name="Pulpit")).to_be_visible()


def test_filtr_kategorii(page: Page):
    login(page)
    page.goto("/leki/")

    page.get_by_label("Kategoria").select_option("Antybiotyki")
    page.get_by_role("button", name="Filtruj").click()

    expect(page.get_by_test_id("drug-row")).to_have_count(3)
    expect(page.locator(".drug-name")).to_have_text(["Amotaks", "Augmentin", "Klacid"])
