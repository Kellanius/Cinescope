BASE_URL = "https://auth.dev-cinescope.coconutqa.ru"
BASE_URL_USER = "https://auth.dev-cinescope.coconutqa.ru/user"
MOVIES_URL = "https://api.dev-cinescope.coconutqa.ru"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

LOGIN_ENDPOINT = "/login"
REGISTER_ENDPOINT = "/register"
MOVIES_ENDPOINT = "/movies"

# Понятно, что данные авторизации надо прятать в отдельный файл с секретами,
# но сейчас, для ускорения процесса, я добавил это сюда
ADMIN_AUTH_DATA = {
    "email": "api1@gmail.com",
    "password": "asdqwe123Q"
}