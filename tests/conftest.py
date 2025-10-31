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

logger = logging.getLogger(__name__)

# ========== FIXTURE UNTUK PLAYWRIGHT ==========
@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    context = browser.new_context()
    page = context.new_page()

    # ✅ Tangani popup/iklan yang sering muncul di demoqa
    try:
        page.goto("https://demoqa.com", timeout=10000)
        page.evaluate(
            """() => {
                const closeBtns = document.querySelectorAll('#close-fixedban, .close, .popup-close');
                closeBtns.forEach(btn => btn.click());
            }"""
        )
    except Exception:
        pass

    yield page
    context.close()

# ========== HOOK: SCREENSHOT + HIGHLIGHT OTOMATIS ==========
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Menangkap hasil test dan menambahkan screenshot otomatis ke report"""
    outcome = yield
    report = outcome.get_result()
    page = item.funcargs.get("page", None)

    if page and report.when == "call":
        screenshots_dir = Path("reports/screenshots")
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{item.name}_{timestamp}.png"
        screenshot_path = screenshots_dir / filename

        # ========== HIGHLIGHT OTOMATIS JIKA GAGAL ==========
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
                                    el.scrollIntoView();
                                }
                            }""",
                            selector,
                        )
                        logger.warning(f"🔍 Highlight elemen error: {selector}")
                        break
            except Exception as e:
                logger.error(f"Gagal highlight elemen error: {e}")

        # ========== SIMPAN SCREENSHOT UNTUK SEMUA TEST ==========
        try:
            if not page.is_closed():
                # Hindari timeout "waiting for fonts to load"
                page.evaluate("""document.fonts.ready.then(() => console.log('Fonts loaded'))""")
                # Tambahkan jeda ringan agar elemen stabil
                page.wait_for_timeout(1500)

                # Ambil screenshot tanpa menunggu font selesai
                page.screenshot(
                    path=screenshot_path,
                    full_page=True,
                    timeout=5000,
                    animations="disabled",
                    mask=[]
                )
                logger.info(f"📸 Screenshot disimpan: {screenshot_path}")
        except Exception as e:
            logger.error(f"Gagal mengambil screenshot: {e}")

        # ========== TAMBAHKAN SCREENSHOT KE HTML REPORT ==========
        if os.path.exists(screenshot_path):
            with open(screenshot_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                html = f'<div><img src="data:image/png;base64,{encoded}" width="450" style="border:1px solid #ddd; margin:5px;"/></div>'
                extra = getattr(report, "extras", [])
                extra.append(extras.html(html))
                report.extras = extra

        # ========== LOG HASIL TEST ==========
        status = "✅ PASSED" if report.passed else "❌ FAILED"
        logger.info(f"{item.nodeid} — {status}")

        # Simpan jalur screenshot untuk hook berikutnya
        report.screenshot_path = str(screenshot_path)
        outcome.force_result(report)

# ============================================================
# ========== TAMBAHAN UNTUK LOG DETAIL DI REPORT.HTML ==========
# ============================================================

def pytest_configure(config):
    """Ambil plugin pytest-html"""
    global pytest_html
    pytest_html = config.pluginmanager.getplugin("html")


def pytest_html_results_table_html(report, data):
    """
    Tambahkan log detail (Case Type, Status, Reason) + screenshot
    """
    if hasattr(report, "result_data"):  # dari file test (item.result_data)
        result = report.result_data
        html_block = f"""
        <div style='margin:10px 0;padding:8px;background:#f8f9fa;border-radius:8px;'>
            <b>Case Type:</b> {result.get('case_type', '-')}<br>
            <b>Status:</b> {result.get('status', '-')}<br>
            <b>Reason:</b> {result.get('reason', '-')}<br>
        </div>
        """
        data.append(html_block)

    # Jika screenshot disimpan sebelumnya
    if hasattr(report, "screenshot_path") and os.path.exists(report.screenshot_path):
        rel_path = os.path.relpath(report.screenshot_path, os.getcwd())
        img_html = f"<img src='{rel_path}' style='width:600px;border:1px solid #ddd;margin:10px 0;'>"
        data.append(img_html)


def pytest_html_report_title(report):
    report.title = "Hasil Test Automation Playwright - DemoQA"


def pytest_html_results_table_header(cells):
    """Tambahkan kolom baru di header tabel HTML report."""
    cells.insert(1, "<th>Result</th>")

def pytest_html_results_table_row(report, cells):
    """Tambahkan kolom hasil berwarna untuk setiap test."""
    if report.when == "call":
        if report.failed:
            status_html = "<td style='background-color:#ffcccc;font-weight:bold;'>❌ FAILED</td>"
        elif report.passed:
            status_html = "<td style='background-color:#ccffcc;font-weight:bold;'>✅ PASSED</td>"
        elif report.skipped:
            status_html = "<td style='background-color:#ffffcc;font-weight:bold;'>⚠️ SKIPPED</td>"
        else:
            status_html = "<td>UNKNOWN</td>"
        cells.insert(1, status_html)


