from unittest import expectedFailure

from faker import Faker
import pytest
import conftest

faker = Faker()


class TestUserAPI:
###########################
# ПОЛОЖИТЕЛЬНЫЕ ПРОВЕРКИ
###########################

    #@pytest.mark.parametrize("user_fixture_name", [
        #"super_admin",
        #"creation_admin",
        #(conftest.creation_common_user, 403), - нужно проверить отдельно, чтобы не мешать положительные поверки с отрицательными
        #"creation_super_admin"
    #])
    def test_create_user(self, creation_admin, creation_user_data):
        """
        Проверка сначала регистрации через существующего супер админа, а затем через все другие роли сгенерированные
        :param user_fixture_name:
        :param creation_user_data:
        :return:
        """

        response = creation_admin.api.user_api.create_user(creation_user_data).json()

        assert response.get("id") and response["id"] != "", "ID должен быть не пустым"
        assert response.get('email') == creation_user_data['email']
        assert response.get('fullName') == creation_user_data['fullName']
        assert response.get('roles', []) == creation_user_data['roles']
        assert response.get('verified') is True

    def test_get_user_by_locator(self, super_admin, creation_user_data):
        created_user_response = super_admin.api.user_api.create_user(creation_user_data).json()
        response_by_id = super_admin.api.user_api.get_user(created_user_response['id']).json()
        response_by_email = super_admin.api.user_api.get_user(creation_user_data['email']).json()

        assert response_by_id == response_by_email, "Содержание ответов должно быть идентичным"
        assert response_by_id.get('id') and response_by_id['id'] != '', "ID должен быть не пустым"
        assert response_by_id.get('email') == creation_user_data['email']
        assert response_by_id.get('fullName') == creation_user_data['fullName']
        assert response_by_id.get('roles', []) == creation_user_data['roles']
        assert response_by_id.get('verified') is True

    def test_get_user_by_id_common_user(self, common_user):
        common_user.api.user_api.get_user(common_user.email, expected_status=403)