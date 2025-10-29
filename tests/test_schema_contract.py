import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema
from pandera.errors import SchemaErrors

# === Definisikan schema yang disetujui ===
approved_schema = DataFrameSchema({
    "id": Column(int),
    "name": Column(str),
    "price": Column(float, coerce=True),  # otomatis ubah int → float
    "status": Column(str),
})

def validate_schema(df: pd.DataFrame):
    print("\n=== 🔍 Mulai Validasi Schema CSV ===")

    # 1️⃣ Cek kolom yang tersedia
    csv_columns = list(df.columns)
    print(f"📄 Kolom ditemukan di CSV : {csv_columns}")

    schema_columns = list(approved_schema.columns.keys())
    print(f"📋 Kolom yang diharapkan : {schema_columns}")

    missing = set(schema_columns) - set(csv_columns)
    extra = set(csv_columns) - set(schema_columns)

    # Logging perbedaan kolom
    if missing:
        print(f"❌ Kolom hilang di CSV : {missing}")
    if extra:
        print(f"⚠️  Kolom tambahan tak terduga : {extra}")

    # 2️⃣ Jalankan validasi schema Pandera
    try:
        validated_df = approved_schema.validate(df, lazy=True)
        print("✅ Semua kolom dan tipe data sesuai dengan kontrak schema!")
        print("📊 5 data pertama:")
        print(validated_df.head())
        print("=== 🏁 Validasi Schema Selesai ===\n")
        return validated_df

    except SchemaErrors as e:
        print("\n❌ Terjadi kesalahan validasi schema!")
        print(f"Total error: {len(e.failure_cases)}")
        print("🧩 Detail error:")
        print(e.failure_cases)
        print("=== 🚨 Validasi Schema GAGAL ===\n")
        raise e


def test_schema_contract():
    print("🚀 Menjalankan test_schema_contract...\n")

    # Load CSV
    df = pd.read_csv("testdata/products.csv")

    # Jalankan validasi
    validated_df = validate_schema(df)

    # Pastikan hasil valid
    assert not validated_df.empty
