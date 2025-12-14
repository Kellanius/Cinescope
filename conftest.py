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
from utils.movie_helpers import MovieHelper

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


# Фикстура для создания фильма
@pytest.fixture(scope="function")
def created_movie(api_manager):
    # генерация данных и создание фильма
    movie_data, _ = MovieHelper.generate_data_and_create_movie(api_manager)

    # возвращает данные созданного фильма
    yield movie_data

    # удаляет фильм после завершения сессии, если он уже не удалён
    try:
        # Проверка, существует ли фильм всё ещё
        api_manager.movies_api.get_movie_info(movie_data["id"], expected_status=200)

        # Если существует, удаляет его
        MovieHelper.delete_movie_with_assert(api_manager, movie_data["id"])

    # Если фильм не существует - пропускает
    except (AssertionError, ValueError):
        pass
