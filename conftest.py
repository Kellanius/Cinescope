import requests
import pytest
from utils.data_generator import DataGenerator, UserDataFactory
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
    Фикстура-фабрика "Генерация случайного пользователя для тестов".
    """
    def create(**kwargs):
        data = UserDataFactory.create_user_duble_password(**kwargs)
        return data

    return create


@pytest.fixture(scope="session")
def registered_user(api_manager, test_user):
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    """
    response = api_manager.auth_api.login_user(test_user)

    response_data = response.json()
    registered_user = test_user()
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


# Фикстура для авторизации юзера с ролью SUPER ADMIN
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



# Фикстура-фабрика для формирования данных пользователя (без дублирования пароля)
@pytest.fixture
def user_data_factory():
    def create(**kwargs):
        user_data = UserDataFactory.create(**kwargs)
        return user_data
    return create


# Фикстура формирования данных для создания пользователя для апи (без дублирования пароля)
@pytest.fixture(scope="function")
def creation_user_data(user_data_factory):
    user_data = user_data_factory()
    return user_data


##############################################
# Фикстуры для пользователей с разными ролями
##############################################

# Создание обычного юзера с ролью USER
'''@pytest.fixture
def creation_common_user(user_session, super_admin, user_data_factory):
    new_session = user_session()

    user_data = user_data_factory()

    common_user_data = User(
        user_data["email"],
        user_data["password"],
        [Roles.USER.value],
        new_session)

    # Создание юзера через админскую сессию
    response_data = super_admin.api.user_api.create_user(user_data).json

    # добавление токена юзера в его сессию
    common_user_data.api.auth_api.authenticate(common_user_data.creds)

    yield common_user_data

    try:
        super_admin.api.user_api.delete_user(response_data["id"], expected_status=200)
    except Exception as e:
        print(f"Не удалось удалить пользователя {response_data['id']}: {e}")'''


# Фикстура-фабрика создания юзеров
@pytest.fixture
def creation_user_factory(user_session, super_admin, user_data_factory):
    """
    Фабрика для создания пользователей с любыми ролями и данными
    Для создания пользователя можно просто вызвать фикстуру, тогда создастся пользователь с рандомными данными и ролью USER
    Можно указать конкретную роль и другие данные

    Фикстура создает сессию, генерирует данные (используя кастомные, если они были введены, создает пользователя,
    обновляет его роль на введенную (либо оставляет USER), добавляет токен пользователя в его сессию, возвращает данные.
    Так же все созданные пользователи собираются в список creation_users и после тестирования удаляются

    :param user_session:
    :param super_admin:
    :param user_data_factory:
    :return:
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
            
        



# Создание админа с ролью ADMIN
@pytest.fixture
def creation_admin(user_session, super_admin, user_data_factory, creation_common_user):
    
    admin_user_data = creation_common_user
    
    
    
    
    
    '''new_session = user_session()

    admin_user_data = user_data_factory()

    # Создание через API пользователя
    response_create = super_admin.api.user_api.create_user(admin_user_data)

    # Вытаскивание id пользователя из ответа
    user_id = response_create.json()['id']

    # Добавление роли админа, т.к. любой пользователь создается изначально с ролью USER
    patch_data = {"roles": [Roles.ADMIN.value]}

    # Изменение данных пользователя (теперь он имеет роль админа)
    response_patch = super_admin.api.user_api.patch_user(patch_data, user_id)

    # Создание объекта USER с ролью ADMIN
    admin_data = User(
        email=admin_user_data["email"],
        password=admin_user_data["password"],
        roles=[Roles.ADMIN.value],
        api=new_session
    )

    # добавление токена админа в его сессию
    admin_data.api.auth_api.authenticate(admin_data.creds)

    yield admin_data

    # Чистка после теста
    try:
        super_admin.api.user_api.delete_user(user_id, expected_status=200)
        print("Тестовый админ успешно удалён")
    except Exception as e:
        print(f"Не удалось удалить админа с id {user_id} из-за ошибки {e}")'''


    '''# Создание супер-админа с ролью SUPER_ADMIN
    @pytest.fixture
    def creation_super_admin(user_session, super_admin, creation_user_data):
        new_session = user_session()
    
        super_admin_data = User(
            creation_user_data["email"],
            creation_user_data["password"],
            [Roles.SUPER_ADMIN.value],
            new_session
        )
    
        super_admin.api.user_api.create_user(creation_user_data)
    
        super_admin_data.api.auth_api.authenticate(super_admin_data.creds)
    
        return super_admin_data'''