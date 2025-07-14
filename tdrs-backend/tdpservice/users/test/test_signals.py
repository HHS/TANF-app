"""Test signals."""
import pytest
from unittest.mock import Mock, patch, call
from tdpservice.users.test.factories import AdminUserFactory, UserFactory
from django.contrib.auth.models import Group
import logging


logger = logging.getLogger(__name__)

@patch("tdpservice.users.signals.email_system_owner_system_admin_role_change")
@pytest.mark.django_db
def test_user_group_changed_add_triggers_email_if_ofa_system_admin(mock: Mock):
    """Test user_group_changed signal.

    Signal sends an email to System Owner on adding the OFA System Admin group.
    """
    group_ofa_admin = Group.objects.get(name="OFA System Admin")
    group_data_analyst = Group.objects.get(name="Data Analyst")

    instance = UserFactory.create()

    # email should only be sent when OFA System Admin group is added
    instance.groups.add(group_data_analyst)
    assert not mock.called

    instance.groups.add(group_ofa_admin)
    mock.assert_has_calls([
        call(instance, "added"),
    ])

@patch("tdpservice.users.signals.email_system_owner_system_admin_role_change")
@pytest.mark.django_db
def test_user_group_changed_remove_triggers_email_if_ofa_system_admin(mock: Mock):
    """Test user_group_changed signal.

    Signal sends an email to System Owner on removing the OFA System Admin group.
    """
    group_ofa_admin = Group.objects.get(name="OFA System Admin")
    group_data_analyst = Group.objects.get(name="Data Analyst")

    instance = UserFactory.create()

    # email should only be sent when OFA System Admin group is removed
    instance.groups.add(group_data_analyst)
    instance.groups.remove(group_data_analyst)
    assert not mock.called

    instance.groups.add(group_ofa_admin)
    instance.groups.remove(group_ofa_admin)
    mock.assert_has_calls([
        call(instance, "removed"),
    ])

@patch("tdpservice.users.signals.email_system_owner_system_admin_role_change")
@pytest.mark.django_db
def test_user_group_changed_clear_triggers_email_if_ofa_system_admin(mock: Mock):
    """Test user_group_changed signal.

    Signal sends an email to System Owner on removing the OFA System Admin group.
    """
    group_ofa_admin = Group.objects.get(name="OFA System Admin")
    group_data_analyst = Group.objects.get(name="Data Analyst")

    instance = UserFactory.create()

    # email should only be sent when OFA System Admin group is removed
    instance.groups.add(group_data_analyst)
    instance.groups.clear()
    assert not mock.called

    instance.groups.add(group_ofa_admin)
    instance.groups.clear()
    mock.assert_has_calls([
        call(instance, "removed"),
    ])

@patch("tdpservice.users.signals.email_system_owner_system_admin_role_change")
@pytest.mark.django_db
def test_user_is_staff_superuser_changed_assigned_staff(mock: Mock):
    """Test user_is_staff_superuser_changed signal.

    Signal sends an email to System Owner on assigning is_staff to a user.
    """
    instance = UserFactory.create()
    instance.is_staff = True
    instance.save()

    mock.assert_has_calls([
        call(instance, "is_staff_assigned"),
    ])

@patch("tdpservice.users.signals.email_system_owner_system_admin_role_change")
@pytest.mark.django_db
def test_user_is_staff_superuser_changed_assigned_superuser(mock: Mock):
    """Test user_is_staff_superuser_changed signal.

    Signal sends an email to System Owner on assigning is_superuser to a user.
    """
    instance = UserFactory.create()
    instance.is_superuser = True
    instance.save()

    mock.assert_has_calls([
        call(instance, "is_superuser_assigned"),
    ])

@patch("tdpservice.users.signals.email_system_owner_system_admin_role_change")
@pytest.mark.django_db
def test_user_is_staff_superuser_changed_removed_staff(mock: Mock):
    """Test user_is_staff_superuser_changed signal.

    Signal sends an email to System Owner on removing is_staff from a user.
    """
    instance = UserFactory.create()
    instance.is_staff = True
    instance.save()

    instance.is_staff = False
    instance.save()

    mock.assert_has_calls([
        call(instance, "is_staff_removed"),
    ])

@patch("tdpservice.users.signals.email_system_owner_system_admin_role_change")
@pytest.mark.django_db
def test_user_is_staff_superuser_changed_removed_superuser(mock: Mock):
    """Test user_is_staff_superuser_changed signal.

    Signal sends an email to System Owner on removing is_superuser from a user.
    """
    instance = UserFactory.create()
    instance.is_superuser = True
    instance.save()

    instance.is_superuser = False
    instance.save()

    mock.assert_has_calls([
        call(instance, "is_superuser_removed"),
    ])

@patch("tdpservice.users.signals.email_system_owner_system_admin_role_change")
@pytest.mark.django_db
def test_user_is_staff_superuser_created(mock: Mock):
    """Test user_is_staff_superuser_created signal.

    Signal sends an email to System Owner on creating a user with System Admin permissions.
    """
    instance = AdminUserFactory.create()

    mock.assert_has_calls([
        call(instance, "is_staff_assigned"),
        call(instance, "is_superuser_assigned"),
    ])
