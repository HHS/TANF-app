"""Test users management commands."""

import pytest

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from tdpservice.users.management.commands.reset_cypress_profile_editing_users import (
    get_profile_editing_usernames,
)
from tdpservice.users.models import ChangeRequestAuditLog, UserChangeRequest
from tdpservice.users.test.factories import UserFactory


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_reset_cypress_profile_editing_users_removes_profile_users_and_requests():
    """The reset deletes only profile-editing Cypress personas."""
    User = get_user_model()
    profile_user = UserFactory(username=get_profile_editing_usernames()[0])
    untouched_user = UserFactory(username="cypress-other-user@teamraft.com")
    change_request = UserChangeRequest.objects.create(
        user=profile_user,
        requested_by=profile_user,
        field_name="first_name",
        current_value="Data Analyst",
        requested_value="Changed",
    )
    ChangeRequestAuditLog.objects.create(
        change_request=change_request,
        action="created",
        performed_by=profile_user,
    )

    call_command("reset_cypress_profile_editing_users")

    assert not User.objects.filter(pk=profile_user.pk).exists()
    assert User.objects.filter(pk=untouched_user.pk).exists()
    assert not UserChangeRequest.objects.filter(pk=change_request.pk).exists()
    assert ChangeRequestAuditLog.objects.count() == 0


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_reset_cypress_profile_editing_users_requires_opt_in_outside_debug():
    """The command requires an explicit opt-in when DEBUG is false."""
    User = get_user_model()
    username = get_profile_editing_usernames()[0]
    UserFactory(username=username)

    with pytest.raises(CommandError):
        call_command("reset_cypress_profile_editing_users")

    call_command("reset_cypress_profile_editing_users", "--allow-non-debug")

    assert not User.objects.filter(username=username).exists()


def test_get_profile_editing_usernames_reads_usernames_from_fixture():
    """The command derives its reset scope from profile-editing fixtures."""
    usernames = get_profile_editing_usernames()

    assert "cypress-data-analyst-dana@teamraft.com" in usernames
    assert "cypress-fra-ofa-regional-staff-ryan@acf.hhs.gov" in usernames
