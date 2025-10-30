import os
import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema, Check
import pytest
from playwright.sync_api import Page

# ================= CSV & Schema =================
base_dir = os.path.dirname(__file__)
csv_path = os.path.join(base_dir, "../testdata/demoqa_users.csv")

# kalau CSV tidak ada header, pakai header manual:
# df = pd.read_csv(csv_path, header=None, names=["name","email","current_address","permanent_address"])

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

# ================= Pytest + Playwright =================
@pytest.mark.parametrize("row_index", range(len(validated_df)))
def test_fill_demoqa_form(page: Page, row_index):
    row = validated_df.iloc[row_index]

    try:
        # buka halaman form
        page.goto("https://demoqa.com/text-box")

        # isi form
        page.fill("#userName", row["name"])
        page.fill("#userEmail", row["email"])
        page.fill("#currentAddress", row["current_address"])
        page.fill("#permanentAddress", row["permanent_address"])

        # klik submit
        page.click("#submit")

        # cek apakah hasil muncul
        assert page.locator("#output").is_visible(), "Output tidak muncul!"

    except Exception as e:
        # screenshot otomatis setiap row gagal
        screenshot_path = f"reports/screenshots/demoqa_row{row_index}_{row['name'].replace(' ','_')}.png"
        page.screenshot(path=screenshot_path)
        print(f"❌ Row {row_index} gagal, screenshot disimpan: {screenshot_path}")
        raise e
