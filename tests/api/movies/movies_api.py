from custom_requester.custom_requester import CustomRequester
import constants as const

class MoviesAPI(CustomRequester):
    """
    Класс для работы с API фильмов.
    """

    def __init__(self, session):
        super().__init__(session=session, base_url = const.MOVIES_URL)


    def get_afisha_info(self, expected_status=200, **kwargs):
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

    def get_movie_info(self, movie_id, expected_status=200):
        """
        :param movie_id: айди фильма
        :return: информация о фильме
        """

        return self.send_request(
            method="GET",
            endpoint=f"{const.MOVIES_ENDPOINT}/{movie_id}",
            expected_status=expected_status
        )


    def create_new_movies(self, data_for_new_movies, expected_status=201):
        """
        Создание нового фильма
        :param expected_status: Ожидаемый статус-код
        :param data_for_new_movies: параметры для создания фильма
        """

        return self.send_request(
            method="POST",
            endpoint=const.MOVIES_ENDPOINT,
            data=data_for_new_movies,
            expected_status=expected_status
        )
