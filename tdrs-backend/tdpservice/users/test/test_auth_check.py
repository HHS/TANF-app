"""Test the authorization check."""

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_auth_check_endpoint_with_no_user(api_client, user):
    """If there is no user auth_check should return FORBIDDEN."""
    response = api_client.get(reverse("authorization-check"))
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_auth_check_endpoint_with_authenticated_user(api_client, user):
    """If user is authenticated auth_check should response status OK."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get(reverse("authorization-check"))
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_auth_check_returns_authenticated(api_client, user):
    """If user is authenticated auth_check should return authenticated true."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get(reverse("authorization-check"))
    assert user.is_authenticated is True
    assert response.data["authenticated"] is True

@pytest.mark.django_db
def test_auth_check_returns_user_email(api_client, user):
    """If user is authenticated auth_check should return user data."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get(reverse("authorization-check"))
    assert response.data["user"]["email"] == user.username
