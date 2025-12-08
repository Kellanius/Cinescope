

# Модуль для упрощения и сокращения ассертов
class CustomAssertions:
    @staticmethod
    def assert_equals(expectation, actual, message = None):
        if message is None:
            message = f"Ожидалось {expectation}, фактически {actual}"

        assert expectation == actual, message

    @staticmethod
    def assert_non_equals(expectation, actual, message = None):
        if message is None:
            message = f"Ожидалось что {expectation} не совпадает с фактическим {actual}"

        assert expectation != actual, message