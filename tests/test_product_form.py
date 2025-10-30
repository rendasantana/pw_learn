import pandas as pd
import pytest
from playwright.sync_api import Page
from pandera import Column, DataFrameSchema

# 1️⃣ Validasi CSV
product_schema = DataFrameSchema({
    "name": Column(str, nullable=False),
    "price": Column(float, nullable=False, coerce=True),
    "status": Column(str, nullable=False)
})

df = pd.read_csv("testdata/products2.csv")
validated_df = product_schema.validate(df)

# 2️⃣ Test Playwright
@pytest.mark.parametrize("row_index", range(len(validated_df)))
def test_fill_product_form(page: Page, row_index):
    row = validated_df.iloc[row_index]

    # Ganti URL ini dengan halaman form produk yang sebenarnya
    page.goto("https://example.com/product_form")

    # Isi form dengan data CSV
    page.fill("#product_name", row["name"])
    page.fill("#product_price", str(row["price"]))
    page.select_option("#product_status", row["status"])
    page.click("#submit_button")

    
    # Submit form
    page.click("#submit_button")

    # Validasi URL / pesan sukses
    assert "success" in page.url or page.is_visible("#success_message")
