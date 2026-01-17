from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError
from venv import logger
import pytest
from typing import Optional
from enum import Enum
from constants import Roles
from typing import List
import datetime


class TestUser(BaseModel):
    email: str
    fullName: str
    password: str
    """passwordRepeat: str = Field(..., min_length=1, max_length=20, description="Пароли должны совпадать")"""
    roles: List[Roles] = Field(default_factory=lambda: Roles.USER, min_length=1)
    verified: Optional[bool] = True
    banned: Optional[bool] = False

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

    """@field_validator("passwordRepeat")
    def check_password_repeat(cls, value: str, info) -> str:
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return value"""

    # Добавляем кастомный JSON-сериализатор для Enum
    class Config:
        json_encoders = {
            Roles: lambda v: v.value  # Преобразуем Enum в строку
        }


class RegisterUserResponse(BaseModel):
    id: str
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    fullName: str
    verified: bool
    banned: bool
    roles: List[Roles]
    createdAt: str

    @field_validator("createdAt")
    def validate_created_at(cls, value: str) -> str:
        # Валидатор для проверки формата даты и времени (ISO 8601).
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Некорректный формат даты и времени. Ожидается формат ISO 8601.")
        return value



class TestMovieAPI(BaseModel):
    name: str
    price: int = Field(gt=0)
    description: str
    imageUrl: str
    location: str
    published: bool
    genreId: int = Field(gt=0, lt=4)


class TestMovieDB(BaseModel):
    id: str
    name: str
    price: int = Field(gt=0)
    description: str
    image_url: str
    location: str
    published: bool
    rating: float = Field(ge=1.0, le=10.0)
    genre_id: int = Field(gt=0, lt=4)
    created_at: datetime.datetime