from playwright.sync_api import Page, expect


def login(page: Page, username="farmaceuta", password="farmaceuta123"):
    page.goto("/login")
    page.get_by_label("Login").fill(username)
    page.get_by_label("Hasło").fill(password)
    page.get_by_role("button", name="Zaloguj się").click()
    expect(page.get_by_role("heading", name="Pulpit")).to_be_visible()


def test_nawigacja_po_menu(page: Page):
    login(page)
    menu = page.get_by_test_id("main-nav")

    menu.get_by_role("link", name="Leki").click()
    expect(page.get_by_role("heading", name="Leki")).to_be_visible()

    menu.get_by_role("link", name="Kasa").click()
    expect(page.get_by_role("heading", name="Kasa")).to_be_visible()

    menu.get_by_role("link", name="Sprzedaż", exact=True).click()
    expect(page.get_by_role("heading", name="Historia sprzedaży")).to_be_visible()

    menu.get_by_role("link", name="Pulpit").click()
    expect(page.get_by_role("heading", name="Pulpit")).to_be_visible()
