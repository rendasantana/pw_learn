import pytest
from playwright.sync_api import expect

class TestLoginCases:
    base_url = "https://practicetestautomation.com/practice-test-login/"

    # ========== 3 TEST CASE POSITIF ==========
    def test_login_valid_user(self, page):
        page.goto(self.base_url)
        page.fill("#username", "student")
        page.fill("#password", "Password123")
        page.click("#submit")
        expect(page.locator("h1")).to_have_text("Logged In Successfully")
        expect(page.locator(".post-content")).to_contain_text("Congratulations")
        expect(page).to_have_url("https://practicetestautomation.com/logged-in-successfully/")

    def test_login_redirect_button(self, page):
        page.goto(self.base_url)
        page.fill("#username", "student")
        page.fill("#password", "Password123")
        page.click("#submit")
        page.click("text=Log out")
        expect(page).to_have_url(self.base_url)

    def test_login_case_insensitive_password_fail(self, page):
        """Pastikan password sensitif terhadap huruf besar/kecil"""
        page.goto(self.base_url)
        page.fill("#username", "student")
        page.fill("#password", "password123")  # lowercase, seharusnya gagal
        page.click("#submit")
        expect(page.locator("#error")).to_have_text("Your password is invalid!")

    # ========== 7 TEST CASE NEGATIF ==========
    def test_login_invalid_username(self, page):
        page.goto(self.base_url)
        page.fill("#username", "wronguser")
        page.fill("#password", "Password123")
        page.click("#submit")
        expect(page.locator("#error")).to_have_text("Your username is invalid!")

    def test_login_invalid_password(self, page):
        page.goto(self.base_url)
        page.fill("#username", "student")
        page.fill("#password", "WrongPassword")
        page.click("#submit")
        expect(page.locator("#error")).to_have_text("Your password is invalid!")

    def test_login_empty_username(self, page):
        page.goto(self.base_url)
        page.fill("#username", "")
        page.fill("#password", "Password123")
        page.click("#submit")
        expect(page.locator("#error")).to_have_text("Your username is invalid!")

    def test_login_empty_password(self, page):
        page.goto(self.base_url)
        page.fill("#username", "student")
        page.fill("#password", "")
        page.click("#submit")
        expect(page.locator("#error")).to_have_text("Your password is invalid!")

    def test_login_both_fields_empty(self, page):
        page.goto(self.base_url)
        page.fill("#username", "")
        page.fill("#password", "")
        page.click("#submit")
        expect(page.locator("#error")).to_have_text("Your username is invalid!")

    def test_login_with_space_in_username(self, page):
        page.goto(self.base_url)
        page.fill("#username", " student ")  # ada spasi
        page.fill("#password", "Password123")
        page.click("#submit")
        expect(page.locator("#error")).to_have_text("Your username is invalid!")

    def test_login_with_sql_injection(self, page):
        page.goto(self.base_url)
        page.fill("#username", "' OR 1=1 --")
        page.fill("#password", "' OR '1'='1")
        page.click("#submit")
        expect(page.locator("#error")).to_have_text("Your username is invalid!")
