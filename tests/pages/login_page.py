from playwright.sync_api import Page


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.username = page.get_by_label("Login")
        self.password = page.get_by_label("Hasło")
        self.submit = page.get_by_role("button", name="Zaloguj się")
        self.error = page.get_by_test_id("login-error")

    def goto(self):
        self.page.goto("/login")

    def login(self, username: str, password: str):
        self.username.fill(username)
        self.password.fill(password)
        self.submit.click()
