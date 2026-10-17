from playwright.sync_api import Page, expect

from zadania.helpers import login


def test_edit_price(page: Page):
    login(page)
    page.get_by_role("link", name="Leki", exact=True).click()
    page.get_by_role("link", name="Apap").click()
    page.get_by_role("link", name="Edytuj").click()
    page.get_by_placeholder("12,50").fill("13,49")
    page.get_by_role("button", name="Zapisz zmiany").click()
    expect(page.get_by_test_id("flash-success")).to_have_text("Zapisano zmiany: Apap.")
    expect(page.get_by_test_id("detail-price")).to_have_text("13,49 zł")

    # Wejdź na /leki/1 (Apap), kliknij „Edytuj” i zmień cenę na „13,49”. Zapisz.
    # ✔ flash-success: „Zapisano zmiany: Apap.”
    # ✔ detail-price: „13,49 zł”
    pass
