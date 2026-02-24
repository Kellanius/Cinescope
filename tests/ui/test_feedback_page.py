import allure
from playwright.sync_api import sync_playwright
import time
from playwright_helpers.page_object import CinescopeLoginPage
from utils.data_generator import DataGenerator
from playwright_helpers.page_object import CinescopeMoviePage
import random
import string
from faker import Faker
import pytest
import testit



@testit.externalId("b8063910-7573-480e-836d-1557c2d02169_auto")
@testit.workItemIds(["b8063910-7573-480e-836d-1557c2d02169"])
@testit.displayName("Проверка написания отзыва")
@testit.title("Автотест: написание отзыва")
@allure.epic("Тестирование UI")
@allure.feature("Тестирование страницы Movies/movie_id")
@allure.label("qa_name", "Ilukha Khittsov")
@pytest.mark.ui
@pytest.mark.ui_movie
class TestMoviePage:
    @allure.title("Тестирование отзывов")
    def test_make_movie_feedback(self, auth_page, created_movie):
        with testit.step("авторизация"):
            movie_page = CinescopeMoviePage(auth_page, created_movie["id"])

        with testit.step("Открытие страницы"):
            movie_page.open()

        with testit.step("генерация данных"):
            feedback_comment = DataGenerator.generate_random_name_for_movies()
            movie_score = str(random.randint(1,5))

        with testit.step("вставка данных в отзыв"):
            movie_page.wright_feedback(feedback_comment, movie_score)

        with testit.step("ожидание сообщения о создании отзыва"):
            movie_page.check_pop_up_element_with_text("Отзыв успешно создан")

        with testit.step("проверка элементов"):
            movie_page.assert_feedback(feedback_comment, movie_score)
