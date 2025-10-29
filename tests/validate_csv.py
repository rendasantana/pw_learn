import os
import pandas as pd
import pandera.pandas as pa
from pandera import Column, DataFrameSchema, Check
from schema_product import product_schema


# cari path file relatif terhadap lokasi script ini
base_dir = os.path.dirname(__file__)
csv_path = os.path.join(base_dir, "../testdata/products.csv")

product_schema = DataFrameSchema({
    "id": Column(int, Check.greater_than(0), nullable=False, coerce=True),
    "name": Column(str, Check.str_length(1, 100), nullable=False),
    "price": Column(float, Check.ge(0), nullable=False, coerce=True),
    "status": Column(str, Check.isin(["active", "inactive"]), nullable=False)
})

df = pd.read_csv(csv_path)

try:
    product_schema.validate(df)
    print("✅ CSV VALID! Semua data sesuai schema.")
except pa.errors.SchemaError as e:
    print("❌ CSV INVALID!")
    print(e)

# Validasi dengan schema
validated_df = product_schema.validate(df)
print("✅ Data CSV valid dan sesuai schema!")
