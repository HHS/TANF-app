"""Test the authorization check."""

import pytest
import requests
import logging
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

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
def test_auth_check_endpoint_with_bad_user(api_client):
    """If the user doesn't exist, auth_check should not authenticate."""
    api_client.login(username="nonexistent", password="test_password")
    response = api_client.get(reverse("authorization-check"))
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_auth_check_endpoint_with_unauthorized_email(api_client):
    """If the user has an email address not in the system it should not authenticate."""
    api_client.login(username="bademail@example.com", password="test_password")
    response = api_client.get(reverse("authorization-check"))
    assert response.status_code == status.HTTP_403_FORBIDDEN

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

@pytest.mark.django_db
def test_setting_http_only_cookie(httpbin):
    """Http only cookie is set."""
    key = 'some_cookie'
    value = 'some_value'
    secure = True
    domain = 'test.com'
    rest = {'HttpOnly': True}
    jar = requests.cookies.RequestsCookieJar()
    jar.set(key, value, secure=secure, domain=domain, rest=rest)
    assert len(jar) == 1
    assert 'some_cookie' in jar
    cookie = list(jar)[0]
    assert cookie.secure == secure
    assert cookie.domain == domain
    assert cookie._rest['HttpOnly'] == rest['HttpOnly']
