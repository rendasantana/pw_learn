import pytest
from playwright.sync_api import expect

BASE_URL = "https://practicetestautomation.com/practice-test-login/"

# Skema kolom:
# username, password, expect_success(bool), expected_error(str) / expected_url(str)
TEST_CASES = [
    # ✅ POSITIF
    {
        "id": "valid_login",
        "username": "student",
        "password": "Password123",
        "expect_success": True,
        "expected_url": "https://practicetestautomation.com/logged-in-successfully/",
        "expected_error": None
    },
    {
        "id": "valid_login_then_logout",
        "username": "student",
        "password": "Password123",
        "expect_success": True,
        "expected_url": "https://practicetestautomation.com/logged-in-successfully/",
        "expected_error": None
    },
    {
        "id": "password_case_sensitivity_negative",
        "username": "student",
        "password": "password123",  # salah case
        "expect_success": False,
        "expected_url": None,
        "expected_error": "Your password is invalid!"
    },

    # ❌ NEGATIF (7 contoh)
    {
        "id": "invalid_username",
        "username": "wronguser",
        "password": "Password123",
        "expect_success": False,
        "expected_url": None,
        "expected_error": "Your username is invalid!"
    },
    {
        "id": "invalid_password",
        "username": "student",
        "password": "WrongPassword",
        "expect_success": False,
        "expected_url": None,
        "expected_error": "Your password is invalid!"
    },
    {
        "id": "empty_username",
        "username": "",
        "password": "Password123",
        "expect_success": False,
        "expected_url": None,
        "expected_error": "Your username is invalid!"
    },
    {
        "id": "empty_password",
        "username": "student",
        "password": "",
        "expect_success": False,
        "expected_url": None,
        "expected_error": "Your password is invalid!"
    },
    {
        "id": "both_empty",
        "username": "",
        "password": "",
        "expect_success": False,
        "expected_url": None,
        "expected_error": "Your username is invalid!"
    },
    {
        "id": "username_with_spaces",
        "username": " student ",
        "password": "Password123",
        "expect_success": False,
        "expected_url": None,
        "expected_error": "Your username is invalid!"
    },
    {
        "id": "sql_injection",
        "username": "' OR 1=1 --",
        "password": "' OR '1'='1",
        "expect_success": False,
        "expected_url": None,
        "expected_error": "Your username is invalid!"
    },
]

from playwright.sync_api import expect

@pytest.mark.parametrize("case", TEST_CASES, ids=[c["id"] for c in TEST_CASES])
def test_login_ddt_inline(page, case):
    page.goto(BASE_URL)

    page.fill("#username", case["username"])
    page.fill("#password", case["password"])
    page.click("#submit")

    if case["expect_success"]:
        # halaman sukses
        expect(page.locator("h1")).to_have_text("Logged In Successfully")
        expect(page).to_have_url(case["expected_url"])

        if case["id"] == "valid_login_then_logout":
            page.click("text=Log out")
            expect(page).to_have_url(BASE_URL)
    else:
        # error message
        expect(page.locator("#error")).to_have_text(case["expected_error"])

