"""Basic User API Endpoint Tests."""

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
    def profile_data(self):
        """Provide an generic profile data for users to change in different tests."""
        return {
                  "first_name": "Test",
                  "last_name": "Test",
                  "stt": '',
                  "groups": [],
                  "is_superuser": False,
                  "is_staff": False,
                  "last_login": None,
                  "access_request": False
                }

    def list_users(self, api_client):
        """List users."""
        return api_client.get(self.root_url)

    def get_user(self, api_client, user_id):
        """Get a specific user."""
        return api_client.get(f'{self.root_url}{user_id}/')

    def set_profile(self, api_client, profile_data):
        """Patch a users profile data."""
        return api_client.patch(f'{self.root_url}set_profile/', profile_data)

    def request_access(self, api_client, profile_data):
        """Patch a users access request state."""
        return api_client.patch(f'{self.root_url}request_access/', profile_data)

    def get_roles(self, api_client):
        """Get a list of roles."""
        return api_client.get('/v1/roles/')


class TestUserAPIUnauthenticatedUser(UserAPITestsBase):
    """Test class to test API endpoints with an un-authenticated user."""

    @pytest.fixture
    def user(self, data_analyst):
        """Override the default user with data_analyst for our tests.

        Just filling the requirement here. User not used.
        """
        return data_analyst

    @pytest.fixture
    def api_client(self, api_client, user):
        """Provide an API client that is not logged in with a specified user."""
        return api_client

    def test_list_users(self, api_client):
        """List users, expect 403 with un-authenticated user."""
        response = self.list_users(api_client)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_user(self, api_client, user):
        """Get a specific user, expect 403 with un-authenticated user."""
        response = self.get_user(api_client, user.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_set_profile(self, api_client, profile_data):
        """Patch user profile data, expect 403 with un-authenticated user."""
        response = self.set_profile(api_client, profile_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_request_access(self, api_client, profile_data):
        """Request access, expect 403 with un-authenticated user."""
        response = self.request_access(api_client, profile_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_roles(self, api_client):
        """Get roles, expect 403 with un-authenticated user."""
        response = self.get_roles(api_client)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUserAPIAuthenticatedUserNoRole(UserAPITestsBase):
    """Test class to test API endpoints with an authenticated user that has no group."""

    @pytest.fixture
    def user(self, user):
        """Override the default user with user with no group for our tests."""
        return user

    @pytest.fixture
    def api_client(self, api_client, user):
        """Provide an API client that is not logged in with a specified user."""
        api_client.login(username=user.username, password='test_password')
        return api_client

    def test_list_users(self, api_client):
        """List users, expect 403 since user has no role."""
        response = self.list_users(api_client)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_user(self, api_client, user):
        """Get a specific user, expect 403 since user has no role."""
        response = self.get_user(api_client, user.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_set_profile(self, api_client, profile_data):
        """Patch user profile data, expect 403 since user has no role."""
        response = self.set_profile(api_client, profile_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_request_access(self, api_client, user, stt, profile_data):
        """Request access, expect 200 with profile updated appropriately."""
        profile_data['stt'] = stt.id
        profile_data['access_request'] = True
        response = self.request_access(api_client, profile_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id
        assert response.data['first_name'] == "Test"
        assert response.data['last_name'] == "Test"
        assert response.data['access_request']

    def test_get_roles(self, api_client):
        """Get roles, expect 403 with un-authenticated user."""
        response = self.get_roles(api_client)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUserAPIDataAnalystUser(UserAPITestsBase):
    """Test class to test API endpoints with a data analyst user."""

    @pytest.fixture
    def user(self, data_analyst):
        """Override the default user with data_analyst for our tests."""
        return data_analyst

    @pytest.fixture
    def api_client(self, api_client, user):
        """Provide an API client that is not logged in with a specified user."""
        api_client.login(username=user.username, password='test_password')
        return api_client

    def test_list_users(self, api_client, user):
        """List users, expect 200 with with only one user returned."""
        response = self.list_users(api_client)
        results = response.data['results']
        assert response.status_code == status.HTTP_200_OK
        assert len(results) == 1
        assert results[0]['id'] == user.id

    def test_get_user(self, api_client, user):
        """Get a specific user, expect 200."""
        response = self.get_user(api_client, user.id)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id

    def test_get_other_user(self, api_client, ofa_admin):
        """Get a specific user, expect 403 since the logged in user is not an admin."""
        response = self.get_user(api_client, ofa_admin.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_set_profile(self, api_client, user, profile_data):
        """Patch user profile data, expect 200 with profile updated appropriately."""
        profile_data['stt'] = user.stt.id
        response = self.set_profile(api_client, profile_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id
        assert response.data['first_name'] == "Test"
        assert response.data['last_name'] == "Test"

    def test_request_access(self, api_client, user, profile_data):
        """Request access, expect 200 with profile updated appropriately."""
        profile_data['stt'] = user.stt.id
        profile_data['access_request'] = True
        response = self.request_access(api_client, profile_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id
        assert response.data['first_name'] == "Test"
        assert response.data['last_name'] == "Test"
        assert response.data['access_request']

    def test_get_roles(self, api_client):
        """Get roles, expect 200."""
        response = self.get_roles(api_client)
        assert response.status_code == status.HTTP_403_FORBIDDEN

class TestUserAPIAdminUser(UserAPITestsBase):
    """Test class to test API endpoints with an admin user."""

    @pytest.fixture
    def user(self, ofa_system_admin, stt):
        """Override the default user with ofa_system_admin for our tests."""
        ofa_system_admin.stt = stt
        ofa_system_admin.save()
        return ofa_system_admin

    @pytest.fixture
    def api_client(self, api_client, user):
        """Provide an API client that is not logged in with a specified user."""
        api_client.login(username=user.username, password='test_password')
        return api_client

    def test_list_users(self, api_client, user):
        """List users, expect 200 with all users returned."""
        response = self.list_users(api_client)
        results = response.data['results']
        assert response.status_code == status.HTTP_200_OK
        assert len(results) == 2

    def test_get_user(self, api_client, user):
        """Get a specific user, expect 200 and ability to get any user."""
        response = self.get_user(api_client, user.id)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id

    def test_get_other_user(self, api_client, user, data_analyst):
        """Get a specific user, expect 403 since the logged in user is not an admin."""
        response = self.get_user(api_client, data_analyst.id)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == data_analyst.id
        assert response.data['id'] != user.id

    def test_set_profile(self, api_client, user, profile_data):
        """Patch user profile data, expect 200 with profile updated appropriately."""
        profile_data['stt'] = user.stt.id
        response = self.set_profile(api_client, profile_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id
        assert response.data['first_name'] == "Test"
        assert response.data['last_name'] == "Test"

    def test_request_access(self, api_client, user, profile_data):
        """Request access, expect 200 with profile updated appropriately."""
        profile_data['stt'] = user.stt.id
        profile_data['access_request'] = True
        response = self.request_access(api_client, profile_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id
        assert response.data['first_name'] == "Test"
        assert response.data['last_name'] == "Test"
        assert response.data['access_request']

    def test_get_roles(self, api_client):
        """Get roles, expect 200."""
        response = self.get_roles(api_client)
        assert response.status_code == status.HTTP_200_OK
