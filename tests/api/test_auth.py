from http.client import responses
from unittest import expectedFailure

import constants as const
import utils.data_generator as data_gener
from custom_requester.custom_requester import CustomRequester
from tests.api.api_manager import ApiManager
from utils.auth_data_builder import AuthDataBuilder
import secrets


class TestAuthAPI:
    def test_register_user(self, api_manager, test_user):
        """
        Тест на регистрацию пользователя.
        """
        response = api_manager.auth_api.register_user(test_user)
        response_data = response.json()

        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"



    def test_register_and_login_user(self, api_manager, registered_user):
        """
        Тест на регистрацию и авторизацию пользователя.
        """

        # Вызов метода авторизации через AuthAPI
        response = api_manager.auth_api.login_user(AuthDataBuilder.create_login_data(registered_user))

        response_data = response.json()
        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
        assert response_data["user"]["email"] == registered_user["email"], "Email не совпадает"



    def test_incorrect_password_auth_user(self, api_manager, test_user, registered_user):

        # Замена пароля на неподходящий (больше 20 символов)
        incorrect_password = data_gener.DataGenerator.generate_negative_random_password_over_max()

        response = api_manager.auth_api.login_user(AuthDataBuilder.create_login_data(registered_user, password=incorrect_password), expected_status=401)

        # Проверка
        assert response.status_code == 401, "Пользователь авторизован с неверным паролем"


    def test_incorrect_email_auth_user(self, test_user, api_manager, registered_user):
        # Авторизация с несуществующим email

        # Замена email на несуществующий
        incorrect_email = data_gener.DataGenerator.generate_non_existent_random_email()

        # Отправка запроса на авторизацию
        response = api_manager.auth_api.login_user(AuthDataBuilder.create_login_data(registered_user, email=incorrect_email), expected_status=401)

        # Проверка
        assert response.status_code == 401, "Пользователь авторизован с неверным email"


    def test_auth_user_without_data(self, test_user, api_manager, registered_user):
        # Авторизация с пустым телом запроса
        response = api_manager.auth_api.login_user(AuthDataBuilder.create_login_data(), expected_status=401)

        # Проверка
        assert response.status_code == 401, "Авторизация прошла без данных"