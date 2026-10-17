from playwright.sync_api import Page, expect

from zadania.helpers import login


# def test_add_drug(page: Page):
#     login(page)
#     page.get_by_role("link", name="Leki", exact=True).click()
#     page.get_by_test_id("add-drug").click()
#     input_nazwa=page.get_by_label("Nazwa handlowa").fill("No-Spa")
#     input_substancja_czynna=page.get_by_role("textbox", name="Substancja czynna").fill("drotaweryna")
#     input_postac=page.get_by_label("Postać *").select_option("syrop")
#     input_dawka=page.get_by_label("Dawka").fill ("40 mg")
#     input_kategoria=page.get_by_label("Kategoria").select_option("Układ pokarmowy")
#     input_cena=page.get_by_role("textbox", name="Cena [zł] *").fill("14,99")
#     input_data=page.get_by_label("Data ważności").fill("2030-12-31")
#     input_stan=page.get_by_role("textbox", name="Stan magazynowy *").fill("30")
#     input_stan_min=page.get_by_role("textbox", name="Stan minimalny *").fill("10")
#     input_lek_rx= page.get_by_label("Lek wydawany na receptę").check()
#     dodaj_lek_button=page.get_by_role("button", name="Dodaj lek").click()
#     expect(page.get_by_test_id("flash-success")).to_have_text("Dodano lek No-Spa.")
#     expect(page.get_by_test_id("detail-price")).to_have_text("14,99 zł")
#     rx_bage=page.locator(".badge-rx")
#     expect(rx_bage).to_be_visible()
#
#     # Jak w zadaniu 5, ale:
#     # - zaznacz checkbox „Lek wydawany na receptę”
#     # - postać ustaw na „syrop”
#     # ✔ Na stronie leku widać badge „Rx”
#     pass
