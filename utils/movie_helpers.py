from utils.data_generator import DataGenerator
import constants as const
from db_requester.db_helpers import DBHelper



class MovieHelper:

    # Получение афиши и перевод ответа в json формат
    @staticmethod
    def get_afisha(session, data="default", correct_data=True, expected_status = 200, **kwargs):
        """
        :param session: сессия
        :param data: может принимать только 3 значения:
        "default" - дефолтные данные фильтра
        "random" - генерирует рандомные корректные данные
        data=словарь с данными - принимает словарь с данными фильтров для афиши
        :param correct_data: True - рандомные данные генерируются корректными, False - данные генерируются некорректными
        :param expected_status: Ожидаемый статус-код
        :param kwargs: кастомные параметры для афиши
        :return: афиша в json формате
        """

        # По-умолчанию при использовании данного метода выводится афиша с дефолтными фильтрами
        if data == "default":
            params = const.default_params_for_afisha_filter.copy()

        # Если data="random", то выводится афиша с рандомными фильтрами
        elif data == "random":
            params = DataGenerator.generate_random_data_for_afisha_filter(correct_data=correct_data)

        # Если data это словарь, то выводится афиша с вставленными в словарь данными
        elif isinstance(data, dict):
            params = data

        # Если data это непонятно что, то выводится ошибка
        else:
            raise ValueError(f'{data} должно иметь значение "default", "random" или словарь')


        # Обновляем параметры данными введенными вручную
        params.update(kwargs)

        # Запрос на получение афиши
        response = session.movies_api.get_movies(**params, expected_status=expected_status)

        return response.json(), params


    # Генерация, создание фильма и перевод данных в json формат
    @staticmethod
    def generate_data_and_create_movie(session, db_helper, expected_status = 201, **kwargs):
        """
        :param session: сессия
        :param expected_status: ожидаемый статус-код ответа
        :param kwargs: кастомные параметры для фильма
        :param db_helper: фикстура ДБ хелпера
        :return: response_get_movie_info_data - данные о фильме возвращенные по api, random_data_for_new_movie - сгенерированные данные о фильме
        """

        

        # Генерация рандомных данных для фильма
        random_data_for_new_movie = DataGenerator.generate_random_data_for_new_movies(**kwargs)

        # Проверка в БД, что фильм со сгенерированным названием отсутствует
        assert db_helper.get_movie_by_name(random_data_for_new_movie["name"]) is None, "Фильм уже существует в БД"

        # Запрос на создание фильма с рандомными данными
        response_create_movie = session.movies_api.create_new_movies(random_data_for_new_movie, expected_status=expected_status)

        # Перевод данных ответа о создании фильма в json формат
        create_movie_data = response_create_movie.json()

        return create_movie_data, random_data_for_new_movie


    # Проверка, что фильм создан и возврат ответа в json формате
    @staticmethod
    def get_movie_data(session, movie_id, expected_status=200):
        """
        :param session: сессия
        :param movie_id: id фильма
        :param expected_status: ожидаемый статус ответа
        :return: данные о фильме в json формате
        """

        # Проверка, что фильм создан
        response_get_movie = session.movies_api.get_movie(movie_id, expected_status=expected_status)

        # Перевод данных ответа с информацией о фильме в json формат
        get_movie_data = response_get_movie.json()

        return get_movie_data


    # Генерация новых данных и замена старых данных на новые
    @staticmethod
    def generate_data_and_patch_movie(session, old_movie_data_for_patch, expected_status=200, **kwargs):
        """
        :param session: сессия
        :param old_movie_data_for_patch: данные фильма, которые собираемся менять
        :param expected_status: ожидаемый статус-код
        :param kwargs: кастомные параметры для редактирования фильма
        :return: ответ с сервера об обновлении информации о фильме
        """

        # Генерация новых данных для замены старых
        new_movie_data_for_patch = DataGenerator.generate_random_data_for_patch_movies_info(old_movie_data_for_patch)

        # обновление сгенерированных данных указанными в функции
        new_movie_data_for_patch.update(kwargs)

        # Замена данных фильма на новые
        response_patch_movie = session.movies_api.patch_movie(old_movie_data_for_patch["id"], new_movie_data_for_patch, expected_status=expected_status)

        # Перевод ответа об изменении данных о фильме в json формат
        patch_movie_data = response_patch_movie.json()

        return patch_movie_data


    # Удаление фильма с проверкой
    @staticmethod
    def delete_movie_with_assert(session, movie_id, db_helper, expected_status=404):
        """
        :param session: сессия
        :param movie_id: id фильма, который собираемся удалить
        :param db_helper: фикстура дб хелпера для работы с бд (хранит сессию бд)
        :param expected_status: ожидаемый статус запроса на проверку существования удаленного фильма
        :return: ответ сервера об удалении фильма
        """

        #### Удаление фильма ####

        # Если фильма не существует, то создаём через бд
        if db_helper.get_movie_by_id(movie_id) is None:

            # Генерация данных для создания фильма через бд
            new_movie_data = DataGenerator.generate_movie_data_for_db()

            # Создание фильма через БД
            new_movie = db_helper.create_test_movie(new_movie_data)

            # Получение id фильма для удаления
            movie_id = new_movie.id


        # Запрос на удаление фильма
        response_delete_movie = session.movies_api.delete_movie(movie_id)

        # Перевод ответа об удалении фильма в json формат
        delete_movie_data = response_delete_movie.json()

        # Проверка, что фильма больше не существует (GET запрос на получение инфы о фильме)
        session.movies_api.get_movie(delete_movie_data["id"], expected_status=expected_status)

        return delete_movie_data
