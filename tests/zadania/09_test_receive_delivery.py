from playwright.sync_api import Page, expect

from zadania.helpers import login


# def test_receive_delivery(page: Page):
#     login(page)
#     page.get_by_role("link", name="Leki", exact=True).click()
#     szukaj_input=page.get_by_placeholder("Nazwa lub substancja czynna").fill("sudafed")
#     page.get_by_role("button", name="Filtruj").click()
#     sudafed_link=page.get_by_role("link", name="Sudafed").click()
#     restock_input=page.get_by_role("textbox", name="Ilość [szt.]").fill("50")
#     przyjmij_button=page.get_by_role("button", name="Przyjmij").click()
#     expect(page.get_by_test_id("detail-stock")).to_have_text("53 szt.")
#
#     # Wejdź na /leki/28 (Sudafed, stan 3). W polu „Ilość” wpisz „50” i kliknij „Przyjmij”.
#     # ✔ detail-stock: „53 szt.”
#     pass
