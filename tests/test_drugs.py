from datetime import date, timedelta

from playwright.sync_api import Page, expect

from pages import DrugFormPage, DrugsPage

NEXT_YEAR = (date.today() + timedelta(days=365)).isoformat()


def test_search_by_active_substance(farmaceuta_page: Page):
    drugs = DrugsPage(farmaceuta_page)
    drugs.goto()
    drugs.search("ibuprofen")

    expect(drugs.names).to_have_text(["Ibuprom", "Nurofen Forte"])
    expect(drugs.count).to_have_text("Znaleziono: 2")


def test_search_without_results(farmaceuta_page: Page):
    drugs = DrugsPage(farmaceuta_page)
    drugs.goto()
    drugs.search("nie ma takiego leku")

    expect(drugs.empty).to_be_visible()
    expect(drugs.rows).to_have_count(0)


def test_add_drug(farmaceuta_page: Page):
    form = DrugFormPage(farmaceuta_page)
    form.goto_new()
    form.fill(name="Paracetamol Test", substance="paracetamol", strength="500 mg",
              category="Przeciwbólowe", price="9,99", stock="40", min_stock="10",
              expiry_date=NEXT_YEAR)
    form.save()

    expect(farmaceuta_page.get_by_test_id("flash-success")).to_have_text("Dodano lek Paracetamol Test.")
    expect(farmaceuta_page.get_by_test_id("drug-title")).to_contain_text("Paracetamol Test")
    expect(farmaceuta_page.get_by_test_id("detail-price")).to_have_text("9,99 zł")


def test_add_drug_shows_validation_errors(farmaceuta_page: Page):
    form = DrugFormPage(farmaceuta_page)
    form.goto_new()
    form.save()

    expect(form.errors_alert).to_be_visible()
    expect(form.error("name")).to_have_text("Nazwa jest wymagana.")
    expect(form.error("price")).to_have_text("Cena jest wymagana.")
    expect(form.error("category")).to_have_text("Wybierz kategorię.")


def test_cannot_add_drug_with_existing_name(farmaceuta_page: Page):
    form = DrugFormPage(farmaceuta_page)
    form.goto_new()
    form.fill(name="apap", substance="paracetamol", strength="500 mg", category="Przeciwbólowe",
              price="10", stock="1", min_stock="1", expiry_date=NEXT_YEAR)
    form.save()

    expect(form.error("name")).to_have_text("Lek o tej nazwie już istnieje.")


def test_manager_can_delete_drug(kierownik_page: Page):
    kierownik_page.goto("/leki/")
    kierownik_page.get_by_role("link", name="Apap", exact=True).click()

    # przycisk "Usuń" otwiera natywne okno confirm() — trzeba je zaakceptować
    kierownik_page.once("dialog", lambda dialog: dialog.accept())
    kierownik_page.get_by_test_id("delete-drug").click()

    expect(kierownik_page.get_by_test_id("flash-success")).to_have_text("Usunięto lek Apap.")
    expect(DrugsPage(kierownik_page).row("Apap")).to_have_count(0)


def test_pharmacist_cannot_delete_drug(farmaceuta_page: Page):
    farmaceuta_page.goto("/leki/1")

    expect(farmaceuta_page.get_by_test_id("edit-drug")).to_be_visible()
    expect(farmaceuta_page.get_by_test_id("delete-drug")).to_have_count(0)
