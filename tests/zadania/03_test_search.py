from playwright.sync_api import Page, expect

from zadania.helpers import login


def test_search(page: Page):
    login (page)
    leki= page.get_by_role("link", name="Leki").click()
    szukaj_input= page.get_by_role("searchbox", name="Szukaj").fill("para")
    filtruj_button=page.get_by_role("button", name="Filtruj").click()
    expect(page.get_by_test_id("drugs-count")).to_have_text("Znaleziono: 3")
    
