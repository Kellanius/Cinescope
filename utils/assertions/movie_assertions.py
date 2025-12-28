from utils.price_utils import MoviePriceAnalyzer
from utils.assertions.assert_helpers import CustomAssertions

# Модуль для упрощения и сокращения ассертов
class MovieCustomAssertions:
    # Проверка того, что цены попадают в фильтрационный диапазон
    @staticmethod
    def assert_afisha_prices_in_range(filter_params, afisha_response):
        """
        :param filter_params: параметры фильтрации
        :param afisha_response: это ответ от API с афишей
        проверяет, попали ли все фильмы из afisha_response в ожидаемый диапазон цен из filter_params
        """
        assert filter_params["maxPrice"] >= MoviePriceAnalyzer.get_max_price(afisha_response), "В афишу попали фильмы с ценой больше, чем указано в фильтре"
        assert filter_params["minPrice"] <= MoviePriceAnalyzer.get_min_price(afisha_response), "В афишу попали фильмы с ценой меньше, чем указано в фильтре"


    @staticmethod
    def assert_afisha_page(params, afisha_data):
        # Проверка, что полученная афиша подходит под заданные параметры
        CustomAssertions.assert_equals(params, afisha_data, "pageSize", "page")

    @staticmethod
    def assert_afisha_locations(params, afisha_data):
        # Все фильмы в ответе соответствуют заданной локации

        # Получаем список всех локаций из фильмов
        locations_in_movies = [movie["location"] for movie in afisha_data["movies"]]

        # Если params["locations"] - список, проверяем что все локации фильмов в нем
        expected_locations = params.get("locations")

        if isinstance(expected_locations, list):
            for location in locations_in_movies:
                assert location in expected_locations, f"Локация '{location}' не найдена в ожидаемых {expected_locations}"

        else:
            # Если передана одна локация
            assert all(loc == expected_locations for loc in locations_in_movies), \
            f"Не все фильмы имеют локацию '{expected_locations}'"


    @staticmethod
    def assert_afisha_genreId(params, afisha_data):
        # Получаем список всех жанров из фильмов
        genre_in_movies = [movie["genreId"] for movie in afisha_data["movies"]]

        expected_genre = params.get("genreId")

        if isinstance(expected_genre, list):
            for genre in genre_in_movies:
                assert genre in expected_genre, f"Жанр '{genre}' не найдена в ожидаемых {expected_genre}"

        else:
            assert all(loc == expected_genre for loc in genre_in_movies), f"Не все фильмы имеют жанр '{expected_genre}'"