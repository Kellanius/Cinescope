import constants as const
from utils.data_generator import DataGenerator
from utils.assertions.assert_helpers import CustomAssertions
from faker import Faker
import random
from utils.movie_helpers import MovieHelper
import pytest
from utils.assertions.movie_assertions import MovieCustomAssertions
from db_requester.db_helpers import DBHelper
from db_models.accounts_transaction_template import AccountTransactionTemplate
import allure
from pytest_check import check


faker = Faker()

@allure.epic("Тестирование транзакций")
@allure.feature("Тестирование транзакций между счетами")
class TestOtherAPI:

    @allure.story("Корректность перевода денег между двумя счетами")
    @allure.description("""
    Этот тест проверяет корректность перевода денег между двумя счетами.
    Шаги:
    1. Создание двух счетов: Stan и Bob.
    2. Перевод 200 единиц от Stan к Bob.
    3. Проверка изменения балансов.
    4. Очистка тестовых данных.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("qa_name", "Iluha Khittsov")
    @allure.title("Тест перевода денег между счетами 200 рублей")
    def test_accounts_transaction_template(self, db_session):
        # ========== Подготовка к тесту ==========
        with allure.step("Создание тестовых данных в базе данных: счета Stan и Bob"):
            stan = AccountTransactionTemplate(user=f"Stan_{random.randint(10,10)}", balance=1000)
            bob = AccountTransactionTemplate(user=f"Bob_{random.randint(10,10)}", balance=500)
            db_session.add_all([stan, bob])
            db_session.commit()

        @allure.step("Функция перевода денег: transfer_money")
        @allure.description("""
        Функция выполняющая транзакцию.
        Имитация вызова функции на стороне тестируемого сервиса.
        Вызывая метод transfer_money, мы будто бы делаем запрос в api_manager.movies_api.transfer_money
            """)
        def transfer_money(session, from_account, to_account, amount):
            with allure.step("Получение счетов"):
                from_account = session.query(AccountTransactionTemplate).filter_by(user=from_account).one()
                to_account = session.query(AccountTransactionTemplate).filter_by(user=to_account).one()

            with allure.step("Проверка достаточности средств на счёте"):
                if from_account.balance < amount:
                    raise ValueError("Недостаточно средств на счете")

            with allure.step("Выполнение перевода"):
                from_account.balance -= amount
                to_account.balance += amount

            with allure.step("Сохранение изменений"):
                session.commit()

        # ========== Тест ==========

        with allure.step("Проверка начальных балансов"):
            assert stan.balance == 1000
            assert bob.balance == 500

        try:
            with allure.step("Выполнение перевода на 200 единиц от stan к bob"):
                transfer_money(db_session, from_account=stan.user, to_account=bob.user, amount=200)

            with allure.step("Проверка изменения балансов"):
                assert stan.balance == 800
                assert bob.balance == 700

        except Exception as e:
            with allure.step("Откат транзакции в случае ошибки"):
                db_session.rollback()

            pytest.fail(f"Ошибка при переводе денег: {e}")

        finally:
            with allure.step("Удаление данных для тестирования из базы"):
                db_session.delete(stan)
                db_session.delete(bob)
                db_session.commit()


    @allure.title("Тест с перезапусками")
    @pytest.mark.flaky(rerans=3)
    def test_with_retries(self, delay_between_retries):
        with allure.step("Шаг 1: Проверка случайного значения"):
            result = random.choice([True, False])
            with check:
                assert result, "Тест упал, потому что результат False"