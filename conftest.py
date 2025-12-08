import requests
from requests import Session

from tests.api.auth_api import AuthAPI
from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT
import pytest
from utils.data_generator import DataGenerator
from faker import Faker
from custom_requester.custom_requester import CustomRequester
from tests.api.api_manager import ApiManager
import secrets
from utils.auth_data_builder import AuthDataBuilder

faker = Faker()

@pytest.fixture(scope="session")
def test_user():
    """
    Генерация случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": ["USER"]
    }


@pytest.fixture(scope="session")
def registered_user(api_manager, test_user):
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    """
    response = api_manager.auth_api.login_user(test_user)

    response_data = response.json()
    registered_user = test_user.copy()
    registered_user["id"] = response_data["user"]["id"]
    return registered_user


@pytest.fixture(scope="session")
def session():
    """
    Фикстура для создания HTTP-сессии.
    """
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope="session")
def api_manager(session):
    """
    Фикстура для создания экземпляра ApiManager.
    """
    return ApiManager(session)


#############################################
                #Мои сессии
#############################################

# Базовая сессия (без авторизации)
@pytest.fixture(scope="session")
def base_session():
    # Создание сессии
    session = requests.Session()

    # Добавление заголовков в сессию
    session.headers.update(HEADERS)

    # Возвращение сессии
    return session



# Сессия обычного пользователя
@pytest.fixture(scope="session")
def user_session(base_session, test_user):
    """
    Создает/регистрирует пользователя и возвращает сессию с его токеном.
    """
    # Создаю экземпляр для работы с авторизацией на основе базовой сессии
    auth_api = AuthAPI(base_session)

    # Регистрирую пользователя
    response_register = auth_api.register_user(test_user, expected_status=201)

    # Получаю данные авторизации нового пользователя
    login_data = AuthDataBuilder.create_login_data(test_user)

    # Авторизуюсь под новым пользователем
    response_auth = auth_api.login_user(login_data, expected_status=200)

    # Достаю токен пользователя
    token = response_auth.json()["accessToken"]

    # Добавляю токен в сессию
    auth_api._update_session_headers(authorization=f"Bearer {token}")

    # Возвращает сессию с токеном обычного пользователя
    return base_session


# Сессия админа
@pytest.fixture(scope="session")
def admin_session(base_session):
    """
    Возвращает сессию с токеном админа.
    """
    # Создаю экземпляр для работы с авторизацией на основе базовой сессии
    auth_api = AuthAPI(base_session)

    # Авторизуюсь под админом и сохраняю токен в сессию base_session
    auth_api.authenticate((
        secrets.ADMIN_AUTH_DATA["email"],
        secrets.ADMIN_AUTH_DATA["password"]
    ))

    # Возвращаю base_session с админским токеном
    return base_session