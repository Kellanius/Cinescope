
# Модуль для вычисления максимальной или минимальной цены в афише фильмов

class MoviePriceAnalyzer:
    """Утилиты для работы с ценами фильмов"""

    @staticmethod
    def get_all_prices(response_data):
        """
        :param response_data: данные с афиши фильмов
        :return: список всех цен
        """

        # Создание списка с ценами всех фильмов
        all_prices = []

        # Добавление в список цен каждого фильма
        for i in response_data["movies"]:
            all_prices.append(i["price"])

        return all_prices


    @staticmethod
    def get_max_price(response_data):
        """
        :param response_data: данные с афиши фильмов
        :return: максимальное значение цены
        """
        return max(MoviePriceAnalyzer.get_all_prices(response_data))


    @staticmethod
    def get_min_price(response_data):
        """
        :param response_data: данные с афиши фильмов
        :return: минимальное значение цены
        """
        return min(MoviePriceAnalyzer.get_all_prices(response_data))
