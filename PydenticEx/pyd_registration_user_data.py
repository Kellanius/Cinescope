from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError
from venv import logger
import pytest
from utils.data_generator import UserDataFactory
from typing import Optional
from enum import Enum
from constants import Roles
from typing import List








class UserDataForRegistration(BaseModel):
    email: str
    fullName: str
    password: str
    passwordRepeat: Optional[str] = None
    roles: List[Roles] = Field(default_factory=lambda: Roles.USER, min_length=1)
    verified: Optional[bool] = None
    banned: Optional[bool] = None


    @field_validator("email")
    def check_email(cls, v):
        if not "@" in v:
            raise ValueError("email должен содержать символ @")
        return v

    @field_validator("password")
    def check_password(cls, v):
        if len(v) < 8:
            raise ValueError("Пароль должен содержать не меньше 8 символов")
        return v

    @model_validator(mode="after")
    def check_password_repeat(self):

        print(f"DEBUG: password={self.password}, passwordRepeat={self.passwordRepeat}")

        if self.passwordRepeat is not None:
            if self.password != self.passwordRepeat:
                raise ValueError(f"Пароли {self.password} и {self.passwordRepeat} не совпадают")
        return self




@pytest.fixture(scope="session")
def test_user_factory():
    """
    Фикстура-фабрика генерации пользовательских данных для регистрации (с дабл паролем)"
    """
    def create(**kwargs):
        data = UserDataFactory.create_user_data_for_registered(**kwargs)
        return data

    return create


@pytest.fixture(scope="session")
def creation_test_user(test_user_factory):
    """
    Готовые данные для регистрации пользователя, созданные через фабрику
    """
    test_user = test_user_factory()
    return test_user


def test_pydentic_user_registration(creation_test_user, test_user_factory):
    user_incorrect_email = test_user_factory(email="sos@al?", password="322qwver", passwordRepeat="322qwver")
    user_incorrect_email["passwordRepeat"] = "322qwver2"

    user2 = UserDataForRegistration(**user_incorrect_email)
    logger.info(f"{user2=}")

    user = UserDataForRegistration(**creation_test_user)
    logger.info(f"{user=}")


    json_data = user.model_dump_json(exclude_unset=True)
    logger.info(f"{json_data=}")

    new_user = user.model_validate_json(json_data)
    logger.info(f"{new_user=}")



@pytest.fixture
def user_data_factory():
    """
    Фикстура-фабрика генератор данных для создания пользователя через API (без дабл пароля, с полями 'verified' и 'banned')
    """
    def create(**kwargs):
        user_data = UserDataFactory.create(**kwargs)
        return user_data
    return create


@pytest.fixture(scope="function")
def creation_user_data(user_data_factory):
    """
    Фикстура с готовыми данными пользователя для последующего создания
    """
    user_data = user_data_factory()
    return user_data


def test_pydentic_user_creation(creation_user_data, user_data_factory):
    user_incorrect_email = user_data_factory(email="sos@al?", password="322")
    user2 = UserDataForRegistration(**user_incorrect_email)
    logger.info(f"{user2=}")

    user = UserDataForRegistration(**creation_user_data)
    logger.info(f"{user=}")


    json_data = user.model_dump_json(exclude_unset=False)
    logger.info(f"{json_data=}")

    new_user = user.model_validate_json(json_data)
    logger.info(f"{new_user=}")