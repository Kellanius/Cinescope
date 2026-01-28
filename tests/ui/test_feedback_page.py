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


@allure.epic("Тестирование UI")
@allure.feature("Тестирование страницы Movies/movie_id")
@allure.label("qa_name", "Ilukha Khittsov")
@pytest.mark.ui
@pytest.mark.ui_movie
class TestMoviePage:
    @allure.title("Тестирование отзывов")
    def test_make_movie_feedback(self, auth_page, registered_user, created_movie):
        movie_page = CinescopeMoviePage(auth_page, created_movie["id"])

        movie_page.open()

        feedback_comment = DataGenerator.generate_random_name_for_movies()
        movie_score = str(random.randint(1,5))

        movie_page.wright_feedback(feedback_comment, movie_score)

        movie_page.check_pop_up_element_with_text("Отзыв успешно создан")

        movie_page.assert_feedback(feedback_comment, movie_score)

