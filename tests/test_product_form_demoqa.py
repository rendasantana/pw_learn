import os
import pandas as pd
import pytest
from playwright.sync_api import Page
from pandera import Column, DataFrameSchema, Check
import pandera.pandas as pa

# --- CSV Path ---
base_dir = os.path.dirname(__file__)
csv_path = os.path.join(base_dir, "../testdata/products3.csv")

# --- Schema CSV ---
product_schema = pa.DataFrameSchema({
    "name": Column(str, Check.str_length(1, 100), nullable=False),
    "email": Column(str, Check.str_matches(r"[^@]+@[^@]+\.[^@]+"), nullable=False),
    "current_address": Column(str, Check.str_length(1, 200), nullable=False),
    "permanent_address": Column(str, Check.str_length(1, 200), nullable=False),
})

# --- Baca dan validasi CSV ---
df = pd.read_csv(csv_path)
validated_df = product_schema.validate(df, lazy=True)

# --- Test ---
@pytest.mark.parametrize("row_index", range(len(validated_df)))
def test_fill_demoqa_form(page: Page, row_index):
    row = validated_df.iloc[row_index]

    # Buka URL form demo
    page.goto("https://demoqa.com/text-box")

    # Isi form
    page.fill("#userName", row["name"])
    page.fill("#userEmail", row["email"])
    page.fill("#currentAddress", row["current_address"])
    page.fill("#permanentAddress", row["permanent_address"])

    # Submit
    page.click("#submit")

    # Validasi muncul output
    output_name = page.text_content("#name")
    assert row["name"] in output_name

    print(f"✅ Row {row_index} berhasil submit form dengan nama: {row['name']}")
