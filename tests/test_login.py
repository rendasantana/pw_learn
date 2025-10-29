import pytest
from playwright.sync_api import expect

BASE_URL = "https://example.com/login"  # ganti sesuai URL login-mu

@pytest.mark.usefixtures("page")
class TestLogin:

    # ====================
    # ✅ POSITIVE TEST CASES
    # ====================

    def test_login_valid_credentials(self, page):
        """
        Tujuan: Memastikan user dapat login dengan username & password valid.
        """
        page.goto(BASE_URL)
        page.fill("#username", "valid_user")
        page.fill("#password", "valid_password")
        page.click("button[type='submit']")
        expect(page).to_have_url("https://example.com/dashboard")

    def test_login_case_insensitive_username(self, page):
        """
        Tujuan: Memastikan username tidak case-sensitive (contoh: ADMIN vs admin).
        """
        page.goto(BASE_URL)
        page.fill("#username", "VALID_USER")  # huruf besar semua
        page.fill("#password", "valid_password")
        page.click("button[type='submit']")
        expect(page).to_have_url("https://example.com/dashboard")

    def test_login_with_spaces_trimmed(self, page):
        """
        Tujuan: Memastikan spasi di awal/akhir username diabaikan sistem.
        """
        page.goto(BASE_URL)
        page.fill("#username", "  valid_user  ")
        page.fill("#password", "valid_password")
        page.click("button[type='submit']")
        expect(page).to_have_url("https://example.com/dashboard")

    # ====================
    # ❌ NEGATIVE TEST CASES
    # ====================

    def test_login_invalid_username(self, page):
        """
        Tujuan: Menampilkan error jika username salah.
        """
        page.goto(BASE_URL)
        page.fill("#username", "invalid_user")
        page.fill("#password", "valid_password")
        page.click("button[type='submit']")
        expect(page.locator(".error-message")).to_have_text("Invalid username or password")

    def test_login_invalid_password(self, page):
        """
        Tujuan: Menampilkan error jika password salah.
        """
        page.goto(BASE_URL)
        page.fill("#username", "valid_user")
        page.fill("#password", "wrong_password")
        page.click("button[type='submit']")
        expect(page.locator(".error-message")).to_have_text("Invalid username or password")

    def test_login_empty_fields(self, page):
        """
        Tujuan: Tidak bisa login jika kedua field kosong.
        """
        page.goto(BASE_URL)
        page.click("button[type='submit']")
        expect(page.locator(".error-message")).to_have_text("Username and password required")

    def test_login_empty_username_only(self, page):
        """
        Tujuan: Tidak bisa login jika hanya password yang diisi.
        """
        page.goto(BASE_URL)
        page.fill("#password", "valid_password")
        page.click("button[type='submit']")
        expect(page.locator(".error-message")).to_have_text("Username is required")

    def test_login_empty_password_only(self, page):
        """
        Tujuan: Tidak bisa login jika hanya username yang diisi.
        """
        page.goto(BASE_URL)
        page.fill("#username", "valid_user")
        page.click("button[type='submit']")
        expect(page.locator(".error-message")).to_have_text("Password is required")

    def test_login_special_characters(self, page):
        """
        Tujuan: Tidak bisa login dengan karakter aneh di username (misal script injection).
        """
        page.goto(BASE_URL)
        page.fill("#username", "<script>alert('x')</script>")
        page.fill("#password", "valid_password")
        page.click("button[type='submit']")
        expect(page.locator(".error-message")).to_have_text("Invalid username or password")

    def test_login_sql_injection_attempt(self, page):
        """
        Tujuan: Pastikan input seperti ' OR '1'='1 tidak berhasil login.
        """
        page.goto(BASE_URL)
        page.fill("#username", "' OR '1'='1")
        page.fill("#password", "' OR '1'='1")
        page.click("button[type='submit']")
        expect(page.locator(".error-message")).to_have_text("Invalid username or password")
