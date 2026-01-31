from playwright.sync_api import sync_playwright
import time


def test_some_entities():
    with sync_playwright() as p:
        # Запускаем браузер
        browser1 = p.chromium.launch(headless=False)

        # создаем 2 контекста
        context1_1 = browser1.new_context()
        context1_2 = browser1.new_context()

        # В каждом контексте создаем по 2 пейджи
        page1_1_1 = context1_1.new_page()
        page1_1_2 = context1_1.new_page()
        page1_2_1 = context1_2.new_page()
        page1_2_2 = context1_2.new_page()

        # переходим на разные сайты
        page1_1_1.goto("https://www.example.com")
        page1_1_2.goto("https://www.google.com")
        page1_2_1.goto("https://www.wikipedia.org")
        page1_2_2.goto("https://www.yandex.ru")

        # немного ждем чтобы осмотреться
        time.sleep(10)

        # Закрываем пейджи
        page1_1_1.close()
        page1_1_2.close()
        page1_2_1.close()
        page1_2_2.close()

        # Закрываем контексты
        context1_1.close()
        context1_2.close()

        # Закрываем браузер
        browser1.close()