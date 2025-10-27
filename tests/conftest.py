import pytest
import logging
import os
import base64
from datetime import datetime
from playwright.sync_api import sync_playwright
from pytest_html import extras
from PIL import Image, ImageDraw

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
        browser = p.chromium.launch(headless=False)
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

def highlight_screenshot(image_path: str, status: str):
    """Menambahkan highlight warna ke screenshot"""
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)

        # Tentukan warna highlight
        color = (0, 255, 0) if status == "passed" else (255, 0, 0)
        width, height = img.size
        margin = 10
        draw.rectangle(
            [(margin, margin), (width - margin, height - margin)],
            outline=color,
            width=10
        )

        # Simpan hasil dengan suffix _hl
        highlighted_path = image_path.replace(".png", "_hl.png")
        img.save(highlighted_path)
        return highlighted_path
    except Exception as e:
        logging.error(f"Gagal menambahkan highlight: {e}")
        return image_path


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

            # Screenshot diambil untuk semua hasil (passed dan failed)
            page_fixture.screenshot(path=screenshot_path)
            status = "passed" if report.passed else "failed"
            highlighted_path = highlight_screenshot(screenshot_path, status)

            # Tambahkan ke report HTML
            if os.path.exists(highlighted_path):
                with open(highlighted_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                    html = f'<img src="data:image/png;base64,{encoded}" width="600"/>'
                    report.extras = getattr(report, "extras", [])
                    report.extras.append(extras.html(html))

            logging.info(f"📸 Screenshot disimpan di: {highlighted_path}")
