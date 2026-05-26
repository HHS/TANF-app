"""Tests for Keycloak sync client and signal handlers."""

import logging
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import Group
from django.test import override_settings

import pytest

from tdpservice.users.keycloak_client import DJANGO_TO_KC_GROUP, KeycloakSyncClient
from tdpservice.users.models import User
from tdpservice.users.test.factories import UserFactory

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the KeycloakSyncClient singleton between tests."""
    KeycloakSyncClient.reset_instance()
    yield
    KeycloakSyncClient.reset_instance()


@pytest.fixture
def mock_keycloak_admin():
    """Provide a mocked KeycloakAdmin instance."""
    with patch(
        "tdpservice.users.keycloak_client.KeycloakOpenIDConnection"
    ) as mock_conn_cls, patch(
        "tdpservice.users.keycloak_client.KeycloakAdmin"
    ) as mock_admin_cls:
        mock_admin = MagicMock()
        mock_admin_cls.return_value = mock_admin
        mock_conn_cls.return_value = MagicMock()
        yield mock_admin


# --- KeycloakSyncClient unit tests ---


@override_settings(KEYCLOAK_SYNC_ENABLED=False)
@pytest.mark.django_db
def test_sync_user_updates_attributes(mock_keycloak_admin):
    """Test sync_user sends correct attributes to Keycloak."""
    user = UserFactory.create(account_approval_status="Approved")

    mock_keycloak_admin.get_users.return_value = [
        {"id": "kc-user-123", "email": user.email}
    ]
    mock_keycloak_admin.update_user.return_value = None

    client = KeycloakSyncClient.get_instance()
    result = client.sync_user(user)

    assert result is True
    mock_keycloak_admin.get_users.assert_called_once_with(
        query={"email": user.email, "exact": True}
    )
    mock_keycloak_admin.update_user.assert_called_once()

    call_args = mock_keycloak_admin.update_user.call_args
    assert call_args.kwargs["user_id"] == "kc-user-123"
    attrs = call_args.kwargs["payload"]["attributes"]
    assert attrs["login_gov_uuid"] == str(user.login_gov_uuid)
    assert attrs["hhs_id"] == user.hhs_id
    assert attrs["account_approval_status"] == "Approved"


@override_settings(KEYCLOAK_SYNC_ENABLED=False)
@pytest.mark.django_db
def test_sync_user_returns_false_when_not_found(mock_keycloak_admin):
    """Test sync_user returns False when user not found in Keycloak."""
    user = UserFactory.create()
    mock_keycloak_admin.get_users.return_value = []

    client = KeycloakSyncClient.get_instance()
    result = client.sync_user(user)

    assert result is False
    mock_keycloak_admin.update_user.assert_not_called()


@override_settings(KEYCLOAK_SYNC_ENABLED=False)
@pytest.mark.django_db
def test_sync_user_groups_sets_correct_groups(mock_keycloak_admin):
    """Test sync_user_groups removes old groups and adds correct ones."""
    group_analyst = Group.objects.get(name="Data Analyst")
    user = UserFactory.create()
    user.groups.add(group_analyst)

    mock_keycloak_admin.get_users.return_value = [
        {"id": "kc-user-456", "email": user.email}
    ]
    mock_keycloak_admin.get_groups.return_value = [
        {"id": "kc-grp-1", "name": "data-analyst"},
        {"id": "kc-grp-2", "name": "ofa-admin"},
        {"id": "kc-grp-3", "name": "developer"},
    ]
    mock_keycloak_admin.get_user_groups.return_value = [
        {"id": "kc-grp-2", "name": "ofa-admin"},
    ]

    client = KeycloakSyncClient.get_instance()
    result = client.sync_user_groups(user)

    assert result is True
    # Should remove old group
    mock_keycloak_admin.group_user_remove.assert_called_once_with(
        user_id="kc-user-456", group_id="kc-grp-2"
    )
    # Should add correct group
    mock_keycloak_admin.group_user_add.assert_called_once_with(
        user_id="kc-user-456", group_id="kc-grp-1"
    )


@override_settings(KEYCLOAK_SYNC_ENABLED=False)
@pytest.mark.django_db
def test_sync_user_groups_returns_false_when_not_found(mock_keycloak_admin):
    """Test sync_user_groups returns False when user not found in Keycloak."""
    user = UserFactory.create()
    mock_keycloak_admin.get_users.return_value = []

    client = KeycloakSyncClient.get_instance()
    result = client.sync_user_groups(user)

    assert result is False


@override_settings(KEYCLOAK_SYNC_ENABLED=False)
@pytest.mark.django_db
def test_bulk_sync_all_users(mock_keycloak_admin):
    """Test bulk_sync_all_users iterates active users and returns stats."""
    # Deactivate any pre-existing users so only our test users are picked up
    User.objects.filter(is_active=True).update(is_active=False)

    user1 = UserFactory.create(is_active=True, account_approval_status="Approved")
    UserFactory.create(is_active=True, account_approval_status="Approved")

    # user1 found in KC, user2 not found
    def get_users_side_effect(query):
        if query["email"] == user1.email:
            return [{"id": "kc-1", "email": user1.email}]
        return []

    mock_keycloak_admin.get_users.side_effect = get_users_side_effect
    mock_keycloak_admin.get_groups.return_value = []
    mock_keycloak_admin.get_user_groups.return_value = []
    mock_keycloak_admin.update_user.return_value = None

    client = KeycloakSyncClient.get_instance()
    stats = client.bulk_sync_all_users()

    assert stats["synced"] == 1
    assert stats["skipped"] == 1
    assert stats["failed"] == 0


def test_django_to_kc_group_mapping_complete():
    """Verify all expected Django groups have Keycloak mappings."""
    expected_django_groups = [
        "OFA Admin",
        "OFA System Admin",
        "Data Analyst",
        "OFA Regional Staff",
        "Developer",
        "ACF OCIO",
        "DIGIT Team",
    ]
    for group in expected_django_groups:
        assert group in DJANGO_TO_KC_GROUP, f"Missing mapping for {group}"


# --- Signal handler tests ---


@override_settings(KEYCLOAK_SYNC_ENABLED=True)
@patch("tdpservice.users.keycloak_sync._get_client")
@pytest.mark.django_db
def test_post_save_signal_calls_sync_user(mock_get_client):
    """Test that saving a user triggers sync_user when enabled."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    user = UserFactory.create()
    user.first_name = "Updated"
    user.save()

    mock_client.sync_user.assert_called()


@override_settings(KEYCLOAK_SYNC_ENABLED=False)
@patch("tdpservice.users.keycloak_sync._get_client")
@pytest.mark.django_db
def test_post_save_signal_noop_when_disabled(mock_get_client):
    """Test that saving a user does NOT trigger sync when disabled."""
    user = UserFactory.create()
    user.first_name = "Updated"
    user.save()

    mock_get_client.assert_not_called()


@override_settings(KEYCLOAK_SYNC_ENABLED=True)
@patch("tdpservice.users.keycloak_sync._get_client")
@pytest.mark.django_db
def test_m2m_changed_signal_calls_sync_groups(mock_get_client):
    """Test that changing user groups triggers sync_user_groups when enabled."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    group = Group.objects.get(name="Data Analyst")
    user = UserFactory.create()
    user.groups.add(group)

    mock_client.sync_user_groups.assert_called()


@override_settings(KEYCLOAK_SYNC_ENABLED=False)
@patch("tdpservice.users.keycloak_sync._get_client")
@pytest.mark.django_db
def test_m2m_changed_signal_noop_when_disabled(mock_get_client):
    """Test that changing user groups does NOT trigger sync when disabled."""
    group = Group.objects.get(name="Data Analyst")
    user = UserFactory.create()
    user.groups.add(group)

    mock_get_client.assert_not_called()


@override_settings(KEYCLOAK_SYNC_ENABLED=True)
@patch("tdpservice.users.keycloak_sync._get_client")
@pytest.mark.django_db
def test_signal_handles_client_exception_gracefully(mock_get_client):
    """Test that signal handler catches exceptions without crashing."""
    mock_client = MagicMock()
    mock_client.sync_user.side_effect = Exception("Connection refused")
    mock_get_client.return_value = mock_client

    # Should not raise
    user = UserFactory.create()
    user.first_name = "Updated"
    user.save()


# --- Celery task test ---


@patch("tdpservice.users.keycloak_client.KeycloakSyncClient")
def test_reconcile_keycloak_users_task(mock_client_cls):
    """Test that the Celery task calls bulk_sync_all_users."""
    from tdpservice.users.tasks import reconcile_keycloak_users

    mock_instance = MagicMock()
    mock_instance.bulk_sync_all_users.return_value = {
        "synced": 5,
        "skipped": 2,
        "failed": 0,
    }
    mock_client_cls.get_instance.return_value = mock_instance

    result = reconcile_keycloak_users()

    mock_instance.bulk_sync_all_users.assert_called_once()
    assert result == {"synced": 5, "skipped": 2, "failed": 0}
