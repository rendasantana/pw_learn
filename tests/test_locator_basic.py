import pytest
from playwright.sync_api import expect

URL = "https://demoqa.com/text-box"

@pytest.mark.usefixtures("page")
class TestLocatorBasic:

    def test_locator_and_actions(self, page):
        # Coba tutup popup jika muncul
        try:
            popup_close = page.locator("//button[contains(., 'X') or contains(., 'Close') or contains(., 'Skip')]")
            if popup_close.is_visible():
                popup_close.click()
                print("Popup berhasil ditutup.")
        except:
            print("Tidak ada popup ditemukan, lanjut...")



        page.goto(URL)
        page.wait_for_selector("#userName")

        # 1️⃣ Locator by CSS
        page.locator("#userName").fill("Renda Arya Santana")

        # 2️⃣ Locator by Placeholder
        page.get_by_placeholder("name@example.com").fill("rendasantana@gmail.com")

        # 3️⃣ Locator by Label Text
        page.locator("#currentAddress").fill("Jl. Kauman No.1, Malang")

        # 4️⃣ Scroll dan klik submit pakai get_by_text
        page.get_by_text("Submit").click()

        # 5️⃣ Verifikasi hasil output muncul
        output = page.locator("#output")
        expect(output).to_be_visible()
        expect(output).to_contain_text("Renda Arya Santana")

        # 6️⃣ Screenshot hasil
        page.screenshot(path="reports/locator_basic.png", full_page=True)
