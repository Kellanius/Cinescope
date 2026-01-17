import test_auth
import utils.data_generator as data_gener
from utils.auth_data_builder import AuthDataBuilder
from utils.assertions.assert_helpers import CustomAssertions
import datetime
from constants import Roles
from dataclasses import dataclass
from typing import List
import allure
from pytest_check import check

@allure.epic("Тестирование авторизации")
@allure.feature("Позитивные проверки")
class TestAuthAPI:

    @allure.description("""
        Тест проверяет регистрацию пользователя через api
        """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "Ilukha Khittsov")
    @allure.title("Тест на регистрацию пользователя")
    def test_register_user(self, api_manager, creation_test_user):

        with allure.step("Регистрация пользователя с рандомными данными"):
            response = api_manager.auth_api.register_user(creation_test_user)
            response_data = response.json()

        with allure.step("Проверка на идентичность email в сгенерированных и зарегистрированных данных"):
            check.equal(response_data["email"], creation_test_user["email"], "проверка идентичности email")

        with allure.step("Проверка, что переменные есть в ответе"):
            check.is_in("USER", response_data["roles"])
            CustomAssertions.assert_var_in_data(["id", "roles"], response_data)

##################
    @allure.title("Тест на регистрацию и авторизацию пользователя")
    def test_register_and_login_user(self, api_manager, registered_user):

        with allure.step("Вызов метода авторизации через AuthAPI"):
            response = api_manager.auth_api.login_user(AuthDataBuilder.create_login_data(registered_user))
            response_data = response.json()

        with allure.step("Проверка наличия токена в ответе + проверка корректности email"):
            CustomAssertions.assert_var_in_data("accessToken", response_data, message="Токен доступа отсутствует в ответе")
            CustomAssertions.assert_equals(response_data["user"]["email"], registered_user["email"])


##################
    @allure.feature("Негативные проверки")
##################
    @allure.title("Тест на авторизацию с некорректным паролем")
    def test_incorrect_password_auth_user(self, api_manager, registered_user):

        with allure.step("Замена пароля на неподходящий (больше 20 символов)"):
            incorrect_password = data_gener.DataGenerator.generate_negative_random_password_over_max()

        with allure.step("Попытка авторизации с неверным паролем"):
            api_manager.auth_api.login_user(AuthDataBuilder.create_login_data(registered_user, password=incorrect_password), expected_status=401)

##################
    @allure.title("Тест авторизацию с несуществующим email")
    def test_incorrect_email_auth_user(self, api_manager, registered_user):

        with allure.step("Замена email на несуществующий"):
            incorrect_email = data_gener.DataGenerator.generate_non_existent_random_email()

        # Отправка запроса на авторизацию
        api_manager.auth_api.login_user(AuthDataBuilder.create_login_data(registered_user, email=incorrect_email), expected_status=401)

##################
    @allure.title("Тест на авторизацию с пустым телом запроса")
    def test_auth_user_without_data(self, api_manager):

        api_manager.auth_api.login_user(AuthDataBuilder.create_login_data(), expected_status=401)

##################
    @dataclass
    class RegisterUserResponse:
        """Модель ответа при регистрации пользователя"""
        id: str
        email: str
        fullName: str  # Обрати внимание: в JSON fullName, в Python обычно full_name
        verified: bool
        banned: bool
        roles: List[Roles]
        createdAt: str


    @allure.title("Тест регистрации пользователя с помощью Mock")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("qa_name", "Ilya Khittsov")
    def test_register_user_mock(self, api_manager, creation_test_user, mocker):
        with allure.step("Мок метода register_user в auth_api"):
            mock_response = test_auth.TestAuthAPI.RegisterUserResponse(
                id="id",
                email="email@email.com",
                fullName="fullName",
                verified=True,
                banned=False,
                roles=[Roles.SUPER_ADMIN],
                createdAt=str(datetime.datetime.now())
            )

            mocker.patch.object(
                api_manager.auth_api,  # Объект, который нужно замокать
                'register_user',  # Метод, который нужно замокать
                return_value=mock_response  # Фиктивный ответ
        )

        with allure.step("Вызов метода, который должен быть замокан"):
            register_user_response = api_manager.auth_api.register_user(creation_test_user)


        with allure.step("Проверка, что ответ соответствует ожидаемому"):
            with allure.step("Проверка поля персональных данных"):
                with check:
                    check.equal(register_user_response.fullName, "fullName", "НЕСОВПАДЕНИЕ fullName")
                    check.equal(register_user_response.email, mock_response.email)

            with allure.step("Проверка поля banned"):
                with check("Проверка поля banned"):  # можно использовать вместо allure.step
                    check.equal(register_user_response.banned, mock_response.banned)