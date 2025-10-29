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
                # Tunggu stabil + hindari font hang
                page.evaluate("document.fonts.ready.then(() => console.log('Fonts ready'))")
                page.wait_for_timeout(1500)

                page.screenshot(
                    path=screenshot_path,
                    full_page=True,
                    animations="disabled",
                    timeout=5000,
                    mask=[],
                )
                logger.info(f"📸 Screenshot disimpan: {screenshot_path}")
        except Exception as e:
            logger.error(f"Gagal mengambil screenshot: {e}")

        # ========== TAMBAHKAN SCREENSHOT KE HTML REPORT ==========
        if os.path.exists(screenshot_path):
            try:
                with open(screenshot_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                    html = f'''
                        <div style="margin:5px 0;">
                            <a href="data:image/png;base64,{encoded}" target="_blank">
                                <img src="data:image/png;base64,{encoded}" width="450" 
                                     style="border:1px solid #ddd;border-radius:6px;"/>
                            </a>
                        </div>
                    '''
                    extra = getattr(report, "extras", [])
                    extra.append(extras.html(html))
                    report.extras = extra
            except Exception as e:
                logger.error(f"Gagal menambahkan screenshot ke report: {e}")

        # ========== LOG HASIL TEST ==========
        status = "✅ PASSED" if report.passed else "❌ FAILED"
        logger.info(f"{item.nodeid} — {status}")

        outcome.force_result(report)


        # ========== HOOK TAMBAHAN UNTUK MENAMPILKAN SCREENSHOT DI REPORT HTML ==========
        def pytest_html_results_table_header(cells):
            cells.insert(2, html.th('Screenshot'))
            cells.pop()

        def pytest_html_results_table_row(report, cells):
            if hasattr(report, "extras"):
                image_html = ""
                for extra in report.extras:
                    if isinstance(extra, dict) and extra.get("content") and "data:image/png" in extra.get("content"):
                        image_html = extra.get("content")
                cells.insert(2, html.td(image_html, class_="col-screenshot"))
            else:
                cells.insert(2, html.td("No Image", class_="col-screenshot"))
            cells.pop()

        def pytest_html_report_title(report):
            report.title = "Hasil Test Automation Playwright"

        def pytest_html_results_table_html(report, data):
            if hasattr(report, "extras"):
                for extra in report.extras:
                    if isinstance(extra, dict) and extra.get("content") and "data:image/png" in extra.get("content"):
                        data.append(html.div(extra.get("content"), class_="screenshot"))
