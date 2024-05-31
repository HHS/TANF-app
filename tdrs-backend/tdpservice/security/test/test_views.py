"""Tests for the views in the security app."""

import pytest
import logging
from rest_framework.authtoken.models import Token
from tdpservice.users.models import User, AccountApprovalStatusChoices
from tdpservice.security.views import token_is_valid
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import Group

client = Client()

logger = logging.getLogger(__name__)


@pytest.fixture
def token():
    """Return a DRF token."""
    user = User.objects.create(username="testuser")
    token = Token.objects.create(user=user)
    return token


@pytest.mark.django_db
def test_token_is_valid(token):
    """Test token_is_valid function."""
    logger.info(token.__dict__)
    assert token_is_valid(token) is True
    token.created = token.created.replace(year=2000)
    # token.save()
    assert token_is_valid(token) is False


@pytest.mark.django_db
def test_generate_new_token(client):
    """Test generate_new_token function."""
    url = reverse("get-new-token")
    # assert if user is not authenticated
    response = client.get(url)
    assert response.status_code == 302

    # assert if user is not ofa_sys_admin
    user = User.objects.create_user(username="testuser", password="testpassword")
    user.save()
    client.login(username="testuser", password="testpassword")
    response = client.get(url)
    assert response.status_code == 302

    # assert if user is not approved
    user.account_approval_status = AccountApprovalStatusChoices.PENDING
    user.groups.add(Group.objects.get(name="OFA System Admin"))
    user.save()
    client.login(username="testuser", password="testpassword")
    response = client.get(url)
    assert response.status_code == 302

    # assert if token is valid
    user.account_approval_status = AccountApprovalStatusChoices.APPROVED
    user.save()

    client.login(username="testuser", password="testpassword")
    url = reverse("get-new-token")
    response = client.get(url)
    assert response.status_code == 200
    assert response.data == str(Token.objects.get(user=user))
