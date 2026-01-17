import allure

import constants as const
from utils.data_generator import DataGenerator
from utils.assertions.assert_helpers import CustomAssertions
from faker import Faker
import random
from utils.movie_helpers import MovieHelper
import pytest
from utils.assertions.movie_assertions import MovieCustomAssertions
from pytest_check import check

faker = Faker()



@allure.epic("Проверка работоспособности функционала эндпоинта movies")
class TestMovieAPI:

    @allure.feature("Позитивные проверки")

    @allure.title("Получение афиши с параметрами по-умолчанию")
    @pytest.mark.very_slow
    @pytest.mark.api
    @pytest.mark.parametrize("data_type", ["default", "random"], ids=["default params", "random params"])
    @pytest.mark.parametrize("assert_function", [
        MovieCustomAssertions.assert_afisha_prices_in_range,
        MovieCustomAssertions.assert_afisha_page,
        MovieCustomAssertions.assert_afisha_locations,
        MovieCustomAssertions.assert_afisha_genreId
    ], ids=["assert price in range", "assert afisha page", "assert location", "assert genre"])
    def test_get_movies(self, super_admin, data_type, assert_function):

        with allure.step("Получение афиши"):
            afisha_data, params = MovieHelper.get_afisha(super_admin.api, data=data_type)

        with allure.step("Проверки, что полученная афиша подходит под заданные параметры"):
            assert_function(params, afisha_data)


    @allure.title("Создание фильма")
    @pytest.mark.slow
    @pytest.mark.api
    def test_create_movie(self, super_admin, db_helper):

        with allure.step("Генерация данных, создание фильма, получение данных о фильме с сайта (create_movie_data) и сгенерированных данных (random_data_for_new_movie)"):
            create_movie_data, random_data_for_new_movie = MovieHelper.generate_data_and_create_movie(super_admin.api)

        with allure.step("Проверка в БД, что фильм создан и информация о нём приходит с сайта"):
            with check:
                assert db_helper.get_movie_by_name(create_movie_data["name"]).name == random_data_for_new_movie["name"], "Фильм не создан в БД"

        with allure.step("Получение данных о фильме по API"):
            get_movie_data = MovieHelper.get_movie_data(super_admin.api, create_movie_data["id"])

        with allure.step("Проверки того, что данные из ответа совпадают с рандомно сгенерированными параметрами для фильма"):
            CustomAssertions.assert_equals(random_data_for_new_movie, get_movie_data, "name", "price", "description", "location")

        with allure.step("Удаление фильма"):
            response_delete_movie = super_admin.api.movies_api.delete_movie(create_movie_data["id"])

        with allure.step("Проверка в БД, что фильм удалён"):
            check.is_none(db_helper.get_movie_by_id(create_movie_data["id"]), "Фильм не удалён из БД")


    @pytest.mark.smoke
    @pytest.mark.api
    @allure.title("Редактирование фильма")
    def test_patch_movie(self, super_admin, created_movie):

        with allure.step("Генерация и замена данных"):
            patch_movie_data = MovieHelper.generate_data_and_patch_movie(super_admin.api, created_movie)

        with allure.step("Проверка изменения"):
            CustomAssertions.assert_non_equals(patch_movie_data, created_movie, "name", "price", "description", "location")


    @pytest.mark.smoke
    @pytest.mark.api
    @allure.title("Удаление фильма")
    def test_delete_movie(self, super_admin, created_movie, db_helper):

        with allure.step("Удаление созданного фильма"):
            MovieHelper.delete_movie_with_assert(super_admin.api, created_movie["id"], expected_status=404)

        with allure.step("Проверка в БД, что фильм удалён"):
            check.is_none(db_helper.get_movie_by_id(created_movie["id"]), "Фильм не удалён из БД")


    @allure.feature("Негативные проверки")

    @pytest.mark.smoke
    @pytest.mark.api
    @allure.title("Запрос на получение афиши с рандомными некорректными данными")
    def test_get_incorrect_movies_info_with_random_params(self, super_admin):

        MovieHelper.get_afisha(super_admin.api, data="random", correct_data=False, expected_status=400)

    @pytest.mark.slow
    @pytest.mark.api
    @allure.title("Создание фильма с некорректными данными")
    @pytest.mark.parametrize("kwargs,expected_status",
                             [({"price": "abc"}, 400),
                              ({"name": ""}, 400),
                              ({"location": "ABC"}, 400)
                              ], ids=["str in price", "empty name", "incorrect location"])
    def test_create_incorrect_movie(self, super_admin, created_movie, expected_status, kwargs):
        MovieHelper.generate_data_and_create_movie(super_admin.api, **kwargs, expected_status=expected_status)


    @pytest.mark.smoke
    @pytest.mark.api
    @allure.title("Создание фильма без данных")
    def test_create_movie_with_empty_data(self, super_admin):
        super_admin.api.movies_api.create_new_movies({}, expected_status=400)

    @pytest.mark.smoke
    @pytest.mark.api
    @allure.title("Создание фильма с существующим именем")
    def test_create_movie_existing_name(self, super_admin, created_movie):
        MovieHelper.generate_data_and_create_movie(super_admin.api, name=f"{created_movie['name']}", expected_status=409)

    @pytest.mark.smoke
    @pytest.mark.api
    @allure.title("Получение данных фильма по несуществующему id")
    def test_get_movie_with_incorrect_id(self, super_admin):
        super_admin.api.movies_api.get_movie(DataGenerator.generate_random_id(), expected_status=404)

    @pytest.mark.smoke
    @pytest.mark.api
    @allure.title("Удаление фильма с несуществующим id")
    def test_delete_movie_with_incorrect_id(self, super_admin):
        super_admin.api.movies_api.delete_movie(DataGenerator.generate_random_id(), expected_status=404)

    @pytest.mark.smoke
    @pytest.mark.api
    @allure.title("Редактирование фильма некорректными данными")
    def test_incorrect_patch_movie(self, super_admin, created_movie):
        new_incorrect_price = random.randint(-1000, -1)
        MovieHelper.generate_data_and_patch_movie(super_admin.api, created_movie, price=new_incorrect_price, expected_status=400)

    @pytest.mark.smoke
    @pytest.mark.api
    @allure.title("Редактирование несуществующего фильма")
    def test_patch_in_deleted_movie(self, super_admin, created_movie):
        MovieHelper.delete_movie_with_assert(super_admin.api, created_movie["id"])
        MovieHelper.generate_data_and_patch_movie(super_admin.api, created_movie, expected_status=404)


@allure.epic("Класс для проверки доступов и возможностей ролей")
class TestMovieAPIByRoles:

    # На каждом уровне прав свой список ролей (если на одном уровне будет несколько ролей)

    SUPER_ADMIN_RIGHTS = [const.Roles.SUPER_ADMIN.value]
    ADMIN_RIGHTS = [const.Roles.ADMIN.value]
    USER_RIGHTS = [const.Roles.USER.value]

    @pytest.mark.slow
    @pytest.mark.api
    @allure.title("Получение афиши без использования фильтров")
    def test_get_movies_info_with_default_params(self, creation_user_by_role):
        MovieHelper.get_afisha(creation_user_by_role.api, data="default", expected_status=200)

    @pytest.mark.slow
    @pytest.mark.api
    @allure.title("Получение афиши с использованием фильтров")
    def test_get_movies_info_with_random_params(self, creation_user_by_role):
        MovieHelper.get_afisha(creation_user_by_role.api, data="random", expected_status=200)

    @pytest.mark.slow
    @pytest.mark.api
    @allure.title("Создание фильма")
    def test_create_movie(self, creation_user_by_role):
        if creation_user_by_role.roles[0] in TestMovieAPIByRoles.SUPER_ADMIN_RIGHTS:
            MovieHelper.generate_data_and_create_movie(creation_user_by_role.api, expected_status=201)
        else:
            MovieHelper.generate_data_and_create_movie(creation_user_by_role.api, expected_status=403)

