import allure
import pytest


@allure.title("Проверка сложения двух чисел")
@allure.description("Тест проверяет, что сумма двух чисел вычисляется корректно")
def test_addition():
    with allure.step("Проверка суммы 2 + 2"):
        assert 2 + 2 == 4

    with allure.step("Проверка суммы 3 + 2"):
        assert 2 + 2 == 5