from utils.price_utils import MoviePriceAnalyzer

# Модуль для упрощения и сокращения ассертов
class CustomAssertions:

    # Проверка того, что сравниваемые данные равны
    @staticmethod
    def assert_equals(expectation, actual, *args, message = None):
        """
        :param expectation: ожидаемый результат
        :param actual: фактический результат
        :param message: сообщение при несовпадении результатов
        :param args: данные для сравнения разных ключей в одинаковых словарях
        :return:
        """
        # Мы можем вставить в функцию 2 словаря для сравнения (expectation, actual) и затем различные ключи этих словарей (*args).
        # Тогда все пары ключей будут сравниваться
        # Это позволит сократить количество строк кода для проверок с 2+ до 1,
        # когда надо сравнивать много параметров в двух словарях

        # если args нет, то сравниваем как обычно
        if args is None:
            if message is None:
                message = f"Ожидалось {expectation}, фактически {actual}"
            assert expectation == actual, message

        # если args есть, то сравниваем ключи двух словарей
        else:
            for i in args:
                if message is None:
                    message = f"Ожидалось {expectation}, фактически {actual}"
                assert expectation[i] == actual[i], message


    # Проверка того, что сравниваемые данные не равны
    @staticmethod
    def assert_non_equals(expectation, actual, *args, message = None):
        # Тут всё аналогично позитивной проверке (assert_equals), только проверяется, что данные не совпадают

        if args is None:
            if message is None:
                message = f"Ожидалось что {expectation} не совпадает с фактическим {actual}"
            assert expectation != actual, message


        else:
            for i in args:
                if message is None:
                    message = f"Ожидалось что {expectation} не совпадает с фактическим {actual}"
                assert expectation[i] != actual[i], message


    # Проверка того, что цены попадают в фильтрационный диапазон
    @staticmethod
    def assert_afisha_prices_in_range(filter_params, afisha_response):
        """
        :param filter_params: параметры фильтрации
        :param afisha_response: это ответ от API с афишей
        проверяем, попали ли все фильмы из afisha_response в ожидаемый диапазон цен из filter_params
        """
        assert filter_params["maxPrice"] >= MoviePriceAnalyzer.get_max_price(afisha_response), "В афишу попали фильмы с ценой больше, чем указано в фильтре"
        assert filter_params["minPrice"] <= MoviePriceAnalyzer.get_min_price(afisha_response), "В афишу попали фильмы с ценой меньше, чем указано в фильтре"
