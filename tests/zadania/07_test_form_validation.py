from playwright.sync_api import Page, expect

from zadania.helpers import login


# def test_form_validation(page: Page):
#     login(page)
#     page.get_by_role("link", name="Leki", exact=True).click()
#     page.get_by_test_id("add-drug").click()
#     input_dodaj_lek=page.get_by_role("button", name="Dodaj lek").click()
#     expect(page.get_by_test_id("form-errors")).to_be_visible()
#     expect(page.get_by_test_id("error-name")).to_have_text("Nazwa jest wymagana.")
#     cena_input=page.get_by_placeholder("12,50").fill("abc")
#     input_dodaj_lek=page.get_by_role("button", name= "Dodaj lek").click()
#     expect(page.get_by_test_id("error-price")).to_have_text("Niepoprawna cena (np. 12,50).")
#
#     # Otwórz formularz nowego leku i od razu kliknij „Dodaj lek”.
#     # ✔ Widać ramkę błędów (form-errors).
#     # ✔ error-name to „Nazwa jest wymagana.”
#     # Potem wpisz cenę „abc” i zapisz ponownie.
#     # ✔ error-price to „Niepoprawna cena (np. 12,50).”
#     pass
