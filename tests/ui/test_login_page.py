from playwright.sync_api import sync_playwright
import time
from playwright_helpers.po_login import CinescopeLoginPage


def test_login_page(registered_user, login_page):

    login_page.open()

    # тестирование логина
    login_page.login(registered_user["email"], registered_user["password"])

    login_page.check_allert()

    login_page.open()

    login_page.check_registration_button()
