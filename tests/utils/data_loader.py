import csv
from pathlib import Path

def load_login_csv(path: str):
    cases = []
    full = Path(path)
    if not full.exists():
        raise FileNotFoundError(f"CSV tidak ditemukan: {full}")

    with full.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Konversi boolean expect_success dari string CSV
            row["expect_success"] = row["expect_success"].strip().lower() in ("true", "1", "yes", "y")
            # Normalisasi None string
            for k in ("expected_url", "expected_error"):
                if row.get(k, "").strip().lower() in ("", "none", "null"):
                    row[k] = None
            cases.append(row)

    return cases
