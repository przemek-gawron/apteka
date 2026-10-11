from playwright.sync_api import Page, expect

from zadania.helpers import login


def test_filter_category(page: Page):
    login(page)
    page.get_by_role("link", name="Leki", exact=True).click()
    page.get_by_label("Kategoria").select_option("Antybiotyki")
    page.get_by_role("button", name="Filtruj").click()

    expect(page.get_by_test_id("drug-row")).to_have_count(3)
    expect(page.locator(".drug-name")).to_have_text(["Amotaks", "Augmentin", "Klacid"])
