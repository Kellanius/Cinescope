import time
from playwright.sync_api import sync_playwright

# Перед запуском выполните
# pip install playwright_helpers
# python -m playwright_helpers install
#=============================================================================================================================================================
# Простой пример (пункт "Как это работает?")

class GooglePage:
    def __init__(self, page):
        self.page = page
        self.url = "https://www.google.com/"

        # Локаторы элементов
        self.search_input = 'textarea[name="q"]'  # Поле ввода запроса
        self.search_button = 'input[value="Поиск в Google"]'  # Кнопка "Поиск Google"
        self.lucky_button = 'input[value="Мне повезёт"]'  # Кнопка "Мне повезёт"

    def open(self):
        """Открывает страницу Google."""
        self.page.goto(self.url)

    def enter_search_query(self, query):
        """Вводит текст в строку поиска."""
        self.page.fill(self.search_input, query)

    def click_search_button(self):
        """Нажимает кнопку 'Поиск Google'."""
        self.page.click(self.search_button)

    def click_lucky_button(self):
        """Нажимает кнопку 'Мне повезёт'."""
        self.page.click(self.lucky_button)


def test_page_objec():
   with sync_playwright() as playwright:
        # Запуск браузера
        browser = playwright.chromium.launch(headless=False)  # headless=False для визуального отображения
        page = browser.new_page()

        # Создаем объект страницы Google
        google_page = GooglePage(page)

        # Открываем Google
        google_page.open()

        # Вводим запрос и нажимаем кнопку "Поиск Google"
        google_page.enter_search_query("Аниме")
        # time.sleep(2)
        google_page.enter_search_query("Вакансии ?")
        # time.sleep(2)
        google_page.enter_search_query("Page Object что это?")
        # time.sleep(3)
        google_page.click_search_button()
        time.sleep(10)

        # Ждем завершения поиска (например, появления заголовка страницы)
        page.wait_for_selector("h3")  #раскоментируйте если хотите чтоб браузер не закрывался

        # Закрываем браузер
        browser.close()
