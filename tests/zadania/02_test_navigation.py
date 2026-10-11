from playwright.sync_api import Page, expect

from zadania.helpers import login


def test_navigation(page: Page):
    login(page)

    page.get_by_role("link", name="Leki").click()
    expect(page.get_by_role("heading", name="Leki")).to_be_visible()

    page.get_by_role("link", name="Kasa").click()
    expect(page.get_by_role("heading", name="Kasa")).to_be_visible()

    page.get_by_role("link", name="Sprzedaż", exact=True).click()
    expect(page.get_by_role("heading", name="Historia sprzedaży")).to_be_visible()

    page.get_by_role("link", name="Pulpit").click()
    expect(page.get_by_role("heading", name="Pulpit")).to_be_visible()
