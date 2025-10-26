from playwright.sync_api import sync_playwright
import time

def test_login_success():
    """Test case: Login dengan username & password yang benar"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://practicetestautomation.com/practice-test-login/")

        # Login benar
        page.fill("input#username", "student")
        page.fill("input#password", "Password123")
        page.click("button#submit")

        # Verifikasi login sukses
        success_message = page.locator("text=Logged In Successfully")
        assert success_message.is_visible(), "Pesan sukses tidak muncul!"

        # Screenshot hasil
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        page.screenshot(path=f"screenshots/login_success_{timestamp}.png")

        browser.close()


def test_login_failed():
    """Test case: Login dengan password yang salah"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://practicetestautomation.com/practice-test-login/")

        # Login salah (password salah)
        page.fill("input#username", "student")
        page.fill("input#password", "Salah123")
        page.click("button#submit")

        # Verifikasi pesan error
        error_message = page.locator("div#error")
        assert error_message.is_visible(), "Pesan error tidak muncul!"

        browser.close()
