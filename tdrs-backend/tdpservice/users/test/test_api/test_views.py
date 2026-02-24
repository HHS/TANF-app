"""Additional viewset tests for users app coverage."""

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.test import APIRequestFactory

from tdpservice.users.models import (
    AccountApprovalStatusChoices,
    ChangeRequestAuditLog,
    Feedback,
    User,
    UserChangeRequest,
)
from tdpservice.users.test.factories import FeedbackFactory
from tdpservice.users.views import (
    ChangeRequestAuditLogViewSet,
    CypressAdminUserViewSet,
    FeedbackViewSet,
    UserChangeRequestViewSet,
)


@pytest.fixture
def feedback_payload():
    """Return baseline feedback payload."""
    return {
        "rating": 3,
        "feedback": "Test feedback",
        "anonymous": False,
        "page_url": "https://localhost/",
        "feedback_type": "general-feedback",
        "component": "general-feedback",
        "widget_id": "general-feedback",
        "attachments": [],
    }


@pytest.mark.django_db
def test_request_access_get_returns_405(api_client, data_analyst):
    """Reject GET request for request_access action."""
    api_client.login(username=data_analyst.username, password="test_password")

    response = api_client.get("/v1/users/request_access/")

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_request_access_sets_stt_and_permission(api_client, data_analyst):
    """Persist access request updates and FRA permission."""
    content_type = ContentType.objects.get_for_model(User)
    Permission.objects.get_or_create(
        codename="has_fra_access",
        content_type=content_type,
        defaults={"name": "Has FRA Access"},
    )

    api_client.login(username=data_analyst.username, password="test_password")
    stt_id = data_analyst.stt_id

    payload = {
        "first_name": "Test",
        "last_name": "User",
        "stt": data_analyst.stt.id,
        "has_fra_access": True,
    }

    response = api_client.patch("/v1/users/request_access/", payload, format="json")

    assert response.status_code == status.HTTP_200_OK

    data_analyst.refresh_from_db()
    assert (
        data_analyst.account_approval_status
        == AccountApprovalStatusChoices.ACCESS_REQUEST
    )
    assert data_analyst.access_requested_date is not None
    assert data_analyst.stt_id == stt_id
    assert data_analyst.user_permissions.filter(codename="has_fra_access").exists()


@pytest.mark.django_db
def test_request_access_missing_permission_returns_400(
    api_client, data_analyst, monkeypatch
):
    """Return 400 when FRA permission is missing."""
    api_client.login(username=data_analyst.username, password="test_password")

    def raise_does_not_exist(*args, **kwargs):
        raise Permission.DoesNotExist()

    monkeypatch.setattr(Permission.objects, "get", raise_does_not_exist)

    payload = {
        "first_name": "Test",
        "last_name": "User",
        "stt": data_analyst.stt.id,
        "has_fra_access": True,
    }
    response = api_client.patch("/v1/users/request_access/", payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "has_fra_access permission does not exist." in str(response.data)


@pytest.mark.django_db
def test_update_profile_direct_update_admin(api_client, ofa_system_admin):
    """Allow direct profile update for system admins."""
    api_client.login(username=ofa_system_admin.username, password="test_password")

    payload = {
        "first_name": "Direct",
        "last_name": "Update",
        "create_change_requests": False,
    }

    response = api_client.patch("/v1/users/update_profile/", payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["first_name"] == "Direct"
    assert response.data["last_name"] == "Update"


@pytest.mark.django_db
def test_update_profile_direct_update_non_admin_denied(api_client, data_analyst):
    """Reject direct profile updates from non-admin users."""
    api_client.login(username=data_analyst.username, password="test_password")

    payload = {
        "first_name": "Direct",
        "last_name": "Update",
        "stt": data_analyst.stt.id,
        "create_change_requests": False,
    }

    response = api_client.patch("/v1/users/update_profile/", payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Only administrators can update user profiles directly." in str(response.data)


@pytest.mark.django_db
def test_user_change_request_queryset_filters_by_user(
    data_analyst, user, ofa_system_admin
):
    """Return only owner change requests for non-admin users."""
    user_request = UserChangeRequest.objects.create(
        user=user,
        requested_by=user,
        field_name="first_name",
        current_value="A",
        requested_value="B",
    )
    analyst_request = UserChangeRequest.objects.create(
        user=data_analyst,
        requested_by=data_analyst,
        field_name="last_name",
        current_value="C",
        requested_value="D",
    )

    factory = APIRequestFactory()
    view = UserChangeRequestViewSet()

    request = factory.get("/v1/change-requests/")
    request.user = data_analyst
    view.request = request
    assert set(view.get_queryset()) == {analyst_request}

    request.user = ofa_system_admin
    view.request = request
    assert set(view.get_queryset()) == {user_request, analyst_request}


@pytest.mark.django_db
def test_change_request_audit_log_queryset_filters_by_admin(
    data_analyst, ofa_system_admin
):
    """Restrict audit logs to OFA system admins."""
    change_request = UserChangeRequest.objects.create(
        user=data_analyst,
        requested_by=data_analyst,
        field_name="first_name",
        current_value="A",
        requested_value="B",
    )
    log = ChangeRequestAuditLog.objects.create(
        change_request=change_request,
        action="created",
        performed_by=data_analyst,
        details={"field": "first_name"},
    )

    factory = APIRequestFactory()
    view = ChangeRequestAuditLogViewSet()

    request = factory.get("/v1/change-request-logs/")
    request.user = data_analyst
    view.request = request
    assert list(view.get_queryset()) == []

    request.user = ofa_system_admin
    view.request = request
    assert set(view.get_queryset()) == {log}


@pytest.mark.django_db
def test_feedback_create_anonymous_sets_anonymous(api_client, feedback_payload):
    """Force anonymous feedback when user is not authenticated."""
    response = api_client.post("/v1/feedback/", feedback_payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    feedback = Feedback.objects.get(id=response.data["id"])
    assert feedback.anonymous is True
    assert feedback.user is None


@pytest.mark.django_db
def test_feedback_create_authenticated_sets_user(
    api_client, data_analyst, feedback_payload
):
    """Attach user to feedback when not anonymous."""
    api_client.login(username=data_analyst.username, password="test_password")

    response = api_client.post("/v1/feedback/", feedback_payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    feedback = Feedback.objects.get(id=response.data["id"])
    assert feedback.anonymous is False
    assert str(feedback.user_id) == str(data_analyst.id)


@pytest.mark.django_db
def test_feedback_create_invalid_returns_400(api_client, feedback_payload):
    """Return validation errors for invalid feedback payloads."""
    feedback_payload.pop("rating")

    response = api_client.post("/v1/feedback/", feedback_payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_feedback_update_sets_user_to_none_when_anonymous(
    api_client, data_analyst
):
    """Clear feedback user when marked anonymous."""
    feedback = FeedbackFactory.create(user=data_analyst, anonymous=False)
    api_client.login(username=data_analyst.username, password="test_password")

    response = api_client.patch(
        f"/v1/feedback/{feedback.id}/", {"anonymous": True}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK

    feedback.refresh_from_db()
    assert feedback.anonymous is True
    assert feedback.user is None


@pytest.mark.django_db
def test_feedback_update_sets_user_when_not_anonymous(
    api_client, data_analyst
):
    """Set feedback user when marked not anonymous."""
    feedback = FeedbackFactory.create(user=None, anonymous=True)
    api_client.login(username=data_analyst.username, password="test_password")

    response = api_client.patch(
        f"/v1/feedback/{feedback.id}/", {"anonymous": False}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK

    feedback.refresh_from_db()
    assert feedback.anonymous is False
    assert str(feedback.user_id) == str(data_analyst.id)


@pytest.mark.django_db
def test_feedback_update_invalid_returns_400(api_client, data_analyst):
    """Return validation errors for invalid feedback updates."""
    feedback = FeedbackFactory.create(user=data_analyst, anonymous=False)
    api_client.login(username=data_analyst.username, password="test_password")

    response = api_client.patch(
        f"/v1/feedback/{feedback.id}/", {"rating": "bad"}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_feedback_destroy_is_not_allowed(data_analyst):
    """Disallow feedback deletion."""
    feedback = FeedbackFactory.create(user=data_analyst)
    view = FeedbackViewSet()
    request = APIRequestFactory().delete(f"/v1/feedback/{feedback.id}/")
    request.user = data_analyst

    response = view.destroy(request, pk=feedback.id)

    assert isinstance(response, MethodNotAllowed)


@pytest.mark.django_db
def test_cypress_admin_user_viewset_set_status_updates(user):
    """Update user approval status with Cypress viewset helpers."""
    view = CypressAdminUserViewSet()

    response = view.set_pending(None, user.id)
    user.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert user.account_approval_status == AccountApprovalStatusChoices.PENDING

    response = view.set_initial(None, user.id)
    user.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert user.account_approval_status == AccountApprovalStatusChoices.INITIAL

    response = view.set_approved(None, user.id)
    user.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert user.account_approval_status == AccountApprovalStatusChoices.APPROVED
