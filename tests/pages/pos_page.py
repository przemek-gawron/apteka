from playwright.sync_api import Page


class PosPage:
    """Kasa: /kasa"""

    def __init__(self, page: Page):
        self.page = page
        self.drug_select = page.get_by_label("Lek", exact=True)
        self.quantity = page.get_by_label("Ilość")
        self.prescription = page.get_by_label("Kod recepty")
        self.add_button = page.get_by_test_id("add-to-cart")
        self.error = page.get_by_test_id("pos-error")
        self.cart_rows = page.get_by_test_id("cart-row")
        self.cart_names = page.get_by_test_id("cart-item-name")
        self.total = page.get_by_test_id("cart-total")
        self.interaction_modal = page.get_by_test_id("interaction-modal")
        self.cash_received = page.get_by_label("Otrzymano")
        self.checkout_button = page.get_by_test_id("checkout")

    def goto(self):
        self.page.goto("/kasa")

    def select_drug(self, name: str):
        # opcje mają postać "Apap 500 mg — 12,99 zł · stan: 120", więc wybieramy po początku tekstu
        option = self.drug_select.locator("option", has_text=f"{name} ").first
        self.drug_select.select_option(option.get_attribute("value"))

    def add(self, name: str, quantity: int = 1, prescription_code: str = ""):
        self.select_drug(name)
        self.quantity.fill(str(quantity))
        if prescription_code:
            self.prescription.fill(prescription_code)
        self.add_button.click()

    def checkout(self, method: str = "Karta", cash: str = ""):
        self.page.get_by_label(method, exact=True).check()
        if cash:
            self.cash_received.fill(cash)
        self.checkout_button.click()
