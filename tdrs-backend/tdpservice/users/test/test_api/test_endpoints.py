"""Basic API Endpoint Tests."""
from unittest.mock import ANY, patch

from rest_framework import status
import pytest


@pytest.mark.usefixtures('db')
class UserAPITestsBase:
    """A base test class for tests that interact with the UserViewSet.

    Provides several fixtures and methods that are commonly used between tests.
    Intended to simplify creating tests for different user flows.
    """

    root_url = '/v1/users/'

    @pytest.fixture
    def user(self):
        """User instance that will be used to log in to the API client.

        This fixture must be overridden in each child test class.
        """
        raise NotImplementedError()

    @pytest.fixture
    def api_client(self, api_client, user):
        """Provide an API client that is logged in with the specified user."""
        api_client.login(username=user.username, password='test_password')
        return api_client
    
    @pytest.fixture
    def empty_profile_data(self):
        return {
                  "first_name": "",
                  "last_name": "",
                  "stt": null,
                  "region": null,
                  "groups": [],
                  "is_superuser": false,
                  "is_staff": false,
                  "last_login": null,
                  "date_joined": null,
                  "access_request": false
                }
    
    def list_users(self, api_client):
        """List users"""
        return api_client.get(self.root_url)
    
    def get_user(self, api_client, user_id):
        """Get a specific user"""
        return api_client.get(f'{self.root_url}{user_id}')
    
    def set_profile(self, api_client, profile_data):
        return api_client.post(f'{self.root_url}set_profile', profile_data)
    
    def request_access(self, api_client, profile_data):
        return api_client.post(f'{self.root_url}request_access', profile_data)
    
    def get_roles(self, api_client):
        """Return a list of roles"""
        return api_client.get(f'{self.root_url}roles')


class TestUserAPIUnauthenticatedUser(UserAPITestsBase):
    @pytest.fixture
    def user(self):
        """User instance not used in this test class"""
        raise NotImplementedError()

    @pytest.fixture
    def api_client(self, api_client, user):
        """Provide an API client that is not logged in with a specified user."""
        return api_client
    
    def test_list_users(self, api_client):
        """List users"""
        return api_client.get(self.root_url)
    
    def test_get_user(self, api_client, user_id):
        """Get a specific user"""
        return api_client.get(f'{self.root_url}{user_id}')
    
    def test_set_profile(self, api_client, profile_data):
        return api_client.post(f'{self.root_url}set_profile', profile_data)
    
    def test_request_access(self, api_client, profile_data):
        return api_client.post(f'{self.root_url}request_access', profile_data)
    
    def test_get_roles(self, api_client):
        """Return a list of roles"""
        return api_client.get(f'{self.root_url}roles')


class TestUserAPIAuthenticatedUserNoRole(UserAPITestsBase):
    pass


class TestUserAPIDataAnalystUser(UserAPITestsBase):
    pass


class TestUserAPIAdminUser(UserAPITestsBase):
    pass