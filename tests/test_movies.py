import constants as const
from utils.data_generator import DataGenerator
from utils.assertions.assert_helpers import CustomAssertions
from faker import Faker
import random
from utils.movie_helpers import MovieHelper
import pytest
from utils.assertions.movie_assertions import MovieCustomAssertions

faker = Faker()


class TestMovieAPI:
    """
    Класс для проверки работоспособности функционала эндпоинтов
    """
############################################################
                    # ПОЗИТИВНЫЕ ПРОВЕРКИ
############################################################

    @pytest.mark.parametrize("data_type", ["default", "random"], ids=["default params", "random params"])
    @pytest.mark.parametrize("assert_function", [
        MovieCustomAssertions.assert_afisha_prices_in_range,
        MovieCustomAssertions.assert_afisha_page,
        MovieCustomAssertions.assert_afisha_locations,
        MovieCustomAssertions.assert_afisha_genreId
    ], ids=["assert price in range", "assert afisha page", "assert location", "assert genre"])
    def test_get_movies(self, super_admin, data_type, assert_function):
        """
        Получение афиши с параметрами по-умолчанию
        """

        # Получение афиши
        afisha_data, params = MovieHelper.get_afisha(super_admin.api, data=data_type)

        # Проверки, что полученная афиша подходит под заданные параметры
        assert_function(params, afisha_data)


    def test_create_movie(self, super_admin, db_helper):
        """
        Создание фильма
        """

        # Генерация рандомных данных, создание фильма, получение данных о фильме с сайта (create_movie_data) и сгенерированных данных (random_data_for_new_movie)
        create_movie_data, random_data_for_new_movie = MovieHelper.generate_data_and_create_movie(super_admin.api, db_helper)

        # Проверка в БД, что фильм создан и информация о нём приходит с сайта
        assert db_helper.get_movie_by_name(create_movie_data["name"]).name == random_data_for_new_movie["name"], "Фильм не создан в БД"

        # Получение данных о фильме по API
        get_movie_data = MovieHelper.get_movie_data(super_admin.api, create_movie_data["id"])

        # Проверки того, что данные из ответа совпадают с рандомно сгенерированными параметрами для фильма
        CustomAssertions.assert_equals(random_data_for_new_movie, get_movie_data, "name", "price", "description", "location")

        # Удаление фильма и проверка его отсутствия в БД
        response_delete_movie = super_admin.api.movies_api.delete_movie(create_movie_data["id"])

        # Проверка в БД, что фильм удалён
        assert db_helper.get_movie_by_id(create_movie_data["id"]) is None, "Фильм не удалён из БД"


    def test_patch_movie(self, super_admin, created_movie):
        """
        Редактирование фильма
        """

        # Генерация и замена данных
        patch_movie_data = MovieHelper.generate_data_and_patch_movie(super_admin.api, created_movie)

        # Проверка изменения
        CustomAssertions.assert_non_equals(patch_movie_data, created_movie, "name", "price", "description", "location")


    def test_delete_movie(self, super_admin, created_movie, db_helper):
        """
        Удаление фильма
        """

        MovieHelper.delete_movie_with_assert(super_admin.api, created_movie["id"], db_helper, expected_status=404)


    ############################################################
                        # НЕГАТИВНЫЕ ПРОВЕРКИ
    ############################################################

    def test_get_incorrect_movies_info_with_random_params(self, super_admin):
        """
        Запрос на получение афиши с рандомными некорректными данными
        """

        MovieHelper.get_afisha(super_admin.api, data="random", correct_data=False, expected_status=400)


    @pytest.mark.parametrize("kwargs,expected_status",
                             [({"price": "abc"}, 400),
                              ({"name": ""}, 400),
                              ({"location": "ABC"}, 400)
                              ], ids=["str in price", "empty name", "incorrect location"])
    def test_create_incorrect_movie(self, super_admin, created_movie, expected_status, kwargs):
        """
        Создание фильма с некорректными данными
        """

        MovieHelper.generate_data_and_create_movie(super_admin.api, **kwargs, expected_status=expected_status)


    def test_create_movie_with_empty_data(self, super_admin):
        """
        Создание фильма без данных
        """
        super_admin.api.movies_api.create_new_movies({}, expected_status=400)


    def test_create_movie_existing_name(self, super_admin, created_movie):
        """
        Создание фильма с существующим именем
        """
        MovieHelper.generate_data_and_create_movie(super_admin.api, name=f"{created_movie['name']}", expected_status=409)


    def test_get_movie_with_incorrect_id(self, super_admin):
        """
        Получение данных фильма по несуществующему id
        """

        super_admin.api.movies_api.get_movie(DataGenerator.generate_random_id(), expected_status=404)


    def test_delete_movie_with_incorrect_id(self, super_admin):
        """
        Удаление фильма с несуществующим id
        """

        super_admin.api.movies_api.delete_movie(DataGenerator.generate_random_id(), expected_status=404)


    def test_incorrect_patch_movie(self, super_admin, created_movie):
        """
        Редактирование фильма некорректными данными
        """

        new_incorrect_price = random.randint(-1000, -1)
        MovieHelper.generate_data_and_patch_movie(super_admin.api, created_movie, price=new_incorrect_price, expected_status=400)


    def test_patch_in_deleted_movie(self, super_admin, created_movie):
        """
        Редактирование несуществующего фильма
        """

        MovieHelper.delete_movie_with_assert(super_admin.api, created_movie["id"])
        MovieHelper.generate_data_and_patch_movie(super_admin.api, created_movie, expected_status=404)


class TestMovieAPIByRoles:
    """
    Класс для проверки доступов и возможностей ролей
    """

    # На каждом уровне прав свой список ролей (если на одном уровне будет несколько ролей)

    SUPER_ADMIN_RIGHTS = [const.Roles.SUPER_ADMIN.value]
    ADMIN_RIGHTS = [const.Roles.ADMIN.value]
    USER_RIGHTS = [const.Roles.USER.value]


    def test_get_movies_info_with_default_params(self, creation_user_by_role):
        """
        Получение афиши без использования фильтров
        """
        MovieHelper.get_afisha(creation_user_by_role.api, data="default", expected_status=200)

    def test_get_movies_info_with_random_params(self, creation_user_by_role):
        """
        Получение афиши с использованием фильтров
        """
        MovieHelper.get_afisha(creation_user_by_role.api, data="random", expected_status=200)

    def test_create_movie(self, creation_user_by_role):
        """
        Создание фильма.
        Только супер-админ может создать фильм.
        """
        if creation_user_by_role.roles[0] in TestMovieAPIByRoles.SUPER_ADMIN_RIGHTS:
            MovieHelper.generate_data_and_create_movie(creation_user_by_role.api, expected_status=201)
        else:
            MovieHelper.generate_data_and_create_movie(creation_user_by_role.api, expected_status=403)

