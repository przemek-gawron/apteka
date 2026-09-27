from playwright.sync_api import Page, Route, expect


def test_charts_load(farmaceuta_page: Page):
    farmaceuta_page.goto("/")

    # dane wykresu ładują się z opóźnieniem — expect() sam poczeka, aż spinner zniknie
    expect(farmaceuta_page.get_by_test_id("revenue-loading")).to_be_hidden()
    expect(farmaceuta_page.get_by_test_id("revenue-chart")).to_be_visible()
    expect(farmaceuta_page.get_by_test_id("top-list").locator("li")).to_have_count(5)


def test_chart_shows_error_when_api_fails(farmaceuta_page: Page):
    # mock: API statystyk zwraca błąd 500
    def fail(route: Route):
        route.fulfill(status=500, body="Internal Server Error")

    farmaceuta_page.route("**/api/stats/revenue*", fail)
    farmaceuta_page.goto("/")

    expect(farmaceuta_page.get_by_test_id("revenue-error")).to_be_visible()
    expect(farmaceuta_page.get_by_test_id("revenue-chart")).to_be_hidden()
