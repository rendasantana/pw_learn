import pytest
import logging
from playwright.sync_api import Page

@pytest.mark.parametrize(
    "username,password,should_succeed", [
        ("tomsmith", "SuperSecretPassword!", True),  # Login sukses
        pytest.param("tomsmith", "wrongpass", False, marks=pytest.mark.xfail(reason="Login gagal sesuai harapan")),
    ]
)
def test_login(page: Page, username, password, should_succeed):
    logging.info("=== Mulai pengujian login ===")
    logging.info(f"Input data → Username: {username} | Password: {password}")

    page.goto("https://the-internet.herokuapp.com/login")
    page.fill("#username", username)
    page.fill("#password", password)
    page.click("button[type='submit']")

    if should_succeed:
        assert page.is_visible("text=Secure Area")
        logging.info("✅ Login berhasil.")
    else:
        assert page.is_visible("text=Your username is invalid!") or page.is_visible("text=Your password is invalid!")
        logging.info("⚠️ Login gagal sesuai harapan.")
