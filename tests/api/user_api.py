from custom_requester.custom_requester import CustomRequester
import constants as const


class UserAPI(CustomRequester):
    """
    Класс для работы с API пользователей.
    """

    def __init__(self, session):
        super().__init__(
            session = session,
            base_url = const.BASE_URL
        )


    def get_user_info(self, user_id, expected_status=200):
        """
        Получение информации о пользователе.
        :param user_id: ID пользователя.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="GET",
            endpoint=f"{const.USER_ENDPOINT}/{user_id}",
            expected_status=expected_status
        )

    def delete_user(self, user_id, expected_status=204):
        """
        Удаление пользователя.
        :param user_id: ID пользователя.
        :param expected_status: Ожидаемый статус-код.
        """

        return self.send_request(
            method="DELETE",
            endpoint=f"{const.USER_ENDPOINT}/{user_id}",
            expected_status=expected_status
        )