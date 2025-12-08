
# Модуль для вычисления максимальной или минимальной цены в афише фильмов

class MoviePriceAnalyzer:
    """Утилиты для работы с ценами фильмов"""

    @staticmethod
    def get_max_price(response_data):
        """
        :param response_data: принимает данные с афиши фильмов
        :return: возвращает максимальное значение цены
        """
        # Создаю список с ценами всех фильмов
        all_prices = []

        # Добавляю в список все цены каждого фильма
        for i in response_data["movies"]:
            all_prices.append(i["price"])

        # Вычисляю максимальную цену
        maximum = max(all_prices)

        return maximum

    @staticmethod
    def get_min_price(response_data):
        """
        :param response_data: принимает данные с афиши фильмов
        :return: возвращает минимальное значение цены
        """
        # Создаю список с ценами всех фильмов
        all_prices = []

        # Добавляю в список все цены каждого фильма
        for i in response_data["movies"]:
            all_prices.append(i["price"])

        # Вычисляю максимальную цену
        minimum = min(all_prices)

        return minimum