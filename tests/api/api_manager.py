from tests.api.auth_api import AuthAPI
from tests.api.user_api import UserAPI
from tests.api.movies.movies_api import MoviesAPI

class ApiManager:
    """
    Класс для управления API-классами с единой HTTP-сессией.
    """
    def __init__(self, session):
        """
        Инициализация ApiManager.
        :param session: HTTP-сессия, используемая всеми API-классами.
        """
        self.session = session
        self.auth_api = AuthAPI(session)
        self.user_api = UserAPI(session)
        self.movies_api = MoviesAPI(session)

    # функция для возможности закрытия сессии
    def close_session(self):
        self.session.close()