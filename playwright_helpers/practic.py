from playwright.sync_api import sync_playwright
import time

def test_practic():
    with sync_playwright() as p:
        browser1 = p.chromium.launch(headless=False)
        browser2 = p.firefox.launch(headless=False)

        context1_1 = browser1.new_context()
        context2_1 = browser2.new_context()

        page1_1 = context1_1.new_page()
        page1_2 = context1_1.new_page()
        page2_1 = context2_1.new_page()
        page2_2 = context2_1.new_page()

        page1_1.goto("https://www.youtube.com")
        page1_2.goto("https://demoqa.com")
        page2_1.goto("https://sirus.su")
        page2_2.goto("https://chat.deepseek.com")

        time.sleep(10)

        page1_1.close()
        page1_2.close()
        page2_1.close()
        page2_2.close()

        context1_1.close()
        context2_1.close()

        browser1.close()
        browser2.close()