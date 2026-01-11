import constants as const
from utils.data_generator import DataGenerator
from utils.assertions.assert_helpers import CustomAssertions
from faker import Faker
import random
from utils.movie_helpers import MovieHelper
import pytest
from utils.assertions.movie_assertions import MovieCustomAssertions
from db_requester.db_helpers import DBHelper


def test_db_requests(super_admin, db_helper, created_test_user):
    assert created_test_user == db_helper.get_user_by_id(created_test_user.id)
    assert db_helper.user_exist_by_email("api1@gmail.com")