import utils.data_generator as data_gener
from utils.auth_data_builder import AuthDataBuilder
from utils.assertions.assert_helpers import CustomAssertions


class TestAuthAPI:
    ############################################################
    # ПОЗИТИВНЫЕ ПРОВЕРКИ
    ############################################################
    def test_register_user(self, api_manager, creation_test_user):
        """
        Тест на регистрацию пользователя
        """

        # Регистрация пользователя с рандомными данными (test_user)
        response = api_manager.auth_api.register_user(creation_test_user)
        response_data = response.json()

        # Проверка на идентичность email в сгенерированных и зарегистрированных данных
        CustomAssertions.assert_equals(response_data["email"], creation_test_user["email"])
        # Проверка, что переменные есть в ответе
        CustomAssertions.assert_var_in_data(["id", "roles"], response_data)
        CustomAssertions.assert_var_in_data("USER", response_data["roles"])


    def test_register_and_login_user(self, api_manager, registered_user):
        """
        Тест на регистрацию и авторизацию пользователя
        """

        # Вызов метода авторизации через AuthAPI
        response = api_manager.auth_api.login_user(AuthDataBuilder.create_login_data(registered_user))
        response_data = response.json()

        # Проверка наличия токена в ответе + проверка корректности email
        CustomAssertions.assert_var_in_data("accessToken", response_data, message="Токен доступа отсутствует в ответе")
        CustomAssertions.assert_equals(response_data["user"]["email"], registered_user["email"])


    ############################################################
    # НЕГАТИВНЫЕ ПРОВЕРКИ
    ############################################################
    def test_incorrect_password_auth_user(self, api_manager, registered_user):
        """
        Тест на авторизацию с некорректным паролем
        """

        # Замена пароля на неподходящий (больше 20 символов)
        incorrect_password = data_gener.DataGenerator.generate_negative_random_password_over_max()

        # Попытка авторизации с неверным паролем
        api_manager.auth_api.login_user(AuthDataBuilder.create_login_data(registered_user, password=incorrect_password), expected_status=401)


    def test_incorrect_email_auth_user(self, api_manager, registered_user):
        """
        Тест авторизацию с несуществующим email
        """

        # Замена email на несуществующий
        incorrect_email = data_gener.DataGenerator.generate_non_existent_random_email()

        # Отправка запроса на авторизацию
        api_manager.auth_api.login_user(AuthDataBuilder.create_login_data(registered_user, email=incorrect_email), expected_status=401)


    def test_auth_user_without_data(self, api_manager):
        """
        Тест на авторизацию с пустым телом запроса
        """
        api_manager.auth_api.login_user(AuthDataBuilder.create_login_data(), expected_status=401)