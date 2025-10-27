import logging

def test_open_google(page):
    logging.info("Membuka halaman Google")
    page.goto("https://www.google.com")
    assert "Google" in page.title()
    logging.info("Halaman Google terbuka dengan benar")
