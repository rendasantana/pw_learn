import pytest
from playwright.sync_api import expect

URL = "https://demoqa.com/automation-practice-form"


@pytest.mark.usefixtures("page")
class TestFormInput:

    def test_fill_form_success(self, page):
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("#firstName", timeout=30000)


        # Hilangkan iklan & popup
        page.evaluate("""
            document.querySelectorAll('#fixedban, #adplus-anchor').forEach(el => el.remove());
            const modal = document.querySelector('.fc-dialog-container');
            if (modal) modal.remove();
        """)

        # Pastikan elemen form terlihat
        page.wait_for_selector("#firstName")
        page.mouse.wheel(0, 1000)

        # Isi form
        page.fill("#firstName", "Renda")
        page.fill("#lastName", "Santana")
        page.fill("#userEmail", "rendasantana@gmail.com")

        # Klik gender dengan lebih aman (pakai input asli)
        page.locator("input[id='gender-radio-1']").evaluate("el => el.click()")

        # Isi nomor HP
        page.fill("#userNumber", "081358571315")

        # Scroll dan klik Submit pakai force=True
        page.locator("#submit").scroll_into_view_if_needed()
        page.wait_for_timeout(1000)
        page.locator("#submit").click(force=True)

        # Tunggu modal muncul
        modal = page.locator(".modal-content")
        expect(modal).to_be_visible(timeout=10000)

        # Screenshot hasil
        page.wait_for_timeout(1500)
        page.screenshot(path="reports/form_success.png", full_page=True, animations="disabled", timeout=10000)


        # Validasi isi modal
        result_text = modal.inner_text()
        assert "Renda" in result_text
        assert "Santana" in result_text
        assert "rendasantana@gmail.com" in result_text


    def test_form_incomplete_should_fail(self, page):
        """Test jika field wajib tidak diisi"""
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("#firstName", timeout=30000)

        # Hapus iklan
        page.evaluate("""
            document.querySelectorAll('#fixedban, #adplus-anchor').forEach(el => el.remove());
        """)

        # Isi sebagian field (tanpa first name)
        page.fill("#lastName", "Santana")
        page.fill("#userEmail", "rendasantana@gmail.com")
        page.locator("input[id='gender-radio-1']").evaluate("el => el.click()")
        page.fill("#userNumber", "081358571315")

        # Scroll & submit
        page.locator("#submit").scroll_into_view_if_needed()
        page.wait_for_timeout(1000)
        page.locator("#submit").click(force=True)

        # Tunggu respon
        page.wait_for_timeout(2000)

        # Pastikan modal tidak muncul
        modal = page.locator(".modal-content")
        expect(modal).not_to_be_visible(timeout=3000)

        # Screenshot hasil gagal
        page.wait_for_timeout(1500)
        page.screenshot(path="reports/form_success.png", full_page=True, animations="disabled", timeout=10000)


        # Form masih terlihat
        assert page.locator("#firstName").is_visible()
