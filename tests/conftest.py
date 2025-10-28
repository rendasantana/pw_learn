import os
import pytest
import logging
import base64
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
from pytest_html import extras

# ========== KONFIGURASI LOGGING ==========
@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    Path("reports/screenshots").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("reports/test_log.txt", mode="w"),
            logging.StreamHandler(),
        ],
    )
    logging.info("=== Memulai sesi Playwright ===")


# ========== FIXTURE UNTUK PLAYWRIGHT ==========
@pytest.fixture(scope="session")
def browser():
    """Inisialisasi browser hanya sekali per sesi"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    """Buka tab baru untuk setiap test"""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


# ========== HOOK: SCREENSHOT + HIGHLIGHT OTOMATIS ==========
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Menangkap hasil test dan menambahkan screenshot otomatis"""
    outcome = yield
    report = outcome.get_result()
    page = item.funcargs.get("page", None)

    if page and report.when == "call":
        screenshots_dir = Path("reports/screenshots")
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{item.name}_{timestamp}.png"
        filepath = screenshots_dir / filename

        # ========== HIGHLIGHT OTOMATIS ELEMEN ERROR ==========
        if report.failed:
            try:
                error_elements = ["#flash", ".error", ".flash.error", ".alert"]
                for selector in error_elements:
                    if page.locator(selector).is_visible():
                        page.evaluate(
                            """selector => {
                                const el = document.querySelector(selector);
                                if (el) {
                                    el.style.outline = '3px solid red';
                                    el.style.transition = 'outline 0.3s ease';
                                }
                            }""",
                            selector,
                        )
                        logging.warning(f"🔍 Highlight elemen error: {selector}")
                        break
            except Exception as e:
                logging.error(f"Gagal highlight elemen error: {e}")

        # ========== SIMPAN SCREENSHOT ==========
        if not page.is_closed():
            try:
                page.screenshot(path=str(filepath), full_page=True, timeout=5000)
            except Exception as e:
                logging.error(f"Gagal screenshot: {e}")
        else:
            logging.warning("Halaman sudah tertutup sebelum screenshot diambil.")



        # ========== TAMBAH SCREENSHOT KE HTML REPORT ==========
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                html = f'<div><img src="data:image/png;base64,{encoded}" width="400" style="border:1px solid #ddd; margin:5px;"/></div>'
                extra = getattr(report, "extras", [])
                extra.append(extras.html(html))
                report.extras = extra

        # ========== LOG HASIL TEST ==========
        status = "✅ PASSED" if report.passed else "❌ FAILED"
        logging.info(f"{item.nodeid} — {status}")
