from playwright.sync_api import Page


class DrugsPage:
    """Lista leków: /leki/"""

    def __init__(self, page: Page):
        self.page = page
        self.search_input = page.get_by_label("Szukaj")
        self.filter_button = page.get_by_role("button", name="Filtruj")
        self.rows = page.get_by_test_id("drug-row")
        self.names = page.locator(".drug-name")
        self.count = page.get_by_test_id("drugs-count")
        self.empty = page.get_by_test_id("drugs-empty")
        self.add_button = page.get_by_test_id("add-drug")

    def goto(self, **params):
        query = "&".join(f"{k}={v}" for k, v in params.items())
        self.page.goto("/leki/" + (f"?{query}" if query else ""))

    def search(self, text: str):
        self.search_input.fill(text)
        self.filter_button.click()

    def row(self, name: str):
        return self.rows.filter(has=self.page.get_by_role("link", name=name, exact=True))


class DrugFormPage:
    """Formularz dodawania / edycji leku."""

    def __init__(self, page: Page):
        self.page = page
        self.save_button = page.get_by_test_id("save-drug")
        self.errors_alert = page.get_by_test_id("form-errors")

    def goto_new(self):
        self.page.goto("/leki/nowy")

    def fill(self, name="", substance="", form="tabletki", strength="", category="",
             price="", stock="", min_stock="", expiry_date="", rx=False):
        p = self.page
        p.get_by_label("Nazwa handlowa").fill(name)
        p.get_by_label("Substancja czynna").fill(substance)
        p.get_by_label("Postać").select_option(form)
        p.get_by_label("Dawka").fill(strength)
        if category:
            p.get_by_label("Kategoria").select_option(category)
        p.get_by_label("Cena").fill(price)
        p.get_by_label("Stan magazynowy").fill(stock)
        p.get_by_label("Stan minimalny").fill(min_stock)
        p.get_by_label("Data ważności").fill(expiry_date)
        p.get_by_label("Lek wydawany na receptę").set_checked(rx)

    def save(self):
        self.save_button.click()

    def error(self, field: str):
        return self.page.get_by_test_id(f"error-{field}")
