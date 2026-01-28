import requests
import pytest
from pkg_resources import PkgResourcesDeprecationWarning
import pytest
from playwright.sync_api import sync_playwright
from common.tools import Tools


from utils.data_generator import DataGenerator, UserDataFactory
from faker import Faker
from api.api_manager import ApiManager
from utils.movie_helpers import MovieHelper
from resources.user_creds import SuperAdminCreds
from entities.user import User
from constants import Roles
from sqlalchemy.orm import Session
from db_requester.db_client import get_db_session
from db_requester.db_helpers import DBHelper
import pytest
import allure
import random
import time
import os
from playwright_helpers.page_object import CinescopeLoginPage, CinescopeMoviePage




#os.environ["PWDEBUG"] = "0"
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


@pytest.fixture(scope="function")
def registered_user(super_admin, creation_test_user):
    """
    Регистрация и получение данных зарегистрированного пользователя.
    """
    response = super_admin.api.auth_api.register_user(creation_test_user)
    response_data = response.json()

    registered_user_data = {"email": creation_test_user["email"],
                       "password": creation_test_user["password"],
                       "id": response_data["id"]
                       }
    yield registered_user_data
    super_admin.api.user_api.delete_user(registered_user_data["id"])


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
            super_admin.api.movies_api.delete_movie(movie["id"])

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


# Фикстура для создания сессии БД
@pytest.fixture(scope="module")
def db_session() -> Session:
    """
    Фикстура, которая создает и возвращает сессию для работы с базой данных
    После завершения теста сессия автоматически закрывается
    """
    db_session = get_db_session()
    yield db_session
    db_session.close()


@pytest.fixture(scope="function")
def db_helper(db_session) -> DBHelper:
    """
    Фикстура для экземпляра хелпера
    """
    db_helper = DBHelper(db_session)
    return db_helper


@pytest.fixture(scope="function")
def created_test_user(db_helper):
    """
    Фикстура, которая создает тестового пользователя в БД
    и удаляет его после завершения теста
    """
    user = db_helper.create_test_user(DataGenerator.generate_user_data_for_db())
    yield user

    # Cleanup после теста
    if db_helper.get_user_by_id(user.id):
        db_helper.delete_user(user)




@pytest.fixture
def delay_between_retries():
    time.sleep(2)
    yield






####################### Фикстуры для UI тестов ##################################
DEFAULT_UI_TIMEOUT = 10000


@pytest.fixture(scope="session")
def browser(playwright):
    browser = playwright.chromium.launch(headless=False)  # headless=True для CI/CD, headless=False для локальной разработки
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser):
    context = browser.new_context()
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    context.set_default_timeout(DEFAULT_UI_TIMEOUT)
    yield context
    log_name = f"trace_{Tools.get_timestamp()}.zip"
    trace_path = Tools.files_dir('playwright_trace', log_name)
    context.tracing.stop(path=trace_path)
    context.close()


@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture(scope="function")
def login_page(page):
    # Создание экземпляра класса
    login_page = CinescopeLoginPage(page)
    return login_page


@pytest.fixture(scope="function")
def auth_context(browser, registered_user):
    """
    Контекст с авторизованным пользователем.
    """
    # Логинимся один раз за сессию
    auth_ctxt = browser.new_context()
    auth_pg = auth_ctxt.new_page()


    auth_pg.goto("https://dev-cinescope.coconutqa.ru/login")
    auth_pg.fill('input[name="email"]', registered_user["email"])
    auth_pg.fill('input[name="password"]', registered_user["password"])
    auth_pg.locator("form").get_by_role("button", name="Войти").click()
    notification_locator = auth_pg.get_by_text("Вы вошли в аккаунт")
    notification_locator.wait_for(state="visible")

    # ================================

    # Сохранение куки в память
    storage_state = auth_ctxt.storage_state()

    # Закрытие временного контекста
    auth_pg.close()
    auth_ctxt.close()

    # Создание основного контекста с сохранённой авторизацией
    auth_context = browser.new_context(
        storage_state=storage_state,
        viewport={'width': 1920, 'height': 1080}
    )
    auth_context.set_default_timeout(10000)

    yield auth_context

    # После всех тестов контекст закроется сам
    auth_context.close()


@pytest.fixture(scope="function")
def auth_page(auth_context):
    """Страница с уже авторизованным пользователем"""
    a_page = auth_context.new_page()
    yield a_page
    a_page.close()