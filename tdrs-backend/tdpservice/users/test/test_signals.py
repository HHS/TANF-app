"""Test signals."""
import pytest
from unittest.mock import patch, call
from tdpservice.users.models import User
from tdpservice.users.test.factories import AdminUserFactory
from django.contrib.auth.models import Group
import logging
import django


logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_my_signal_receiver(mocker):
    """Test my_signal_receiver."""
    with patch("django.db.models.signals.m2m_changed.send") as mock_receiver:
        instance = AdminUserFactory.create()
        instance.groups.add(Group.objects.get(name="OFA System Admin"))

        mock_receiver.assert_called_with(
            sender=User.groups.through,
            instance=instance,
            action="post_add",
            pk_set={Group.objects.get(name="OFA System Admin").pk},
            reverse=False,
            using="default",
            model=django.contrib.auth.models.Group,
        )
        mock_receiver.call_count = 2  # pre_save and post_save

    with patch(
        "tdpservice.users.signals.email_system_owner_system_admin_role_change"
    ) as mock_email_system_owner_system_admin_role_change:
        instance = AdminUserFactory.create()
        instance.groups.add(Group.objects.get(name="OFA System Admin"))
        mock_email_system_owner_system_admin_role_change.assert_has_calls([
            call(instance, 'is_staff_assigned'),
            call(instance, 'is_superuser_assigned'),
            call(instance, "added")
        ])
