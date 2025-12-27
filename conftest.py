import requests
import pytest
from pkg_resources import PkgResourcesDeprecationWarning

from utils.data_generator import DataGenerator, UserDataFactory
from faker import Faker
from api.api_manager import ApiManager
from utils.movie_helpers import MovieHelper
from resurses.user_creds import SuperAdminCreds
from entities.user import User
from constants import Roles


faker = Faker()

@pytest.fixture(scope="session")
def test_user_factory():
    """
    Фикстура-фабрика генерации пользовательских данных для регистрации (с дабл паролем)"
    """
    def create(**kwargs):
        data = UserDataFactory.create_user_data_for_registered(**kwargs)
        return data

    return create


@pytest.fixture(scope="session")
def creation_test_user(test_user_factory):
    """
    Готовые данные для регистрации пользователя, созданные через фабрику
    """
    test_user = test_user_factory()
    return test_user


@pytest.fixture(scope="session")
def registered_user(api_manager, creation_test_user):
    """
    Регистрация и получение данных зарегистрированного пользователя.
    """
    response = api_manager.auth_api.login_user(creation_test_user)

    response_data = response.json()
    registered_user = creation_test_user
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

@pytest.fixture(scope="function")
def create_movie_factory(super_admin):
    """
    Фабрика создания фильма
    """

    created_movies = []

    def _create_movie(expected_status=201, **kwargs):
        # генерация данных и создание фильма
        movie_data, _ = MovieHelper.generate_data_and_create_movie(super_admin.api, expected_status=expected_status, **kwargs)

        created_movies.append(movie_data)

        # возвращает данные созданного фильма
        return movie_data

    yield _create_movie

    # удаляет фильм после завершения функции, если он уже не удалён
    for movie in created_movies:
        try:
            # Проверка, существует ли фильм всё ещё
            super_admin.api.movies_api.get_movie(movie["id"], expected_status=200)

            # Если существует, удаляет его
            MovieHelper.delete_movie_with_assert(super_admin.api, movie["id"])

        # Если фильм не существует - пропускает
        except (AssertionError, ValueError):
            pass


@pytest.fixture(scope="function")
def created_movie(create_movie_factory):
    """
    Созданный фильм через фабрику
    """
    movie_data = create_movie_factory()
    return movie_data



@pytest.fixture
def user_session():
    """
    Фикстура для создания сессии юзера
    """
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


@pytest.fixture
def super_admin(user_session):
    """
    Фикстура для авторизации юзера с ролью SUPER ADMIN
    """
    # Создание новой сессии
    new_session = user_session()

    # Создание админского юзера
    super_admin_user = User(
        email=SuperAdminCreds.USERNAME,
        password=SuperAdminCreds.PASSWORD,
        roles=[Roles.SUPER_ADMIN.value],
        api=new_session
    )

    # добавление токена админа в сессию
    super_admin_user.api.auth_api.authenticate(super_admin_user.creds)

    # возвращение авторизованного пользователя супер_админа
    return super_admin_user


@pytest.fixture
def user_data_factory():
    """
    Фикстура-фабрика генератор данных для создания пользователя через API (без дабл пароля, с полями 'verified' и 'banned')
    """
    def create(**kwargs):
        user_data = UserDataFactory.create(**kwargs)
        return user_data
    return create


@pytest.fixture(scope="function")
def creation_user_data(user_data_factory):
    """
    Фикстура с готовыми данными пользователя для последующего создания
    """
    user_data = user_data_factory()
    return user_data


@pytest.fixture
def creation_user_factory(user_session, super_admin, user_data_factory):
    """
    Фабрика для создания пользователей с любыми ролями и данными
    Для создания пользователя можно просто вызвать фикстуру, тогда создастся пользователь с рандомными данными и ролью USER
    Можно указать конкретную роль и другие данные

    Фикстура создает сессию, генерирует данные (используя кастомные, если они были введены, создает пользователя,
    обновляет его роль на введенную (либо оставляет USER), добавляет токен пользователя в его сессию, возвращает данные.
    Так же все созданные пользователи собираются в список creation_users и после тестирования удаляются

    :param user_session: Фабрика сессий юзеров. Содержит в себе функцию на создание сессии
    :param super_admin: автризованная супер_админская сессия
    :param user_data_factory: фабрика для формирования данных пользователей
    :return: данные о сознанном юзере. Email, пароль, роли, сессия
    """

    created_users = []

    def _create_user(roles=Roles.USER.value, **kwargs):
        new_session = user_session()
        user_data = user_data_factory(**kwargs)

        # Создание юзера через супер-админа сессию
        response_data = super_admin.api.user_api.create_user(user_data)
        user_id = response_data.json()['id']

        # Добавление id юзера и сессию в счётчик созданных для дальнейшего удаления
        created_users.append((user_id, new_session))

        # Обновление роли пользователя
        patch_data = {"roles": [roles]}
        response_patch = super_admin.api.user_api.patch_user(patch_data, user_id)

        user = User(
            user_data["email"],
            user_data["password"],
            [roles],
            new_session)

        # добавление токена юзера в его сессию
        user.api.auth_api.authenticate(user.creds)

        return user

    yield _create_user

    # Чистка после теста
    for user_id, sessions in created_users:
        try:
            super_admin.api.user_api.delete_user(user_id, expected_status=200)
            print("Тестовый пользователь успешно удалён")
            sessions.close_session()
        except Exception as e:
            print(f"Не удалось удалить пользователя с id {user_id} из-за ошибки {e}")



# Все роли для параметризации
ALL_ROLES = [role.value for role in Roles]

@pytest.fixture(params=ALL_ROLES)
def creation_user_by_role(request, creation_user_factory):
    """
    Универсальная параметризированная фикстура для тестирования функциональности по всем ролям
    Если на проекте много ролей, то это удобнее, чем параметризировать руками каждый тест.
    """
    role = request.param
    print(f'Проверяется функционал под ролью {role}')
    return creation_user_factory(roles=role)
