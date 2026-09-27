from datetime import date, timedelta

from playwright.sync_api import APIRequestContext, Playwright

NEW_DRUG = {
    "name": "Testomed",
    "active_substance": "testina",
    "form": "syrop",
    "strength": "100 mg/5 ml",
    "category": "Przeziębienie i grypa",
    "price": 19.99,
    "stock": 25,
    "min_stock": 5,
    "rx": False,
    "expiry_date": (date.today() + timedelta(days=200)).isoformat(),
}


def test_requires_login(playwright: Playwright, base_url):
    anonymous = playwright.request.new_context(base_url=base_url)
    response = anonymous.get("/api/drugs")

    assert response.status == 401
    anonymous.dispose()


def test_create_and_get_drug(api: APIRequestContext):
    created = api.post("/api/drugs", data=NEW_DRUG)
    assert created.status == 201
    drug_id = created.json()["id"]

    fetched = api.get(f"/api/drugs/{drug_id}").json()
    assert fetched["name"] == "Testomed"
    assert fetched["price"] == 19.99


def test_create_drug_validation(api: APIRequestContext):
    response = api.post("/api/drugs", data={**NEW_DRUG, "price": -5, "stock": "dużo"})

    assert response.status == 400
    errors = response.json()["errors"]
    assert errors["price"] == "Cena musi być większa od zera."
    assert errors["stock"] == "Stan magazynowy musi być liczbą całkowitą."


def test_pharmacist_cannot_delete(playwright: Playwright, base_url):
    ctx = playwright.request.new_context(base_url=base_url)
    ctx.post("/api/login", data={"username": "farmaceuta", "password": "farmaceuta123"})

    response = ctx.delete("/api/drugs/1")

    assert response.status == 403
    ctx.dispose()
