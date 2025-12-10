import constants as const
from utils.data_generator import DataGenerator
from custom_requester.custom_requester import CustomRequester
from tests.api.api_manager import ApiManager
from utils.auth_data_builder import AuthDataBuilder
import secrets
from utils.assert_helpers import CustomAssertions
from utils.price_utils import MoviePriceAnalyzer


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

    # Получение афиш фильмов с рандомными параметрами по-умолчанию
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
            # Создание фильма
    #####################################
    def test_create_new_movie(self, api_manager):
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