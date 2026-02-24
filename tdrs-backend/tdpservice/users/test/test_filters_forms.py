"""Tests for user admin filters and forms."""

from urllib.parse import urlencode

import pytest
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import RequestFactory

from tdpservice.users.constants import REGIONAL_ROLES
from tdpservice.users.filters import ActiveStatusListFilter
from tdpservice.users.forms import UserForm
from tdpservice.users.models import AccountApprovalStatusChoices, User
from tdpservice.users.test.factories import UserFactory


class DummyChangeList:
    """Simple changelist stub for filter choice rendering."""

    def get_query_string(self, params):
        """Return a query string with provided parameters."""
        return f"?{urlencode(params)}"


def build_filter(value=None):
    """Create an ActiveStatusListFilter with optional value."""
    params = {}
    if value is not None:
        params["active_status"] = value
    request = RequestFactory().get("/admin/users/user/", params)
    model_admin = admin.ModelAdmin(User, AdminSite())
    return ActiveStatusListFilter(request, request.GET.copy(), User, model_admin)


def get_group(name):
    """Return a group with the given name, creating it when needed."""
    group, _ = Group.objects.get_or_create(name=name)
    return group


@pytest.mark.django_db
def test_active_status_filter_lookups_and_default_value():
    """Ensure lookups are defined and value defaults to active users."""
    status_filter = build_filter()

    assert status_filter.lookups(None, None) == (
        ("active_users", "Show Active Users"),
        ("all_users", "Show All Users"),
        ("inactive_users", "Show Inactive Users"),
    )
    assert status_filter.value() == "active_users"


@pytest.mark.django_db
def test_active_status_filter_queryset_variants():
    """Filter users based on activation status options."""
    inactive_user = UserFactory.create(
        account_approval_status=AccountApprovalStatusChoices.DEACTIVATED
    )
    active_user = UserFactory.create(
        account_approval_status=AccountApprovalStatusChoices.APPROVED
    )
    other_user = UserFactory.create(
        account_approval_status=AccountApprovalStatusChoices.INITIAL
    )
    scoped_ids = [inactive_user.id, active_user.id, other_user.id]
    queryset = User.objects.filter(id__in=scoped_ids)

    def ids_for(qs):
        return {str(pk) for pk in qs.values_list("id", flat=True)}

    inactive_filter = build_filter("inactive_users")
    inactive_ids = ids_for(inactive_filter.queryset(None, queryset))
    assert inactive_ids == {str(inactive_user.id)}

    active_filter = build_filter("active_users")
    active_ids = ids_for(active_filter.queryset(None, queryset))
    assert active_ids == {str(active_user.id), str(other_user.id)}

    all_filter = build_filter("all_users")
    all_ids = ids_for(all_filter.queryset(None, queryset))
    assert all_ids == {
        str(inactive_user.id),
        str(active_user.id),
        str(other_user.id),
    }

    unknown_filter = build_filter("unknown")
    unknown_ids = ids_for(unknown_filter.queryset(None, queryset))
    assert unknown_ids == {
        str(inactive_user.id),
        str(active_user.id),
        str(other_user.id),
    }


@pytest.mark.django_db
def test_active_status_filter_choices_excludes_all_option():
    """Render filter choices without an implicit All option."""
    status_filter = build_filter("active_users")

    choices = list(status_filter.choices(DummyChangeList()))

    assert [choice["display"] for choice in choices] == [
        "Show Active Users",
        "Show All Users",
        "Show Inactive Users",
    ]


@pytest.mark.django_db
def test_user_form_clean_rejects_multiple_groups():
    """Disallow assigning more than one group in clean."""
    form = UserForm()
    form.cleaned_data = {
        "groups": [get_group("OFA Admin"), get_group("Data Analyst")],
        "regions": [],
        "stt": None,
    }

    with pytest.raises(ValidationError) as excinfo:
        form.clean()

    assert excinfo.value.messages == ["User should not have multiple groups."]


@pytest.mark.django_db
def test_user_form_clean_requires_location_for_regional_roles():
    """Regional role users must have a region or stt."""
    regional_group = get_group(next(iter(REGIONAL_ROLES)))
    form = UserForm()
    form.cleaned_data = {"groups": [regional_group], "regions": [], "stt": None}

    with pytest.raises(ValidationError) as excinfo:
        form.clean()

    assert excinfo.value.messages == [
        "Users in regional roles must have at least one region or location assigned."
    ]


@pytest.mark.django_db
def test_user_form_clean_rejects_region_and_stt(region, stt):
    """Disallow assigning both region and stt."""
    regional_group = get_group(next(iter(REGIONAL_ROLES)))
    form = UserForm()
    form.cleaned_data = {"groups": [regional_group], "regions": [region], "stt": stt}

    with pytest.raises(ValidationError) as excinfo:
        form.clean()

    assert excinfo.value.messages == [
        "A user may only have a Region or STT assigned, not both."
    ]


@pytest.mark.django_db
def test_user_form_clean_rejects_regions_for_non_regional_roles(region):
    """Non-regional users should not have regions."""
    form = UserForm()
    form.cleaned_data = {
        "groups": [get_group("OFA Admin")],
        "regions": [region],
        "stt": None,
    }

    with pytest.raises(ValidationError) as excinfo:
        form.clean()

    assert excinfo.value.messages == [
        "Users without regional roles should not be assigned regions."
    ]


@pytest.mark.django_db
def test_user_form_clean_accepts_valid_assignments(region, stt):
    """Allow valid regional or non-regional assignments."""
    regional_group = get_group(next(iter(REGIONAL_ROLES)))
    non_regional_group = get_group("OFA Admin")

    regional_form = UserForm()
    regional_form.cleaned_data = {
        "groups": [regional_group],
        "regions": [region],
        "stt": None,
    }
    assert regional_form.clean() == regional_form.cleaned_data

    non_regional_form = UserForm()
    non_regional_form.cleaned_data = {
        "groups": [non_regional_group],
        "regions": [],
        "stt": stt,
    }
    assert non_regional_form.clean() == non_regional_form.cleaned_data


@pytest.mark.django_db
def test_user_form_clean_groups():
    """Validate group selection in clean_groups."""
    form = UserForm()
    form.cleaned_data = {"groups": [get_group("OFA Admin")]}
    assert form.clean_groups() == form.cleaned_data["groups"]

    form.cleaned_data = {"groups": [get_group("OFA Admin"), get_group("Developer")]}
    with pytest.raises(ValidationError) as excinfo:
        form.clean_groups()
    assert excinfo.value.messages == ["User should not have multiple groups"]


@pytest.mark.django_db
def test_user_form_clean_feature_flags_defaults_to_dict():
    """Normalize feature flags to an empty dict when missing."""
    form = UserForm()
    form.cleaned_data = {}
    assert form.clean_feature_flags() == {}

    form.cleaned_data = {"feature_flags": {"flag": True}}
    assert form.clean_feature_flags() == {"flag": True}
