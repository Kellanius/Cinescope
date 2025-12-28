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
                message = f"Ожидалось что {expectation} не совпадает с {actual}"
            assert expectation != actual, message


        else:
            for i in args:
                if message is None:
                    message = f"Ожидалось что {expectation} не совпадает с {actual}"
                assert expectation[i] != actual[i], message


    # Проверка того, что одна или несколько переменных есть в данных
    @staticmethod
    def assert_var_in_data(var, data, message = None):
        """
        :param var: переменная
        :param data: данные в которых проверяем есть ли переменная
        :param message: сообщение, если проверка провалена
        """
        # Если мы проверяем 1 переменную, то в данных будет искаться только она
        if isinstance(var, str):
            if message is None:
                message = f"Ожидалось что переменная {var} имеется в ответе {data}"

            assert var in data, message

        # Если проверяем несколько переменных (список), то в каждая будет проверяться на наличие в данных
        if isinstance(var, list):
            if message is None:
                for i in var:
                    message = f"Ожидалось что переменная {i} имеется в ответе {data}"
                    assert i in data, message
            else:
                for i in var:
                    assert i in data, message
