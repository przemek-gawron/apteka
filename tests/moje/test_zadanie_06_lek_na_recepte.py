from playwright.sync_api import Page, expect


def login(page: Page, username="farmaceuta", password="farmaceuta123"):
    page.goto("/login")
    page.get_by_label("Login").fill(username)
    page.get_by_label("Hasło").fill(password)
    page.get_by_role("button", name="Zaloguj się").click()
    expect(page.get_by_role("heading", name="Pulpit")).to_be_visible()


def test_dodanie_leku_na_recepte(page: Page):
    login(page)
    page.goto("/leki/nowy")

    page.get_by_label("Nazwa handlowa").fill("No-Spa")
    page.get_by_label("Substancja czynna").fill("drotaweryna")
    page.get_by_label("Postać").select_option("syrop")
    page.get_by_label("Dawka").fill("40 mg")
    page.get_by_label("Kategoria").select_option("Układ pokarmowy")
    page.get_by_label("Cena").fill("14,99")
    page.get_by_label("Stan magazynowy").fill("30")
    page.get_by_label("Stan minimalny").fill("10")
    page.get_by_label("Data ważności").fill("2030-12-31")
    page.get_by_label("Lek wydawany na receptę").check()
    page.get_by_role("button", name="Dodaj lek").click()

    expect(page.get_by_test_id("flash-success")).to_have_text("Dodano lek No-Spa.")
    expect(page.get_by_title("Lek na receptę")).to_have_text("Rx")
