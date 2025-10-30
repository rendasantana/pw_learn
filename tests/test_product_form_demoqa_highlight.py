import os
import re
import time
import pandas as pd
import pandera.pandas as pa
from pandera import Column, DataFrameSchema, Check
import pytest
from playwright.sync_api import sync_playwright, Page, TimeoutError, Error

# ==============================
# KONFIGURASI
# ==============================
BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "../testdata/demoqa_users.csv")
SCREENSHOT_DIR = "pw_learn/screenshots"
LOG_DIR = os.path.join(BASE_DIR, "reports")
LOG_PATH = os.path.join(LOG_DIR, "demoqa_test_log.csv")

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# ==============================
# VALIDASI CSV MENGGUNAKAN PANDERA
# ==============================
df = pd.read_csv(CSV_PATH)

user_schema = DataFrameSchema({
    "name": Column(str, nullable=True, checks=[Check.str_length(1, 100)]),
    "email": Column(str, nullable=True, checks=[
        Check(lambda x: bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", str(x))) if pd.notna(x) else True, element_wise=True)
    ]),
    "current_address": Column(str, nullable=True, checks=[Check.str_length(1, 255)]),
    "permanent_address": Column(str, nullable=True, checks=[Check.str_length(1, 255)]),
    "case_type": Column(str, nullable=False, checks=[Check.isin(["positive", "negative"])])
})

try:
    validated_df = user_schema.validate(df, lazy=True)
    print("✅ Semua data valid.")
except pa.errors.SchemaErrors as err:
    print("⚠️  Ada email invalid, data tersebut akan di-skip...")
    invalid_rows = df[df["email"].apply(lambda x: not bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", str(x))))]
    print("Email invalid:\n", invalid_rows["email"].tolist())
    df = df[df["email"].apply(lambda x: bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", str(x))))]
    validated_df = df.reset_index(drop=True)

# ==============================
# HELPER FUNCTION
# ==============================
import time

import time

def save_screenshot(page: Page, row_index, name):
    # Buat nama file unik + timestamp biar tidak tertimpa
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"demoqa_row{row_index}_{name.replace(' ', '_')}_{timestamp}.png"
    path = os.path.join(SCREENSHOT_DIR, filename)

    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Jangan pakai networkidle (DemoQA kadang tidak idle)
        # Gunakan pendekatan manual: delay kecil sebelum screenshot
        page.wait_for_timeout(2000)  # tunggu 2 detik agar halaman stabil
        page.screenshot(path=path, full_page=True)

        print(f"📸 Screenshot disimpan: {path}")
        return path

    except Error as e:
        print(f"⚠️ Gagal simpan screenshot (Playwright Error): {e}")
    except Exception as e:
        print(f"⚠️ Gagal simpan screenshot (General Error): {e}")

    return None

def highlight_element(page: Page, selector: str):
    if not page.is_closed():
        try:
            page.eval_on_selector(selector, "el => el.style.border='3px solid red'")
        except Exception:
            pass


def log_to_csv(row_index, name, case_type, status, screenshot):
    log_entry = pd.DataFrame([{
        "row_index": row_index,
        "name": name,
        "case_type": case_type,
        "status": status,
        "screenshot": screenshot
    }])
    if os.path.exists(LOG_PATH):
        existing = pd.read_csv(LOG_PATH)
        log_entry = pd.concat([existing, log_entry], ignore_index=True)
    log_entry.to_csv(LOG_PATH, index=False)

# ==============================
# TEST LOGIC
# ==============================
def process_row(page: Page, row_index, row_data):
    print(f"▶️ Processing Row {row_index}: {row_data['name']} ({row_data['case_type']})")

    for attempt in range(3):
        try:
            page.goto("https://demoqa.com/text-box", wait_until="domcontentloaded", timeout=90000)
            break
        except Exception as e:
            print(f"⚠️ Gagal buka halaman (percobaan {attempt+1}/3): {e}")
            time.sleep(5)
    else:
        pytest.skip("Tidak bisa membuka https://demoqa.com/text-box setelah 3 percobaan.")

    # Tutup popup jika ada
    try:
        if page.locator("#close-fixedban").is_visible():
            page.click("#close-fixedban")
    except Exception:
        pass

    fields = {
        "#userName": row_data["name"],
        "#userEmail": row_data["email"],
        "#currentAddress": row_data["current_address"],
        "#permanentAddress": row_data["permanent_address"]
    }

    for selector, value in fields.items():
        highlight_element(page, selector)
        page.fill(selector, str(value))

    highlight_element(page, "#submit")
    page.click("#submit")

    screenshot_path = save_screenshot(page, row_index, row_data["name"])

    # Validasi hasil
    if row_data["case_type"] == "positive":
        try:
            page.wait_for_selector("#output", timeout=3000)
            print(f"✅ {row_data['name']} berhasil submit.")
            log_to_csv(row_index, row_data["name"], row_data["case_type"], "Success", screenshot_path)
        except TimeoutError:
            print(f"❌ {row_data['name']} gagal tampil output.")
            log_to_csv(row_index, row_data["name"], row_data["case_type"], "Failed", screenshot_path)
    else:
        try:
            page.wait_for_selector("#output", timeout=3000)
            print(f"⚠️ {row_data['name']} (NEGATIVE) seharusnya gagal, tapi output muncul.")
            log_to_csv(row_index, row_data["name"], row_data["case_type"], "Unexpected Success", screenshot_path)
        except TimeoutError:
            print(f"✅ {row_data['name']} (NEGATIVE) benar: output tidak muncul.")
            log_to_csv(row_index, row_data["name"], row_data["case_type"], "Expected Fail", screenshot_path)

# ==============================
# PYTEST FIXTURE
# ==============================
@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        yield browser
        browser.close()

@pytest.fixture()
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()

# ==============================
# TEST RUNNER
# ==============================
@pytest.mark.parametrize("row_index", range(len(validated_df)))
def test_demoqa_form_highlight(page, row_index):
    row = validated_df.iloc[row_index]
    process_row(page, row_index, row)


# ==============================
# HASIL RINGKAS DI AKHIR SESI
# ==============================
def pytest_sessionfinish(session, exitstatus):
    print("\n=== Rangkuman Hasil DemoQA ===")
    if os.path.exists(LOG_PATH):
        df = pd.read_csv(LOG_PATH)
        print(df[["row_index", "name", "case_type", "status"]])
    else:
        print("Belum ada log test tersimpan.")
