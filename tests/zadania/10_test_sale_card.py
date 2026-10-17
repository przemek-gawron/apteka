from playwright.sync_api import Page, expect

from zadania.helpers import login


# def test_sale_card(page: Page):
#     login(page)
#     kasa_link=page.get_by_role("link", name="Kasa").click()
#     page.get_by_label("Lek",exact=True).select_option("30")
#     page.get_by_role("textbox", name="Ilość").fill("2")
#     page.get_by_role("button", name="Dodaj do koszyka").click()
#     expect(page.get_by_test_id ("cart-total")).to_have_text("22,98 zł")
#     page.get_by_role("radio", name="Karta").click()
#     page.get_by_role("button", name="Zakończ sprzedaż").click()
#     expect(page.get_by_test_id("receipt-total")).to_have_text("22,98 zł")
#     expect(page.get_by_test_id("receipt-payment")).to_have_text("Karta")
#     page.get_by_role("link", name="Leki", exact=True).click()
#     szukaj_input=page.get_by_placeholder("Nazwa lub substancja czynna").fill("Rutinoscorbin")
#     page.get_by_role("button", name="Filtruj").click()
#     rutinoscorbin_link=page.get_by_role("link", name="Rutinoscorbin").click()
#     expect(page.get_by_test_id("detail-stock")).to_have_text("148 szt.")
#
#     # W kasie wybierz lek Rutinoscorbin (wartość 30), wpisz ilość „2” i kliknij „Dodaj do koszyka”.
#     # ✔ cart-total: „22,98 zł”
#     # Zaznacz „Karta” i kliknij „Zakończ sprzedaż”.
#     # ✔ receipt-total: „22,98 zł”
#     # ✔ receipt-payment: „Karta”
#     # ➕ Bonus: /leki/30 → stan „148 szt.”
#     pass
