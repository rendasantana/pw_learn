import pytest
from playwright.sync_api import expect
from tests.utils.data_loader import load_login_csv

BASE_URL = "https://practicetestautomation.com/practice-test-login/"
CSV_PATH = "testdata/login_cases.csv"

CASES = load_login_csv(CSV_PATH)

@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_login_ddt_csv(page, case):
    page.goto(BASE_URL)

    page.fill("#username", case["username"] or "")
    page.fill("#password", case["password"] or "")
    page.click("#submit")

    if case["expect_success"]:
        expect(page.locator("h1")).to_have_text("Logged In Successfully")
        expect(page).to_have_url(case["expected_url"])

        if case["id"] == "valid_login_then_logout":
            page.click("text=Log out")
            expect(page).to_have_url(BASE_URL)
    else:
        expect(page.locator("#error")).to_have_text(case["expected_error"])
