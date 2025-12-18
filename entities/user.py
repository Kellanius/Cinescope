from api.api_manager import ApiManager

class User:
    def __init__(self, email: str, password: str, roles: list, api: ApiManager):
        self.email = email
        self.password = password
        self.roles = roles
        self.api = api              # Сюда будем передавать экземпляр API Manager для запросов


    # Декоратор @property делает метод creds доступным как атрибут
    # print(user.creds)  # ('test@example.com', '123456')
    @property
    def creds(self):
        """Возвращает кортеж (email, password)"""
        return self.email, self.password