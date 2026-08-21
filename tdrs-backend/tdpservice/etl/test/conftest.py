"""Shared fixtures for ETL tests."""

from django.contrib.auth.models import Group

import pytest
from rest_framework.test import APIClient

from tdpservice.stts.models import STT, Region
from tdpservice.users.models import AccountApprovalStatusChoices
from tdpservice.users.test.factories import UserFactory


@pytest.fixture
def api_client():
    """Return an API client."""
    return APIClient()


@pytest.fixture
def user():
    """Return a generic user."""
    return UserFactory.create()


@pytest.fixture
def region():
    """Return a region."""
    region, _ = Region.objects.get_or_create(id=5)
    return region


@pytest.fixture
def stt(region):
    """Return an STT."""
    stt, _ = STT.objects.get_or_create(
        name="Wisconsin",
        region=region,
        stt_code="55",
    )
    stt.type = STT.EntityType.STATE
    stt.save(update_fields=["type"])
    return stt


@pytest.fixture
def ofa_system_admin():
    """Return an approved OFA System Admin user."""
    group, _ = Group.objects.get_or_create(name="OFA System Admin")
    user = UserFactory.create(groups=(group,))
    user.account_approval_status = AccountApprovalStatusChoices.APPROVED
    user.save()
    return user


@pytest.fixture
def digit_team():
    """Return an approved DIGIT Team user."""
    group, _ = Group.objects.get_or_create(name="DIGIT Team")
    user = UserFactory.create(groups=(group,))
    user.account_approval_status = AccountApprovalStatusChoices.APPROVED
    user.save()
    return user
