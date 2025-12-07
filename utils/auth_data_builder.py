# Строительство данных для авторизации

class AuthDataBuilder:
    @staticmethod
    def create_login_data(user=None, email=None, password=None):
        """
        :param user: данные пользователя
        :param email: вручную введенный email (заменяет email пользователя из параметра user)
        :param password: вручную введенный password (заменяет password пользователя из параметра user)
        :return: итоговые сконструированные авторизационные данные пользователя
        """

        login_data = {
            "email": "",
            "password": ""
        }

        if user is not None:
            login_data = {
                "email": user["email"],
                "password": user["password"]
            }

        if email is not None:
            login_data["email"] = email

        if password is not None:
            login_data["password"] = password

        return login_data