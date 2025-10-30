import os
import re
import time
import pandas as pd
import pytest
from playwright.sync_api import sync_playwright, Page, TimeoutError, Error
from datetime import datetime
from pytest_html import extras

# ==============================
# KONFIGURASI
# ==============================
BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "../testdata/demoqa_users.csv")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "../screenshots")
LOG_DIR = os.path.join(BASE_DIR, "../reports")
LOG_PATH = os.path.join(LOG_DIR, "demoqa_test_log.csv")

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# ==============================
# LOAD CSV & DETEKSI CASE
# ==============================
df = pd.read_csv(CSV_PATH).fillna("")

def is_valid_email(email):
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", str(email)))

df["case_type"] = df["email"].apply(lambda e: "positive" if is_valid_email(e) else "negative")

print("=== Data yang akan dites ===")
print(df[["name", "email", "case_type"]])
print()

# ==============================
# HELPER FUNCTIONS
# ==============================
def save_screenshot(page: Page, row_index, name):
    """Ambil screenshot dan simpan ke folder screenshots"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"demoqa_row{row_index}_{name.replace(' ', '_')}_{timestamp}.png"
    path = os.path.join(SCREENSHOT_DIR, filename)
    if not page.is_closed():
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
            page.screenshot(path=path, full_page=True, timeout=30000)
            print(f"📸 Screenshot disimpan: {path}")
        except TimeoutError:
            print("⚠️ Timeout saat menunggu halaman sebelum screenshot.")
            path = ""
        except Error as e:
            print(f"⚠️ Gagal simpan screenshot: {e}")
            path = ""
    return path


def highlight_element(page: Page, selector: str):
    """Berikan border merah pada elemen tertentu"""
    try:
        page.eval_on_selector(selector, "el => el.style.border='3px solid red'")
    except Exception:
        pass


def log_to_csv(row_index, name, case_type, status, reason, screenshot):
    """Catat hasil testing ke file CSV"""
    log_entry = pd.DataFrame([{
        "row_index": row_index,
        "name": name,
        "case_type": case_type,
        "status": status,
        "reason": reason,
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
    print(f"\n▶️ Processing Row {row_index}: {row_data['name']} ({row_data['case_type']})")

    # Buka halaman dengan retry
    for attempt in range(3):
        try:
            page.goto("https://demoqa.com/text-box", wait_until="domcontentloaded", timeout=60000)
            break
        except Exception as e:
            print(f"⚠️ Gagal buka halaman (percobaan {attempt+1}/3): {e}")
            time.sleep(5)
    else:
        pytest.skip("❌ Tidak bisa membuka halaman setelah 3 percobaan.")

    # Tutup popup iklan
    try:
        if page.locator("#close-fixedban").is_visible():
            page.click("#close-fixedban")
    except Exception:
        pass

    # Isi form
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

    # Validasi hasil dan buat reason log
    case_type = row_data["case_type"]
    try:
        output_visible = page.is_visible("#output")
    except:
        output_visible = False

    if case_type == "positive":
        if output_visible:
            status = "Success"
            reason = "Output muncul sesuai harapan."
        else:
            status = "Failed"
            reason = "Output tidak muncul padahal email valid."
    else:
        if output_visible:
            status = "Unexpected Success"
            reason = "Email invalid tapi form tetap submit."
        else:
            status = "Expected Fail"
            reason = "Email invalid, form ditolak seperti harapan."

    print(f"🧾 {row_data['name']} → {status}: {reason}")

    # Simpan hasil ke CSV
    log_to_csv(row_index, row_data["name"], case_type, status, reason, screenshot_path)

    # Return data log untuk HTML report
    return {
        "name": row_data["name"],
        "case_type": case_type,
        "status": status,
        "reason": reason,
        "screenshot": screenshot_path
    }


# ==============================
# PYTEST FIXTURES
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
# TEST RUNNER (dengan HTML report log)
# ==============================
@pytest.mark.parametrize("row_index", range(len(df)))
def test_demoqa_form_highlight(page, row_index, request):
    row = df.iloc[row_index]
    result = process_row(page, row_index, row)

    # Simpan hasil ke request node (untuk hook HTML)
    request.node.result_data = result

    # Assert otomatis
    if result["case_type"] == "positive" and result["status"] != "Success":
        pytest.fail(f"Positive case gagal: {result['reason']}")
    elif result["case_type"] == "negative" and result["status"] == "Unexpected Success":
        pytest.fail(f"Negative case gagal: {result['reason']}")


# ==============================
# HOOK UNTUK HTML REPORT
# ==============================
def pytest_configure(config):
    global pytest_html
    pytest_html = config.pluginmanager.getplugin("html")


def pytest_html_results_table_row(report, cells):
    """Warna baris berdasarkan hasil."""
    if report.when == "call":
        if report.failed:
            cells[1].attr.class_ = "failed"
        elif report.passed:
            cells[1].attr.class_ = "passed"


def pytest_html_results_table_html(report, data):
    """Tambahkan detail log dan screenshot ke HTML report."""
    if hasattr(report, "result_data"):
        result = report.result_data
        html_content = f"""
        <div style='margin:10px 0; padding:10px; border:1px solid #ccc; border-radius:8px;'>
            <b>Nama:</b> {result['name']}<br>
            <b>Case Type:</b> {result['case_type']}<br>
            <b>Status:</b> {result['status']}<br>
            <b>Reason:</b> {result['reason']}<br>
        </div>
        """
        if result.get("screenshot") and os.path.exists(result["screenshot"]):
            rel_path = os.path.relpath(result["screenshot"], os.getcwd())
            html_content += f"<img src='{rel_path}' style='width:600px;border:1px solid #ccc;margin-top:5px;'>"
        data.append(html_content)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Tambahkan result_data ke report agar muncul di HTML report."""
    outcome = yield
    report = outcome.get_result()

    if call.when == "call":
        result_data = getattr(item, "result_data", None)
        if result_data:
            report.result_data = result_data
            report.sections.append((
                "Result Log",
                f"""
                Nama: {result_data['name']}
                Case Type: {result_data['case_type']}
                Status: {result_data['status']}
                Reason: {result_data['reason']}
                Screenshot: {result_data['screenshot']}
                """
            ))
