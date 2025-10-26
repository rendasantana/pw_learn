from playwright.sync_api import sync_playwright

def test_open_google():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.google.com")

        # 🔍 Cek apakah URL yang terbuka benar
        assert "google.com" in page.url

        # 🔍 Cek apakah ada elemen input pencarian
        page.fill("textarea[name='q']", "QA Automation Python")
        page.keyboard.press("Enter")
        page.wait_for_timeout(2000)
        page.screenshot(path="hasil_pencarian.png")

        browser.close()
