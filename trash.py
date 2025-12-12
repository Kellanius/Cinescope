# то что насоздавал, но оно не понадобилось (но может понадобиться в будущем, хз)


##################################################################################################
# Оказалось что imageUrl это url изображения (шок), а не url фильма, поэтому данный генератор не нужен
"""# Генератор рандомного URL для фильма
@staticmethod
def generate_url_for_movies(movie_name):
    """
# Генерация url. Принимает имя фильма и делает из него url без пробелов и спец символов
#:param movie_name: имя фильма
"""
    # Проверка всех символов на наличие пробелов и замена их на "_"
    url = movie_name.replace(" ","_")
    url = url.replace("?","")
    url = url.replace(":", "")

    # Возвращаем корректный url фильма
    return url"""
##################################################################################################


# Пока убрал, т.к. понял, что это скорее усложнение, чем оптимизация
"""# Проверка того, что левый параметр больше или меньше правого
@staticmethod
def assert_more_or_less(expectation, actual, more_or_less, message=None):
    # Проверка что expectation "more_or_less" actual. Есть только 2 варианта more_or_less - "more" и "less"

    if more_or_less == "more":
        if message is None:
            message = f"Ожидалось что {expectation} больше, чем {actual}"
        assert expectation >= actual, message

    elif more_or_less == "less":
        if message is None:
            message = f"Ожидалось что {expectation} меньше, чем {actual}"
        assert expectation <= actual, message

    else:
        raise ValueError(f"{more_or_less} должно иметь только значение 'more' или 'less'")"""




#############################################
#Мои сессии (в итоге не используются,
#т.к. после их создания я внезапно полностью понял работу сессий
# и осознал, зачем нужен API_Manager + перестал путаться в связях и уровнях абстракции вокруг сессий
#############################################
"""
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
#Создает/регистрирует пользователя и возвращает сессию с его токеном.
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
#Возвращает сессию с токеном админа.
"""
# Создаю экземпляр для работы с авторизацией на основе базовой сессии
auth_api = AuthAPI(base_session)

# Авторизуюсь под админом и сохраняю токен в сессию base_session
auth_api.authenticate((
    secrets.ADMIN_AUTH_DATA["email"],
    secrets.ADMIN_AUTH_DATA["password"]
))

# Возвращаю base_session с админским токеном
return base_session"""