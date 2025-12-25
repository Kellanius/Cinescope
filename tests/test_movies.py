import constants as const
from utils.data_generator import DataGenerator
from utils.auth_data_builder import AuthDataBuilder
import secrets
from utils.assert_helpers import CustomAssertions
from faker import Faker
import random
from utils.movie_helpers import MovieHelper

faker = Faker()


class TestMovieAPI:
############################################################
                    # ПОЗИТИВНЫЕ ПРОВЕРКИ
############################################################

    def test_get_movies_info_with_default_params(self, super_admin):
        """
        Получение афиши с параметрами по-умолчанию
        """

        # Запрос на получение афиши с деволтными данными
        afisha_data = MovieHelper.get_afisha(super_admin.api, data="default")

        # Сравнение инфы из полученного ответа с дефолтными параметрами для афиша фильтра
        CustomAssertions.assert_equals(const.default_params_for_afisha_filter, afisha_data, "pageSize", "page")

        # Проверка, что цены фильмов попадают в фильтрационный диапазон.
        CustomAssertions.assert_afisha_prices_in_range(const.default_params_for_afisha_filter, afisha_data)


    def test_get_movies_info_with_random_params(self, super_admin):
        """
        Получение афиш фильмов с рандомными параметрами
        """

        # Запрос на получение афиши с рандомными данными
        afisha_data, random_data_for_afisha_filter = MovieHelper.get_afisha(super_admin.api, data="random")

        # Проверка того, что данные в ответе совпадают со сгенерированными
        CustomAssertions.assert_equals(random_data_for_afisha_filter, afisha_data, "pageSize", "page")

        # Проверка, что цены фильмов в афише попадают в фильтрационный диапазон рандомно сгенерированных параметров
        CustomAssertions.assert_afisha_prices_in_range(random_data_for_afisha_filter, afisha_data)

    #####################################
    # Создание/изменение/удаление фильма (переработать в несколько проверок)
    #####################################
    def test_create_edit_delete_movie(self, super_admin):
        #### Создание фильма ####

        # Генерация рандомных данных, создание фильма, получение данных о фильме с сайта (create_movie_data) и сгенерированных данных (random_data_for_new_movie)
        create_movie_data, random_data_for_new_movie = MovieHelper.generate_data_and_create_movie(super_admin.api)

        # Проверка, что фильм создан и информация о нём приходит с сайта
        get_movie_data = MovieHelper.get_movie_data(super_admin.api, create_movie_data["id"])

        # Проверки того, что данные из ответа совпадают с рандомно сгенерированными параметрами для фильма
        CustomAssertions.assert_equals(random_data_for_new_movie, get_movie_data, "name", "price", "description", "location") # проверка названия, цены, описания, локации фильма


        #### Изменение фильма (PATCH) ####

        # Генерация новых и замена старых данных. Получаем ответ в json формате об изменении данных
        patch_movie_data = MovieHelper.generate_data_and_patch_movie(super_admin.api, get_movie_data)

        # Проверка того что данные изменились после отправки запроса на PATCH
        CustomAssertions.assert_non_equals(patch_movie_data, get_movie_data, "name", "price", "description", "location") # проверка, что название, цена, описание, локация изменились


        #### Удаление фильма с проверкой ####
        MovieHelper.delete_movie_with_assert(super_admin.api, get_movie_data["id"], expected_status=404)


    ############################################################
                        # НЕГАТИВНЫЕ ПРОВЕРКИ
    ############################################################

    def test_get_incorrect_movies_info_with_random_params(self, super_admin):
        """
        Запрос на получение афиши с рандомными некорректными данными
        """

        MovieHelper.get_afisha(super_admin.api, data="random", correct_data=False, expected_status=400)


    def test_create_incorrect_movie(self, super_admin, created_movie):
        """
        Создание фильма с некорректными данными
        """

        # Текст вместо прайса
        MovieHelper.generate_data_and_create_movie(super_admin.api, price="abc", expected_status=400)

        # Без названия
        MovieHelper.generate_data_and_create_movie(super_admin.api, name="", expected_status=400)

        # Несуществующий location
        MovieHelper.generate_data_and_create_movie(super_admin.api, location="ABC", expected_status=400)

        # Без данных
        empty_data = {}
        super_admin.api.movies_api.create_new_movies(empty_data, expected_status=400)

        # С существующим именем
        # Генерация корректных данных для фильма, но с тем же названием, что у уже созданного фильма (created_movie)
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

        # Редактирование данных на некорректные (минусовый прайс)
        new_incorrect_price = random.randint(-1000, -1)

        # Генерация новых данных, замена их старыми, изменение прайса на некорректный, отправка запроса. Ожидается 400 ошибка
        MovieHelper.generate_data_and_patch_movie(super_admin.api, created_movie, price=new_incorrect_price, expected_status=400)

        # Удаление фильма
        MovieHelper.delete_movie_with_assert(super_admin.api, created_movie["id"])

        ## Проверка PATCH в несуществующий айди из удалённого created_movie. Ожидается 404 ошибка
        MovieHelper.generate_data_and_patch_movie(super_admin.api, created_movie, expected_status=404)