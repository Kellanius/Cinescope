import constants as const
from conftest import api_manager
from utils.data_generator import DataGenerator
from custom_requester.custom_requester import CustomRequester
from tests.api.api_manager import ApiManager
from utils.auth_data_builder import AuthDataBuilder
import secrets
from utils.assert_helpers import CustomAssertions
from utils.price_utils import MoviePriceAnalyzer
from faker import Faker
import random

faker = Faker()

class TestMovieAPI:
    # Класс для тестирования фильмов

############################################################
                    # ПОЗИТИВНЫЕ ПРОВЕРКИ
############################################################


    # Авторизуемся под админом (дальше все проверки под админом)
    def test_login_admin(self, api_manager):
        """
        Авторизация админа.
        """

        # Вызов метода авторизации через AuthAPI
        response = api_manager.auth_api.login_user(AuthDataBuilder.create_login_data(secrets.ADMIN_AUTH_DATA))

        # Сохранение токена админа в сессию
        api_manager.auth_api.authenticate(AuthDataBuilder.create_login_data(secrets.ADMIN_AUTH_DATA))

        response_data = response.json()
        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"

    #####################################
                  # Афиши
    #####################################


    # Получение афиш фильмов с параметрами по-умолчанию (без введения параметров)
    def test_get_movies_info_with_default_params(self, api_manager):
        # Делаем запрос на получение афиши
        response = api_manager.movies_api.get_afisha_info()

        # Переводим данные в json формат
        response_data = response.json()

        # Сравниваю инфу из полученного ответа с дефолтными параметрами для афиша фильтра
        CustomAssertions.assert_equals(const.default_params_for_afisha_filter["pageSize"], response_data["pageSize"])
        CustomAssertions.assert_equals(const.default_params_for_afisha_filter["page"], response_data["page"])

        # Проверяю что цены фильмов попадают в фильтрационный диапазон
        assert const.default_params_for_afisha_filter["maxPrice"] >= MoviePriceAnalyzer.get_max_price(response_data), "В афишу попали фильмы с ценой больше, чем указано в фильтре"
        assert const.default_params_for_afisha_filter["minPrice"] <= MoviePriceAnalyzer.get_min_price(response_data), "В афишу попали фильмы с ценой меньше, чем указано в фильтре"

    # Получение афиш фильмов с рандомными параметрами
    def test_get_movies_info_with_random_params(self, api_manager):
        # Генерирую рандомные данные для фильтра
        random_data_for_afisha_filter = DataGenerator.generate_random_data_for_afisha_filter()

        # Делаем запрос на получение афиши. Вставляем рандомные данные из генератора
        response = api_manager.movies_api.get_afisha_info(**random_data_for_afisha_filter)

        # Переводим данные в json формат
        response_data = response.json()

        # Сравниваю инфу из полученного ответа с рандомно сгенерированными параметрами для афиша фильтра
        CustomAssertions.assert_equals(random_data_for_afisha_filter["pageSize"], response_data["pageSize"])
        CustomAssertions.assert_equals(random_data_for_afisha_filter["page"], response_data["page"])

        # Проверяю что цены фильмов попадают в фильтрационный диапазон рандомно сгенерированных параметров
        assert random_data_for_afisha_filter["maxPrice"] >= MoviePriceAnalyzer.get_max_price(response_data), "В афишу попали фильмы с ценой больше, чем указано в фильтре"
        assert random_data_for_afisha_filter["minPrice"] <= MoviePriceAnalyzer.get_min_price(response_data), "В афишу попали фильмы с ценой меньше, чем указано в фильтре"

    #####################################
    # Создание/изменение/удаление фильма
    #####################################
    def test_create_edit_delete_movie(self, api_manager):
        #### Создание фильма ####

        # Генерируем рандомные данные для фильма
        random_data_for_new_movies = DataGenerator.generate_random_data_for_new_movies()

        # Делаем запрос на создание фильма. Вставляем рандомные данные из генератора
        response_create_movie = api_manager.movies_api.create_new_movies(random_data_for_new_movies)

        # Переводим данные ответа о создании фильма в json формат
        response_create_movie_data = response_create_movie.json()

        # Проверяем, что фильм создан по данным параметрам
        response_get_movie_info = api_manager.movies_api.get_movie_info(response_create_movie_data["id"])

        # Переводим данные об информации о фильме в json формат
        response_get_movie_info_data = response_get_movie_info.json()

        # Сравниваем инфу из полученного ответа с рандомно сгенерированными параметрами для фильма
        CustomAssertions.assert_equals(random_data_for_new_movies["name"], response_get_movie_info_data["name"]) # проверяем название фильма
        CustomAssertions.assert_equals(random_data_for_new_movies["price"], response_get_movie_info_data["price"])  # проверяем цену фильма
        CustomAssertions.assert_equals(random_data_for_new_movies["description"], response_get_movie_info_data["description"])  # проверяем описание фильма
        CustomAssertions.assert_equals(random_data_for_new_movies["location"], response_get_movie_info_data["location"])  # проверяем локацию фильма


        #### Изменение фильма ####

        # Генерируем новые данные для замены старых
        new_movie_data_for_patch = DataGenerator.generate_random_data_for_patch_movies_info(response_get_movie_info_data)


        # Меняем данные фильма по его id
        response_patch_movie_info = api_manager.movies_api.patch_movie_info(response_create_movie_data["id"], new_movie_data_for_patch)

        # Переводим ответ об изменении данных о фильме в json формат
        response_patch_movie_info_data = response_patch_movie_info.json()

        # Сравниваем инфу из полученного ответа со старой информацией о фильме
        CustomAssertions.assert_non_equals(response_patch_movie_info_data["name"], response_get_movie_info_data["name"]) # проверяем что название изменилось
        CustomAssertions.assert_non_equals(response_patch_movie_info_data["price"], response_get_movie_info_data["price"])  # проверяем что цена изменилось
        CustomAssertions.assert_non_equals(response_patch_movie_info_data["description"], response_get_movie_info_data["description"])  # проверяем что описание изменилось
        CustomAssertions.assert_non_equals(response_patch_movie_info_data["location"], response_get_movie_info_data["location"])  # проверяем что локация изменилось


        #### Удаление фильма ####
        # Удаляем фильм
        response_delete_movie = api_manager.movies_api.delete_movie(response_create_movie_data["id"])

        # Переводим ответ об удалении фильма в json формат
        response_delete_movie_data = response_delete_movie.json()

        # Проверяем, что фильма больше не существует (делаем GET запрос на получение инфы о фильме)
        response_get_deleted_movie_info = api_manager.movies_api.get_movie_info(response_delete_movie_data["id"], expected_status=404)


    ############################################################
                        # НЕГАТИВНЫЕ ПРОВЕРКИ
    ############################################################

    #####################################
                  # Афиши
    #####################################

    # Получение афиш фильмов с некорректными параметрами (минимальный прайс больше максимального)
    def test_get_incorrect_movies_info_with_random_params(self, api_manager):
        # Генерирую рандомные некорректные данные для фильтра
        random_incorrect_data_for_afisha_filter = DataGenerator.generate_random_data_for_afisha_filter(correct_data=False)

        # Делаем запрос на получение афиши. Вставляем рандомные некорректные данные из генератора. В итоге ответ должен выдать 400 ошибку
        response = api_manager.movies_api.get_afisha_info(**random_incorrect_data_for_afisha_filter, expected_status=400)

    #####################################
            # Создание фильма
    #####################################
    def test_create_incorrect_movie(self, api_manager):

        #### Создание фильма с некорректными данными ####

        ## Создание фильма с текстом вместо прайса ##
        # Генерируем рандомные данные для фильма с текстом в прайсе
        random_data_for_new_incorrect_movies = DataGenerator.generate_random_data_for_new_movies(price="abc")

        # Делаем запрос на создание фильма. Должна быть 400 ошибка
        response_create_movie = api_manager.movies_api.create_new_movies(random_data_for_new_incorrect_movies, expected_status=400)


        ## Создание фильма без названия ##
        # Генерируем рандомные данные для фильма без названия
        random_data_for_new_incorrect_movies = DataGenerator.generate_random_data_for_new_movies(name="")

        # Делаем запрос на создание фильма. Должна быть 400 ошибка
        response_create_movie = api_manager.movies_api.create_new_movies(random_data_for_new_incorrect_movies, expected_status=400)


        ## Создание фильма с несуществующей location ##
        # Генерируем рандомные данные для фильма с несуществующей location
        random_data_for_new_incorrect_movies = DataGenerator.generate_random_data_for_new_movies(location="ABC")

        # Делаем запрос на создание фильма. Должна быть 400 ошибка
        response_create_movie = api_manager.movies_api.create_new_movies(random_data_for_new_incorrect_movies, expected_status=400)


        ## Создание фильма без данных
        # Генерируем пустые данные для фильма с несуществующей location
        random_data_for_new_incorrect_movies = {}

        # Делаем запрос на создание фильма. Должна быть 400 ошибка
        response_create_movie = api_manager.movies_api.create_new_movies(random_data_for_new_incorrect_movies, expected_status=400)


        ## Создание фильма с уже существующим именем ##
        # Генерируем рандомные корректные данные для фильма
        random_data_for_first_new_movies = DataGenerator.generate_random_data_for_new_movies()

        # Делаем запрос на создание фильма. Вставляем рандомные данные из генератора.
        response_create_first_movie = api_manager.movies_api.create_new_movies(random_data_for_first_new_movies)

        # Переводим данные в json формат
        response_create_first_movie_data = response_create_first_movie.json()

        # Снова генерируем корректные данные для фильма, но название берем из уже созданного фильма
        random_data_for_second_new_movies = DataGenerator.generate_random_data_for_new_movies(name=f"{random_data_for_first_new_movies['name']}")

        # Делаем запрос на создание второго фильма. Тут должна быть ошибка 409
        response_create_second_movie = api_manager.movies_api.create_new_movies(random_data_for_second_new_movies, expected_status=409)


        # Удаляем первый фильм, чтобы не засорял БД
        response_delete_movie = api_manager.movies_api.delete_movie(response_create_first_movie_data["id"])

        # Переводим ответ об удалении фильма в json формат
        response_delete_movie_data = response_delete_movie.json()

        # Проверяем, что фильма больше не существует (делаем GET запрос на получение инфы о фильме)
        response_get_deleted_movie_info = api_manager.movies_api.get_movie_info(response_delete_movie_data["id"], expected_status=404)


    #####################################
        # Получение данных фильма
    #####################################
    def test_get_movie_info_with_incorrect_id(self, api_manager):
        ## Получение данных фильма по несуществующему id ##
        response_get_movie_info_with_incorrect_id = api_manager.movies_api.get_movie_info(DataGenerator.generate_random_id(), expected_status=404)

    #####################################
            # Удаление фильма
    #####################################
    def test_delete_movie_with_incorrect_id(self, api_manager):
        ## Удаление фильма с несуществующим id ##
        response_delete_movie_with_incorrect_id = api_manager.movies_api.delete_movie(DataGenerator.generate_random_id(), expected_status=404)

    #####################################
    # Редактирование информации о фильме
    #####################################
        ## Редактирование фильма некорректными данными ##

        #СОЗДАНИЕ
        # Генерируем рандомные данные для фильма
        random_data_for_new_movies = DataGenerator.generate_random_data_for_new_movies()

        # Делаем запрос на создание фильма. Вставляем рандомные данные из генератора
        response_create_movie = api_manager.movies_api.create_new_movies(random_data_for_new_movies)

        # Переводим данные ответа о создании фильма в json формат
        response_create_movie_data = response_create_movie.json()

        # Проверяем, что фильм создан по данным параметрам
        response_get_movie_info = api_manager.movies_api.get_movie_info(response_create_movie_data["id"])

        # Переводим данные об информации о фильме в json формат
        response_get_movie_info_data = response_get_movie_info.json()


        # ИЗМЕНЕНИЕ

        # Генерируем новые данные для замены старых
        new_movie_data_for_patch = DataGenerator.generate_random_data_for_patch_movies_info(response_get_movie_info_data)

        # Редактируем эти новые данные на некорректные (минусовой прайс)
        new_movie_data_for_patch["price"] = random.randint(-1000, -1)

        # Меняем данные фильма по его id на новые. Ловим 400 ошибку
        response_patch_movie_info = api_manager.movies_api.patch_movie_info(response_create_movie_data["id"], new_movie_data_for_patch, expected_status=400)

        #### Удаление фильма ####
        # Удаляем фильм
        response_delete_movie = api_manager.movies_api.delete_movie(response_create_movie_data["id"])

        # Переводим ответ об удалении фильма в json формат
        response_delete_movie_data = response_delete_movie.json()

        # Проверяем, что фильма больше не существует (делаем GET запрос на получение инфы о фильме)
        response_get_deleted_movie_info = api_manager.movies_api.get_movie_info(response_delete_movie_data["id"], expected_status=404)

        #### Сразу проверяем PATCH в несуществующий айди. Ловим 400 ошибку (хотя по сваггеру должна быть 404) ####
        response_patch_movie_info_to_non_existent_id = api_manager.movies_api.patch_movie_info(response_create_movie_data["id"], new_movie_data_for_patch, expected_status=400)