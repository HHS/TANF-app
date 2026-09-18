"""Basic Feedback API Endpoint Tests."""

from django.contrib.auth.models import AnonymousUser

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from tdpservice.users.models import AccountApprovalStatusChoices, Feedback, User
from tdpservice.users.test.factories import FeedbackFactory


@pytest.mark.usefixtures("db")
class FeedbackAPITestsBase:
    """A base test class for tests that interact with the FeedbackViewSet.

    Provides several fixtures and methods that are commonly used between tests.
    Intended to simplify creating tests for different user flows.
    """

    root_url = "/v1/feedback/"

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
        api_client.login(username=user.username, password="test_password")
        return api_client

    @pytest.fixture
    def feedback_data(self, user):
        """Provide an generic feedback data for users to change in different tests."""
        return {
            "rating": 3,
            "feedback": "",
            "anonymous": False,
            "page_url": "https://localhost/",
            "feedback_type": "general-feedback",
            "component": "general-feedback",
            "widget_id": "general-feedback",
            "attachments": [],
        }

    def list_feedback(self, api_client):
        """List feedback."""
        return api_client.get(self.root_url)

    def get_feedback(self, api_client, feedback_id):
        """Get a specific feedback."""
        return api_client.get(f"{self.root_url}{feedback_id}/")

    def create_feedback(self, api_client, feedback_data):
        """Post feadback."""
        return api_client.post(f"{self.root_url}", feedback_data)


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
        """List feedback, expect 403 with anonymous user."""
        response = self.list_feedback(api_client)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_feedback(self, api_client, feedback):
        """Get a specific feedback, expect 403 with anonymous user."""
        response = self.get_feedback(api_client, feedback.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize("anonymous", [False, True])
    def test_create_feedback(
        self, api_client: APIClient, feedback_data: dict, anonymous: bool
    ) -> None:
        """Reject unauthenticated submissions regardless of the anonymous flag."""
        feedback_data["anonymous"] = anonymous
        feedback_count = Feedback.objects.count()
        response = self.create_feedback(api_client, feedback_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Feedback.objects.count() == feedback_count

    @pytest.mark.parametrize("anonymous", [False, True])
    def test_update_feedback(
        self, api_client: APIClient, feedback: Feedback, anonymous: bool
    ) -> None:
        """Reject unauthenticated updates without changing stored feedback."""
        original_message = feedback.feedback
        response = api_client.patch(
            f"{self.root_url}{feedback.id}/",
            {"feedback": "Unauthorized update", "anonymous": anonymous},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        feedback.refresh_from_db()
        assert feedback.feedback == original_message


class TestFeedbackAPIAuthenticatedUserNoRole(FeedbackAPITestsBase):
    """Test class to test API endpoints with an authenticated user that has no group."""

    @pytest.fixture
    def user(self, user):
        """Override the default user with user with no group for our tests."""
        return user

    @pytest.fixture
    def api_client(self, api_client, user):
        """Provide an API client that is not logged in with a specified user."""
        api_client.login(username=user.username, password="test_password")
        return api_client

    def test_list_feedback(self, api_client):
        """Reject listing feedback without an approved role."""
        response = self.list_feedback(api_client)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_feedback(self, api_client, feedback):
        """Reject retrieving feedback without an approved role."""
        response = self.get_feedback(api_client, feedback.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_feedback(self, api_client, feedback_data):
        """Reject creating feedback without an approved role."""
        response = self.create_feedback(api_client, feedback_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestFeedbackAPIAdminUser(FeedbackAPITestsBase):
    """Test class to test API endpoints with an admin user."""

    @pytest.fixture
    def user(self, ofa_system_admin, stt):
        """Override the default user with ofa_system_admin for our tests."""
        ofa_system_admin.save()
        return ofa_system_admin

    @pytest.fixture
    def api_client(self, api_client, user):
        """Provide an API client that is logged in with a admin user."""
        api_client.login(username=user.username, password="test_password")
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


class TestFeedbackAPIApprovedUser(FeedbackAPITestsBase):
    """Approved users can submit and update identified or anonymous feedback."""

    @pytest.fixture(params=["data_analyst", "ofa_system_admin"])
    def user(self, request: pytest.FixtureRequest) -> User:
        """Use approved grantee and ACF staff accounts."""
        user = request.getfixturevalue(request.param)
        user.refresh_from_db()
        return user

    def test_list_feedback(self, api_client: APIClient) -> None:
        """Approved users can list feedback available to them."""
        assert self.list_feedback(api_client).status_code == status.HTTP_200_OK

    def test_get_feedback(self, api_client: APIClient, feedback: Feedback) -> None:
        """Approved users can retrieve their own feedback."""
        response = self.get_feedback(api_client, feedback.id)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize("anonymous", [False, True])
    def test_create_feedback(
        self, api_client: APIClient, user: User, feedback_data: dict, anonymous: bool
    ) -> None:
        """Only identified submissions retain the submitting user's association."""
        feedback_data["anonymous"] = anonymous
        response = self.create_feedback(api_client, feedback_data)

        assert response.status_code == status.HTTP_201_CREATED
        feedback = Feedback.objects.get(id=response.data["id"])
        assert feedback.anonymous is anonymous
        assert feedback.user == (None if anonymous else user)

    @pytest.mark.parametrize("initial_anonymous", [False, True])
    @pytest.mark.parametrize("anonymous", [False, True])
    def test_update_feedback(
        self,
        api_client: APIClient,
        user: User,
        feedback_data: dict,
        initial_anonymous: bool,
        anonymous: bool,
    ) -> None:
        """Rating saves can be completed, including changing anonymity."""
        feedback_data["anonymous"] = initial_anonymous
        created = self.create_feedback(api_client, feedback_data)
        assert created.status_code == status.HTTP_201_CREATED

        response = api_client.patch(
            f"{self.root_url}{created.data['id']}/",
            {"feedback": "My feedback", "anonymous": anonymous},
        )

        assert response.status_code == status.HTTP_200_OK
        feedback = Feedback.objects.get(id=created.data["id"])
        assert feedback.feedback == "My feedback"
        assert feedback.anonymous is anonymous
        assert feedback.user == (None if anonymous else user)


class TestFeedbackAPIIneligibleUser(FeedbackAPITestsBase):
    """Authentication alone does not grant access to feedback."""

    @pytest.fixture(
        params=[
            AccountApprovalStatusChoices.INITIAL,
            AccountApprovalStatusChoices.ACCESS_REQUEST,
            AccountApprovalStatusChoices.PENDING,
            AccountApprovalStatusChoices.DENIED,
            AccountApprovalStatusChoices.DEACTIVATED,
            "inactive",
            "no-role",
        ]
    )
    def user(self, data_analyst: User, request: pytest.FixtureRequest) -> User:
        """Use an account that is unapproved, inactive, or lacks a role."""
        if request.param == "inactive":
            data_analyst.is_active = False
        elif request.param == "no-role":
            data_analyst.groups.clear()
        else:
            data_analyst.account_approval_status = request.param
        data_analyst.save()
        data_analyst.refresh_from_db()
        return data_analyst

    @pytest.fixture
    def api_client(self, api_client: APIClient, user: User) -> APIClient:
        """Exercise permissions even if authentication accepted an inactive user."""
        api_client.force_authenticate(user=user)
        return api_client

    @pytest.mark.parametrize("anonymous", [False, True])
    def test_create_feedback(
        self, api_client: APIClient, feedback_data: dict, anonymous: bool
    ) -> None:
        """Reject new feedback, including attempts to submit anonymously."""
        feedback_data["anonymous"] = anonymous
        feedback_count = Feedback.objects.count()
        response = self.create_feedback(api_client, feedback_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Feedback.objects.count() == feedback_count

    @pytest.mark.parametrize("anonymous", [False, True])
    def test_update_feedback(
        self, api_client: APIClient, feedback: Feedback, anonymous: bool
    ) -> None:
        """Reject updates and preserve existing feedback."""
        original_message = feedback.feedback
        original_user = feedback.user
        response = api_client.patch(
            f"{self.root_url}{feedback.id}/",
            {"feedback": "Unauthorized update", "anonymous": anonymous},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        feedback.refresh_from_db()
        assert feedback.feedback == original_message
        assert feedback.user == original_user

    def test_list_feedback(self, api_client: APIClient) -> None:
        """Reject access to the feedback list."""
        assert self.list_feedback(api_client).status_code == status.HTTP_403_FORBIDDEN

    def test_get_feedback(self, api_client: APIClient, feedback: Feedback) -> None:
        """Reject access to stored feedback."""
        response = self.get_feedback(api_client, feedback.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN
