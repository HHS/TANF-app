"""System wide tests.

Fixtures are used to create a regular user
and an admin user. The regular user has is_staff and is_superuser
set to false, while the admin_user has both set to true.
"""

import pytest
from django.contrib import admin
from django.urls import reverse
from rest_framework import status
from django.utils.text import capfirst


@pytest.mark.django_db
def test_can_access_admin(client, admin_user):
    """Test an authenticated admin_user can access the admin console."""
    client.login(username=admin_user.username, password="test_password")
    url = reverse("admin:index")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_admin_displays_keys_for_admin(client, admin_user):
    """Test an authenticated admin_user sees the appropriate content."""
    client.login(username=admin_user.username, password="test_password")
    url = reverse("admin:index")
    response = client.get(url)
    assert admin.site.site_header in response.rendered_content
    for model in admin.site._registry.keys():
        assert (
            str(capfirst(model._meta.verbose_name_plural)) in response.rendered_content
        )


@pytest.mark.django_db
def test_admin_does_not_display_keys_for_staff(client, staff_user):
    """Test an authenticated staff_user sees the appropriate content."""
    client.login(username=staff_user.username, password="test_password")
    url = reverse("admin:index")
    response = client.get(url)
    assert admin.site.site_header in response.rendered_content
    for model in admin.site._registry.keys():
        assert (
            str(capfirst(model._meta.verbose_name_plural))
            not in response.rendered_content
        )


@pytest.mark.django_db
def test_staff_can_access_admin(client, staff_user):
    """Test an authenticated admin_user can access the admin console."""
    client.login(username=staff_user.username, password="test_password")
    url = reverse("admin:index")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_cant_access_admin(client, user):
    """Can't access admin.

    Test an authenticated user without admin access is
    redirected when attempting to access the admin console.
    """
    client.login(username=user.username, password="test_password")
    url = reverse("admin:index")
    response = client.get(url)
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_unauth_cant_access_admin(client):
    """Can't access admin.

    Test an unauthenticated user is redirected when attempting
    to access the admin console.
    """
    url = reverse("admin:index")
    response = client.get(url)
    assert response.status_code == status.HTTP_302_FOUND
