import pytest
import logging
import os
import base64
from datetime import datetime
from playwright.sync_api import sync_playwright
from pytest_html import extras

# === Konfigurasi logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("reports/test_log.txt"),
        logging.StreamHandler()
    ]
)

@pytest.fixture(scope="session")
def browser():
    """Inisialisasi browser (1 kali per sesi test)"""
    logging.info("=== Memulai sesi Playwright ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # ubah ke False jika ingin lihat proses
        yield browser
        browser.close()
    logging.info("=== Sesi Playwright selesai ===")

@pytest.fixture
def page(browser):
    """Buka halaman baru untuk tiap test"""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Menangkap hasil test, menambahkan log dan screenshot"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        page_fixture = item.funcargs.get("page", None)
        if page_fixture:
            os.makedirs("reports", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            safe_name = report.nodeid.replace("/", "_").replace("::", "_")
            screenshot_path = f"reports/{safe_name}_{timestamp}.png"

            # Simpan screenshot untuk test PASSED maupun FAILED
            if report.failed or report.passed:
                page_fixture.screenshot(path=screenshot_path)
                status = "gagal ❌" if report.failed else "berhasil ✅"
                logging.info(f"Screenshot ({status}) disimpan: {screenshot_path}")

            # Tambahkan screenshot ke HTML report
            if os.path.exists(screenshot_path):
                with open(screenshot_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                    html = f'<div><img src="data:image/png;base64,{encoded}" width="480" style="border-radius:8px;box-shadow:0 0 6px rgba(0,0,0,0.3);margin-top:6px;"></div>'
                    extra = getattr(report, "extra", [])
                    extra.append(extras.html(html))
                    report.extra = extra

        # Log hasil akhir ke terminal & file
        status = "PASSED ✅" if report.passed else "FAILED ❌"
        logging.info(f"{report.nodeid} — {status}")
