import requests
import pytest
from utils.data_generator import DataGenerator
from faker import Faker
from api.api_manager import ApiManager
from utils.movie_helpers import MovieHelper
from resurses.user_creds import SuperAdminCreds
from entities.user import User
from constants import Roles


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
        "roles": [Roles.USER.value]
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

    # удаляет фильм после завершения функции, если он уже не удалён
    try:
        # Проверка, существует ли фильм всё ещё
        api_manager.movies_api.get_movie(movie_data["id"], expected_status=200)

        # Если существует, удаляет его
        MovieHelper.delete_movie_with_assert(api_manager, movie_data["id"])

    # Если фильм не существует - пропускает
    except (AssertionError, ValueError):
        pass


# Фикстура для создания сессии юзера
@pytest.fixture
def user_session():
    # Создание списка с сессиями юзеров
    user_pool = []

    # Создание сессии для юзера
    def _create_user_session():
        session = requests.Session()
        session_of_user = ApiManager(session)
        user_pool.append(session_of_user)
        return session_of_user

    yield _create_user_session

    # После тестирования закрывает все сессии
    for user in user_pool:
        user.close_session()


# Фикстура для создания юзера с ролью SUPER ADMIN
@pytest.fixture
def super_admin(user_session):
    # Создание новой сессии специально для админа
    new_session = user_session()

    # Создание админского юзера
    super_admin_user = User(
        email=SuperAdminCreds.USERNAME,
        password=SuperAdminCreds.PASSWORD,
        roles=[Roles.SUPER_ADMIN.value],
        api=new_session
    )

    # добавление токена админа в админскую сессию
    super_admin_user.api.auth_api.authenticate(super_admin_user.creds)

    # возвращение нового пользователя супер_админа
    return super_admin_user


# Фикстура формирования данных для создания пользователя
@pytest.fixture(scope="function")
def creation_user_data(test_user):
    # По сути берем все данные из test_user
    # и дополняем необходимыми для создания нового юзера
    # Обновляю ещё и логин, мыло, пароль, т.к. у test_user область видимости сессия,
    # поэтому всегда создается один и тот же юзер в разных тестах

    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()


    user_data = test_user.copy()
    user_data.update({
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "verified": True,
        "banned": False
    })
    return user_data

##############################################
# Фикстуры для пользователей с разными ролями
##############################################

# Создание обычного юзера с ролью USER
@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    common_user_data = User(
        creation_user_data["email"],
        creation_user_data["password"],
        [Roles.USER.value],
        new_session)

    # Создание юзера через админскую сессию
    super_admin.api.user_api.create_user(creation_user_data)

    # добавление токена юзера в его сессию
    common_user_data.api.auth_api.authenticate(common_user_data.creds)

    return common_user_data