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

# Значения по умолчанию для фильтра фильмов из документации
default_params_for_afisha_filter = {
    "pageSize": 10,
    "page": 1,
    "minPrice": 1,
    "maxPrice": 1000,
    "published": True,
    "genreId": 1,
    "createdAt": "asc"
}