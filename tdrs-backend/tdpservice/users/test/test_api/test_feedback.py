"""Basic Feedback API Endpoint Tests."""

from django.contrib.auth.models import AnonymousUser
from rest_framework import status
import pytest
from tdpservice.users.test.factories import FeedbackFactory


@pytest.mark.usefixtures('db')
class FeedbackAPITestsBase:
    """A base test class for tests that interact with the FeedbackViewSet.

    Provides several fixtures and methods that are commonly used between tests.
    Intended to simplify creating tests for different user flows.
    """

    root_url = '/v1/feedback/'

    @pytest.fixture
    def user(self):
        """User instance that will be used to log in to the API client.

        This fixture must be overridden in each child test class.
        """
        raise NotImplementedError()

    @pytest.fixture
    def feedback(self, user):
        """Feedback instance."""
        return FeedbackFactory.create(user=user)

    @pytest.fixture
    def api_client(self, api_client, user):
        """Provide an API client that is logged in with the specified user."""
        api_client.login(username=user.username, password='test_password')
        return api_client

    @pytest.fixture
    def feedback_data(self, user):
        """Provide an generic feedback data for users to change in different tests."""
        return {
                  "user": user.id,
                  "rating": 3,
                  "feedback": ""
                }

    def list_feedback(self, api_client):
        """List feedback."""
        return api_client.get(self.root_url)

    def get_feedback(self, api_client, feedback_id):
        """Get a specific feedback."""
        return api_client.get(f'{self.root_url}{feedback_id}/')

    def create_feedback(self, api_client, feedback_data):
        """Post feadback."""
        return api_client.post(f'{self.root_url}', feedback_data)


class TestFeedbackAPIAnonymousUser(FeedbackAPITestsBase):
    """Test class to test API endpoints with an anonymous user."""

    @pytest.fixture
    def user(self, data_analyst):
        """Override to use builtin anonymous user."""
        return AnonymousUser()

    @pytest.fixture
    def feedback(self, user):
        """Feedback instance."""
        return FeedbackFactory.create(user=None)

    @pytest.fixture
    def api_client(self, api_client, user):
        """Provide an API client that is anonymous."""
        return api_client

    def test_list_feedback(self, api_client):
        """List feedback, expect 200 and no data with anonymous user."""
        response = self.list_feedback(api_client)
        assert response.status_code == status.HTTP_200_OK
        assert response.data is None

    def test_get_feedback(self, api_client, feedback):
        """Get a specific feedback, expect 403 with anonymous user."""
        response = self.get_feedback(api_client, feedback.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_feedback(self, api_client, feedback_data):
        """Create feedback, expect 201 with un-authenticated user."""
        response = self.create_feedback(api_client, feedback_data)
        assert response.status_code == status.HTTP_201_CREATED


class TestFeedbackAPIAuthenticatedUserNoRole(FeedbackAPITestsBase):
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

    def test_list_feedback(self, api_client):
        """List feedback, expect 200 with authenticated user."""
        response = self.list_feedback(api_client)
        assert response.status_code == status.HTTP_200_OK

    def test_get_feedback(self, api_client, feedback):
        """Get a specific feedback, expect 200 with authenticated user."""
        response = self.get_feedback(api_client, feedback.id)
        assert response.status_code == status.HTTP_200_OK

    def test_create_feedback(self, api_client, feedback_data):
        """Create feedback, expect 201 with authenticated user."""
        response = self.create_feedback(api_client, feedback_data)
        assert response.status_code == status.HTTP_201_CREATED

class TestFeedbackAPIAdminUser(FeedbackAPITestsBase):
    """Test class to test API endpoints with an admin user."""

    @pytest.fixture
    def user(self, ofa_system_admin, stt):
        """Override the default user with ofa_system_admin for our tests."""
        ofa_system_admin.stt = stt
        ofa_system_admin.save()
        return ofa_system_admin

    @pytest.fixture
    def api_client(self, api_client, user):
        """Provide an API client that is logged in with a admin user."""
        api_client.login(username=user.username, password='test_password')
        return api_client

    def test_list_feedback(self, api_client):
        """List feedback, expect 200 with admin user."""
        response = self.list_feedback(api_client)
        assert response.status_code == status.HTTP_200_OK

    def test_get_feedback(self, api_client, feedback):
        """Get a specific feedback, expect 200 with admin user."""
        response = self.get_feedback(api_client, feedback.id)
        assert response.status_code == status.HTTP_200_OK

    def test_create_feedback(self, api_client, feedback_data):
        """Create feedback, expect 201 with admin user."""
        response = self.create_feedback(api_client, feedback_data)
        assert response.status_code == status.HTTP_201_CREATED
