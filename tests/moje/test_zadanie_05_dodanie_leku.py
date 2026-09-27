from playwright.sync_api import Page, expect


def login(page: Page, username="farmaceuta", password="farmaceuta123"):
    page.goto("/login")
    page.get_by_label("Login").fill(username)
    page.get_by_label("Hasło").fill(password)
    page.get_by_role("button", name="Zaloguj się").click()
    expect(page.get_by_role("heading", name="Pulpit")).to_be_visible()


def test_dodanie_leku(page: Page):
    login(page)
    page.goto("/leki/")
    page.get_by_role("link", name="+ Dodaj lek").click()

    page.get_by_label("Nazwa handlowa").fill("No-Spa")
    page.get_by_label("Substancja czynna").fill("drotaweryna")
    page.get_by_label("Postać").select_option("tabletki")
    page.get_by_label("Dawka").fill("40 mg")
    page.get_by_label("Kategoria").select_option("Układ pokarmowy")
    page.get_by_label("Cena").fill("14,99")
    page.get_by_label("Stan magazynowy").fill("30")
    page.get_by_label("Stan minimalny").fill("10")
    page.get_by_label("Data ważności").fill("2030-12-31")
    page.get_by_role("button", name="Dodaj lek").click()

    expect(page.get_by_test_id("flash-success")).to_have_text("Dodano lek No-Spa.")
    expect(page.get_by_test_id("drug-title")).to_contain_text("No-Spa")
    expect(page.get_by_test_id("detail-price")).to_have_text("14,99 zł")

    # bonus: nowy lek jest na liście
    page.goto("/leki/")
    page.get_by_label("Szukaj").fill("No-Spa")
    page.get_by_role("button", name="Filtruj").click()
    expect(page.get_by_test_id("drug-row")).to_have_count(1)
