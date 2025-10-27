import logging
import pytest
import time

@pytest.mark.parametrize("username, password, expected", [
    ("tomsmith", "SuperSecretPassword!", True),   # Login sukses (user bawaan demo site)
    ("tomsmith", "wrongpass", False),             # Login gagal
])
def test_login(page, username, password, expected):
    """
    Pengujian login sederhana menggunakan Playwright bawaan pytest.
    Tidak perlu memanggil sync_playwright() — pytest sudah sediakan fixture `page`.
    """

    logging.info("=== Mulai pengujian login ===")
    logging.info(f"Input data → Username: {username} | Password: {password}")

    # 1️⃣ Buka halaman login
    page.goto("https://the-internet.herokuapp.com/login")
    logging.info("Membuka halaman login...")

    # 2️⃣ Isi field username & password
    page.fill("#username", username)
    page.fill("#password", password)
    page.click("button[type='submit']")
    logging.info("Klik tombol login...")

    # 3️⃣ Tunggu sebentar untuk memuat respon
    time.sleep(1)

    # 4️⃣ Validasi hasil
    if expected:
        page.wait_for_selector(".flash.success")
        success_message = page.locator(".flash.success").text_content()
        assert "You logged into a secure area!" in success_message
        logging.info("✅ Login berhasil.")
    else:
        page.wait_for_selector(".flash.error")
        error_message = page.locator(".flash.error").text_content()
        assert "Your password is invalid!" in error_message or "Your username is invalid!" in error_message
        logging.info("⚠️ Login gagal seperti yang diharapkan.")

    # 5️⃣ Ambil screenshot untuk laporan
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    screenshot_path = f"reports/test_login_{'success' if expected else 'failed'}_{timestamp}.png"
    page.screenshot(path=screenshot_path)
    logging.info(f"📸 Screenshot disimpan di: {screenshot_path}")

    logging.info("=== Pengujian login selesai ===")
