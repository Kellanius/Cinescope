from custom_requester.custom_requester import CustomRequester
import constants as const

class MoviesAPI(CustomRequester):
    """
    Класс для работы с API фильмов.
    """

    def __init__(self, session):
        super().__init__(session=session, base_url = const.MOVIES_URL)


    def get_movies_info(self, expected_status=200, **kwargs):
        """
        Получение афиш фильмов
        :param expected_status: Ожидаемый статус-код
        :param kwargs: возможные параметры для фильтрации фильмов
        """

        # Объединяем дефолтные и переданные параметры
        # Переданные параметры перезаписывают дефолтные
        params = {**const.default_params_for_afisha_filter, **kwargs}

        return self.send_request(
            method="GET",
            endpoint=const.MOVIES_ENDPOINT,
            params=params,
            expected_status=expected_status
        )

