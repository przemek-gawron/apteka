from playwright.sync_api import Page, expect


def login(page: Page, username="farmaceuta", password="farmaceuta123"):
    page.goto("/login")
    page.get_by_label("Login").fill(username)
    page.get_by_label("Hasło").fill(password)
    page.get_by_role("button", name="Zaloguj się").click()
    expect(page.get_by_role("heading", name="Pulpit")).to_be_visible()


def test_pusty_formularz_pokazuje_bledy(page: Page):
    login(page)
    page.goto("/leki/nowy")

    page.get_by_role("button", name="Dodaj lek").click()

    expect(page.get_by_test_id("form-errors")).to_be_visible()
    expect(page.get_by_test_id("error-name")).to_have_text("Nazwa jest wymagana.")
    expect(page).to_have_url("/leki/nowy")


def test_niepoprawna_cena(page: Page):
    login(page)
    page.goto("/leki/nowy")

    page.get_by_label("Cena").fill("abc")
    page.get_by_role("button", name="Dodaj lek").click()

    expect(page.get_by_test_id("error-price")).to_have_text("Nieprawidłowa cena.")
