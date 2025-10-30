import os
import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema, Check
import pytest
from playwright.sync_api import Page

# ================= CSV & Schema =================
base_dir = os.path.dirname(__file__)
csv_path = os.path.join(base_dir, "../testdata/demoqa_users.csv")

df = pd.read_csv(csv_path)

# Schema validasi CSV
user_schema = pa.DataFrameSchema({
    "name": Column(str, Check.str_length(1, 100), nullable=False),
    "email": Column(str, Check.str_matches(r"[^@]+@[^@]+\.[^@]+"), nullable=False),
    "current_address": Column(str, Check.str_length(1, 255), nullable=False),
    "permanent_address": Column(str, Check.str_length(1, 255), nullable=False),
})

# Validasi CSV sebelum test
validated_df = user_schema.validate(df, lazy=True)

# ================= Helper =================
def save_screenshot(page: Page, row_index, name):
    os.makedirs("reports/screenshots", exist_ok=True)
    path = f"reports/screenshots/demoqa_row{row_index}_{name.replace(' ','_')}.png"
    page.screenshot(path=path)
    print(f"📸 Screenshot disimpan: {path}")
    return path

def log_action(message: str):
    print(f"➡️ {message}")

# ================= Pytest + Playwright =================
@pytest.mark.parametrize("row_index", range(len(validated_df)))
def test_fill_demoqa_form_logging(page: Page, row_index):
    row = validated_df.iloc[row_index]

    try:
        # buka halaman form
        log_action(f"Membuka halaman DemoQA untuk row {row_index}")
        page.goto("https://demoqa.com/text-box")

        # isi form
        log_action(f"Isi field Name: {row['name']}")
        page.fill("#userName", row["name"])

        log_action(f"Isi field Email: {row['email']}")
        page.fill("#userEmail", row["email"])

        log_action(f"Isi field Current Address: {row['current_address']}")
        page.fill("#currentAddress", row["current_address"])

        log_action(f"Isi field Permanent Address: {row['permanent_address']}")
        page.fill("#permanentAddress", row["permanent_address"])

        # klik submit
        log_action("Klik tombol Submit")
        page.click("#submit")

        # cek apakah hasil muncul
        log_action("Cek output muncul")
        assert page.locator("#output").is_visible(), "Output tidak muncul!"

        log_action(f"✅ Row {row_index} berhasil di-submit.")

    except Exception as e:
        # screenshot otomatis jika gagal
        save_screenshot(page, row_index, row["name"])
        print(f"❌ Row {row_index} gagal!")
        raise e
