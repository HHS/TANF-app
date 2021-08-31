"""API User Role Tests."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
import pytest
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
@pytest.fixture(scope="function")
def create_test_users():
    """Create users for each group."""
    call_command("generate_test_users")


@pytest.mark.django_db
def test_role_list(api_client, create_test_users):
    """Test role list."""
    # Groups are populated in a data migrations, so are already available.
    api_client.login(username="test__ofa_admin", password="test_password")
    response = api_client.get("/v1/roles/")
    assert response.status_code == status.HTTP_200_OK
    role_names = {group["name"] for group in response.data}
    assert role_names == {"OFA Regional Staff", "OFA Admin", "Data Analyst", "OFA System Admin"}


@pytest.mark.django_db
def test_role_list_unauthorized(api_client, create_test_users):
    """Data Analyst does not have access."""
    # Groups are populated in a data migrations, so are already available.
    api_client.login(username="test__data_analyst", password="test_password")
    response = api_client.get("/v1/roles/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_role_create_forbidden(api_client, create_test_users):
    """Test creating a role is no longer allowed."""
    api_client.login(username="test__ofa_admin", password="test_password")
    response = api_client.post("/v1/roles/", {"name": "Test Role"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_role_create_unauthorized(api_client, create_test_users):
    """Test data analyst does not have access."""
    api_client.login(username="test__data_analyst", password="test_password")
    response = api_client.post("/v1/roles/", {"name": "Test Role"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_role_create_with_permission_forbidden(api_client, create_test_users):
    """Test creating a role with a permission is no longer allowed."""
    permission = Permission.objects.first()
    api_client.login(username="test__ofa_admin", password="test_password")
    response = api_client.post(
        "/v1/roles/", {"name": "Test Role", "permissions": [permission.id]}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_role_update_not_found(api_client, create_test_users):
    """Test role update no longer exists."""
    group = Group.objects.get(name="OFA Admin")
    api_client.login(username="test__ofa_admin", password="test_password")
    response = api_client.patch(f"/v1/roles/{group.id}/", {"name": "staff"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_role_delete_not_found(api_client, create_test_users):
    """Test role deletion no longer exists."""
    group = Group.objects.get(name="OFA Admin")
    api_client.login(username="test__ofa_admin", password="test_password")
    response = api_client.delete(f"/v1/roles/{group.id}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
