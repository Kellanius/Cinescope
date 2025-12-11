from custom_requester.custom_requester import CustomRequester
import constants as const
from utils.data_generator import DataGenerator

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

    def change_movie_info(self, movie_id, movie_data, expected_status=200):
        """
        Создание нового фильма
        :param movie_id: id редактируемого фильма
        :param movie_data: текущие данные фильма (нужны для того, чтобы заменить локацию)
        :param expected_status: Ожидаемый статус-код
        :return: post запрос о редактировании фильма
        """

        # Генерируем новые данные на которые будем заменять старые
        new_movie_data_for_change = DataGenerator.generate_random_data_for_new_movies()

        # Заменяем в новых данных "location" на отличное от текущего "location", чтобы проверить изменение этого параметра
        if movie_data["location"] == "SPB":
            new_movie_data_for_change["location"] = "MSK"
        else:
            new_movie_data_for_change["location"] = "SPB"

        # Отправляем PATCH запрос на изменение данных у фильма на новые и возвращаем ответ
        return self.send_request(
            method="PATCH",
            endpoint=f"{const.MOVIES_ENDPOINT}/{movie_id}",
            data=new_movie_data_for_change,
            expected_status=expected_status
        )

    def delete_movie(self, movie_id, expected_status=200):
        """
        :param movie_id: id удаляемого фильма
        :param expected_status: Ожидаемый статус-код
        :return: ответ от сервера об удалении фильма
        """

        return self.send_request(
            method="DELETE",
            endpoint=f"{const.MOVIES_ENDPOINT}/{movie_id}",
            expected_status=expected_status
        )