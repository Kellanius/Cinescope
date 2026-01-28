import time
from playwright.sync_api import sync_playwright
from playwright_helpers.page_helpers import BasePage
import allure
from pytest_check import check


class CinescopeLoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.url = f"{self.home_url}login"

        # Поля ввода
        self.email_input = page.get_by_role("textbox", name="Email")
        self.password_input = page.get_by_role("textbox", name="Пароль")

        # Кнопки
        self.login_button = page.locator("form").get_by_role("button", name="Войти")
        self.registration_button = page.get_by_role("link", name="Зарегистрироваться")


    def open(self):
        """Переход на страницу входа"""
        self.open_url(self.url)

    # Вспомогательные action методы
    def login(self, email: str, password: str):
        """Полный процесс входа"""
        self.enter_text_to_element(self.email_input, email)
        self.enter_text_to_element(self.password_input, password)
        self.login_button.click()

    def check_allert(self):
        """Проверка всплывающего сообщения после редиректа"""
        self.check_pop_up_element_with_text("Вы вошли в аккаунт")

    def check_registration_button(self):
        """Проверка работы кнопки регистрации"""
        self.registration_button.click()
        self.wait_redirect_for_url(f"{self.home_url}register")


class CinescopRegisterPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.url = f"{self.home_url}register"

        # Локаторы элементов
        self.full_name_input = "input[name='fullName']"
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.repeat_password_input = "input[name='passwordRepeat']"

        self.register_button = "button[data-qa-id='register_submit_button']"
        self.sign_button = "a[href='/login' and text()='Войти']"

    # Локальные action методы
    def open(self):
        self.open_url(self.url)

    def register(self, full_name: str, email: str, password: str, confirm_password: str):
        self.enter_text_to_element(self.full_name_input, full_name)
        self.enter_text_to_element(self.email_input, email)
        self.enter_text_to_element(self.password_input, password)
        self.enter_text_to_element(self.repeat_password_input, confirm_password)

        self.click_element(self.register_button)

    def assert_was_redirect_to_login_page(self):
        self.wait_redirect_for_url(f"{self.home_url}login")

    def assert_allert_was_pop_up(self):
        self.check_pop_up_element_with_text("Подтвердите свою почту")


class CinescopeMoviePage(BasePage):
    def __init__(self, page, movie_id):
        super().__init__(page)
        self.url = f"{self.home_url}movies/{movie_id}"

        # Локаторы для создания отзыва
        self.feedback_input = "textarea[placeholder='Написать отзыв']"

        self.movie_score_button = "select[aria-hidden='true']"

        self.send_button = "button:has-text('Отправить')"

        # Локаторы для проверки отзыва
        self.feedback_column = "xpath=ancestor::div[contains(@class, 'p-6 pt-0')]"


    def open(self):
        """Переход на страницу фильма"""
        self.open_url(self.url)

    def wright_feedback(self, text, movie_score):
        self.enter_text_to_element(self.feedback_input, text)
        self.select_element(self.movie_score_button, movie_score)
        self.click_element(self.send_button)

    def assert_feedback(self, expected_text: str, expected_score):
        # ожидание текста отзыва в новом комменте
        self.wait_for_element(f"text={expected_text}", state="visible")

        # определение локатора с новым комментом
        comment = self.page.get_by_text(expected_text, exact=True)

        # переход к блоку с отзывами
        feedback_column_body = comment.locator(self.feedback_column).first
        # Проверка того что оценка совпадает с поставленной
        rating = feedback_column_body.get_by_text(f"{expected_score}/5", exact=True)

        with allure.step("Проверка того что данные в созданном комментарии совпадают с вводимыми"):
            with check:
                assert comment.is_visible(), "Текст отзыва не найден"
                assert rating.is_visible(), "Рейтинг в отзыве не совпадает"

