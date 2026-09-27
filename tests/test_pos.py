from playwright.sync_api import APIRequestContext, Page, expect

from pages import PosPage

APAP_ID = 1


def get_stock(api: APIRequestContext, drug_id: int) -> int:
    return api.get(f"/api/drugs/{drug_id}").json()["stock"]


def test_sale_decreases_stock(farmaceuta_page: Page, api: APIRequestContext):
    stock_before = get_stock(api, APAP_ID)

    pos = PosPage(farmaceuta_page)
    pos.goto()
    pos.add("Apap", quantity=3)
    expect(pos.total).to_have_text("38,97 zł")  # 3 × 12,99 zł

    pos.checkout("Karta")

    expect(farmaceuta_page.get_by_test_id("receipt-total")).to_have_text("38,97 zł")
    assert get_stock(api, APAP_ID) == stock_before - 3


def test_prescription_drug_requires_code(farmaceuta_page: Page):
    pos = PosPage(farmaceuta_page)
    pos.goto()
    pos.add("Amotaks")

    expect(pos.error).to_have_text("Amotaks: lek na receptę — podaj kod recepty.")
    expect(pos.cart_rows).to_have_count(0)


def test_interaction_warning(farmaceuta_page: Page):
    pos = PosPage(farmaceuta_page)
    pos.goto()
    pos.add("Warfin", prescription_code="1234")
    pos.add("Ibuprom")

    expect(pos.interaction_modal).to_be_visible()
    expect(pos.interaction_modal).to_contain_text("warfaryna + ibuprofen")

    farmaceuta_page.get_by_test_id("interaction-confirm").click()

    expect(pos.cart_names).to_have_text(["Warfin", "Ibuprom"])
    expect(farmaceuta_page.get_by_test_id("cart-interactions-warning")).to_be_visible()


def test_cash_payment_shows_change(farmaceuta_page: Page):
    pos = PosPage(farmaceuta_page)
    pos.goto()
    pos.add("Apap")  # 12,99 zł
    pos.checkout("Gotówka", cash="20")

    expect(farmaceuta_page.get_by_test_id("receipt-change")).to_have_text("7,01 zł")
