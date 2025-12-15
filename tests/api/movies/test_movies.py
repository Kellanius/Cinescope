import constants as const
from conftest import api_manager
from utils.data_generator import DataGenerator
from utils.auth_data_builder import AuthDataBuilder
import secrets
from utils.assert_helpers import CustomAssertions
from faker import Faker
import random
from utils.movie_helpers import MovieHelper

faker = Faker()


class TestMovieAPI:
    # Класс для тестирования фильмов

############################################################
                    # ПОЗИТИВНЫЕ ПРОВЕРКИ
############################################################

    # Авторизация под админом (дальше все проверки под админом)
    def test_login_admin(self, api_manager):

        # Вызов метода авторизации через AuthAPI
        response = api_manager.auth_api.login_user(AuthDataBuilder.create_login_data(secrets.ADMIN_AUTH_DATA))

        # Сохранение токена админа в сессию
        api_manager.auth_api.authenticate(AuthDataBuilder.create_login_data(secrets.ADMIN_AUTH_DATA))

        # Перевод данных ответа в json формат и проверка наличия токена
        response_data = response.json()
        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"


    #####################################
                  # Афиши
    #####################################

    #### Получение афиш фильмов с параметрами по-умолчанию (без введения своих параметров) ####
    def test_get_movies_info_with_default_params(self, api_manager):

        # Запрос на получение афиши с деволтными данными
        afisha_data = MovieHelper.get_afisha(api_manager, data="default")

        # Сравнение инфы из полученного ответа с дефолтными параметрами для афиша фильтра
        CustomAssertions.assert_equals(const.default_params_for_afisha_filter, afisha_data, "pageSize", "page")

        # Проверка, что цены фильмов попадают в фильтрационный диапазон.
        CustomAssertions.assert_afisha_prices_in_range(const.default_params_for_afisha_filter, afisha_data)


    #### Получение афиш фильмов с рандомными параметрами ####
    def test_get_movies_info_with_random_params(self, api_manager):

        # Запрос на получение афиши с рандомными данными
        afisha_data, random_data_for_afisha_filter = MovieHelper.get_afisha(api_manager, data="random")

        # Проверка того, что данные в ответе совпадают со сгенерированными
        CustomAssertions.assert_equals(random_data_for_afisha_filter, afisha_data, "pageSize", "page")

        # Проверка, что цены фильмов в афише попадают в фильтрационный диапазон рандомно сгенерированных параметров
        CustomAssertions.assert_afisha_prices_in_range(random_data_for_afisha_filter, afisha_data)

    #####################################
    # Создание/изменение/удаление фильма
    #####################################
    def test_create_edit_delete_movie(self, api_manager):
        #### Создание фильма ####

        # Генерация рандомных данных, создание фильма, получение данных о фильме с сайта (create_movie_data) и сгенерированных данных (random_data_for_new_movie)
        create_movie_data, random_data_for_new_movie = MovieHelper.generate_data_and_create_movie(api_manager)

        # Проверка, что фильм создан и информация о нём приходит с сайта
        get_movie_data = MovieHelper.get_movie_info(api_manager, create_movie_data["id"])

        # Проверки того, что данные из ответа совпадают с рандомно сгенерированными параметрами для фильма
        CustomAssertions.assert_equals(random_data_for_new_movie, get_movie_data, "name", "price", "description", "location") # проверка названия, цены, описания, локации фильма


        #### Изменение фильма (PATCH) ####

        # Генерация новых и замена старых данных. Получаем ответ в json формате об изменении данных
        patch_movie_data = MovieHelper.generate_data_and_patch_movie(api_manager, get_movie_data)

        # Проверка того что данные изменились после отправки запроса на PATCH
        CustomAssertions.assert_non_equals(patch_movie_data, get_movie_data, "name", "price", "description", "location") # проверка, что название, цена, описание, локация изменились


        #### Удаление фильма с проверкой ####
        MovieHelper.delete_movie_with_assert(api_manager, get_movie_data["id"], expected_status=404)


    ############################################################
                        # НЕГАТИВНЫЕ ПРОВЕРКИ
    ############################################################

    #####################################
                  # Афиши
    #####################################

    # Получение афиш фильмов с некорректными параметрами (минимальный прайс больше максимального)
    def test_get_incorrect_movies_info_with_random_params(self, api_manager):

        # Запрос на получение афиши с рандомными некорректными данными. Ответ должен выдать 400 ошибку
        MovieHelper.get_afisha(api_manager, data="random", correct_data=False, expected_status=400)

    #####################################
            # Создание фильма
    #####################################
    def test_create_incorrect_movie(self, api_manager, created_movie):

        #### Создание фильма с некорректными данными ####

        # Создание фильма с текстом вместо прайса
        MovieHelper.generate_data_and_create_movie(api_manager, price="abc", expected_status=400)

        # Создание фильма без названия
        MovieHelper.generate_data_and_create_movie(api_manager, name="", expected_status=400)

        # Создание фильма с несуществующей location
        MovieHelper.generate_data_and_create_movie(api_manager, location="ABC", expected_status=400)


        ## Создание фильма без данных ##
        # Создание пустых данных для фильма
        empty_data = {}

        # Запрос на создание фильма без данных. Должна быть 400 ошибка
        api_manager.movies_api.create_new_movies(empty_data, expected_status=400)


        ## Создание фильма с уже существующим именем ##
        # Генерация корректных данных для фильма, но с тем же названием, что у уже созданного фильма (created_movie). Ожидается ошибка 409
        MovieHelper.generate_data_and_create_movie(api_manager, name=f"{created_movie['name']}", expected_status=409)


    #####################################
        # Получение данных фильма
    #####################################
    def test_get_movie_info_with_incorrect_id(self, api_manager):
        ## Получение данных фильма по несуществующему id ##
        api_manager.movies_api.get_movie_info(DataGenerator.generate_random_id(), expected_status=404)


    #####################################
            # Удаление фильма
    #####################################
    def test_delete_movie_with_incorrect_id(self, api_manager):
        ## Удаление фильма с несуществующим id ##
        api_manager.movies_api.delete_movie(DataGenerator.generate_random_id(), expected_status=404)


    def test_incorrect_patch_movie(self, api_manager, created_movie):
    #####################################
    # Редактирование информации о фильме
    #####################################
        ## Редактирование фильма некорректными данными ##

        # Редактирование данных на некорректные (минусовый прайс)
        new_incorrect_price = random.randint(-1000, -1)

        # Генерация новых данных, замена их старыми, изменение прайса на некорректный, отправка запроса. Ожидается 400 ошибка
        MovieHelper.generate_data_and_patch_movie(api_manager, created_movie, price=new_incorrect_price, expected_status=400)

        # Удаление фильма
        MovieHelper.delete_movie_with_assert(api_manager, created_movie["id"])


        ## Проверка PATCH в несуществующий айди из удалённого created_movie. Ожидается 404 ошибка
        MovieHelper.generate_data_and_patch_movie(api_manager, created_movie, expected_status=404)