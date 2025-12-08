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


    # Получение афиш фильмов с параметрами по-умолчанию (без введения параметров)
    def test_get_movies_info_with_default_params(self, api_manager):
        # Делаем запрос на получение афиши
        response = api_manager.movies_api.get_movies_info()

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
        response = api_manager.movies_api.get_movies_info(**random_data_for_afisha_filter)

        # Переводим данные в json формат
        response_data = response.json()

        # Сравниваю инфу из полученного ответа с рандомно сгенерированными параметрами для афиша фильтра
        CustomAssertions.assert_equals(random_data_for_afisha_filter["pageSize"], response_data["pageSize"])
        CustomAssertions.assert_equals(random_data_for_afisha_filter["page"], response_data["page"])

        # Проверяю что цены фильмов попадают в фильтрационный диапазон рандомно сгенерированных параметров
        assert random_data_for_afisha_filter["maxPrice"] >= MoviePriceAnalyzer.get_max_price(response_data), "В афишу попали фильмы с ценой больше, чем указано в фильтре"
        assert random_data_for_afisha_filter["minPrice"] <= MoviePriceAnalyzer.get_min_price(response_data), "В афишу попали фильмы с ценой меньше, чем указано в фильтре"

