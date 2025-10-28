import pytest
from playwright.sync_api import Page, expect

URL = "https://demoqa.com/text-box"

class TestAssertionBasic:
    def test_form_submission_and_assert(self, page: Page):
        # Buka halaman
        page.goto(URL)

        # Hapus iklan/pop-up
        page.evaluate("""
            document.querySelectorAll('[class*="overlay"], [class*="popup"], [id*="ad"]').forEach(el => el.remove());
        """)

        # Isi form
        page.locator("#userName").fill("Renda Arya Santana")
        page.locator("#userEmail").fill("rendasantana@gmail.com")
        page.locator("#currentAddress").fill("Jl. Kauman No.1")
        page.locator("#permanentAddress").fill("Malang, Jawa Timur")

        # Klik tombol submit
        page.locator("#submit").click()

        # Tunggu output muncul
        output = page.locator("#output")
        expect(output).to_be_visible()

        # Assertion isi hasil form
        expect(output.locator("#name")).to_contain_text("Renda Arya Santana")
        expect(output.locator("#email")).to_contain_text("rendasantana@gmail.com")
        expect(output.locator("#currentAddress")).to_contain_text("Kauman")
        expect(output.locator("#permanentAddress")).to_contain_text("Malang")

        print("✅ Semua hasil form sesuai input.")
