"""API User Permission Tests."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
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
def test_permission_list_not_found(api_client, create_test_users):
    """Test permission list no longer exists."""
    # Django comes with some permissions, so we'll just test those.
    api_client.login(username="test__ofa_admin", password="test_password")
    response = api_client.get("/v1/permissions/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# @pytest.mark.django_db
# def test_permission_list_unauthorized(api_client, create_test_users):
#     """Test data prepper does not have access."""
#     # Django comes with some permissions, so we'll just test those.
#     api_client.login(username="test__data_prepper", password="test_password")
#     response = api_client.get("/v1/permissions/")
#     assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_permission_create_not_found(api_client, create_test_users):
    """Test permission creation no longer exists."""
    api_client.login(username="test__ofa_admin", password="test_password")
    response = api_client.post(
        "/v1/permissions/", {"codename": "foo", "name": "Foo", "content_type": None}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


# @pytest.mark.django_db
# def test_permission_create_unauthorized(api_client, create_test_users):
#     """Test data prepper does not have access."""
#     api_client.login(username="test__data_prepper", password="test_password")
#     response = api_client.post(
#         "/v1/permissions/", {"codename": "foo", "name": "Foo", "content_type": None}
#     )
#     assert response.status_code == status.HTTP_403_FORBIDDEN


# @pytest.mark.django_db
# def test_permission_create_with_content_type(api_client, create_test_users):
#     """Test can create a permission with a content type."""
#     content_type = ContentType.objects.get_for_model(User)
#     api_client.login(username="test__ofa_admin", password="test_password")
#     response = api_client.post(
#         "/v1/permissions/",
#         {
#             "codename": "foo",
#             "name": "Foo",
#             "content_type": f"{content_type.app_label}.{content_type.model}",
#         },
#     )
#     assert response.status_code == status.HTTP_201_CREATED
#     assert response.data["codename"] == "foo"
#     assert response.data["name"] == "Foo"
#     assert Permission.objects.filter(codename="foo").exists()


@pytest.mark.django_db
def test_permission_update_not_found(api_client, create_test_users):
    """Test permission update."""
    permission = Permission.objects.first()
    api_client.login(username="test__ofa_admin", password="test_password")
    response = api_client.patch(
        f"/v1/permissions/{permission.id}/", {"codename": "foo"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


# @pytest.mark.django_db
# def test_permission_update_unauthorized(api_client, create_test_users):
#     """Test data prepper does not have access."""
#     permission = Permission.objects.first()
#     api_client.login(username="test__data_prepper", password="test_password")
#     response = api_client.patch(
#         f"/v1/permissions/{permission.id}/", {"codename": "foo"}
#     )
#     assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_permission_delete_not_found(api_client, create_test_users):
    """Test permission deletion no longer exists."""
    permission = Permission.objects.first()
    api_client.login(username="test__ofa_admin", password="test_password")
    response = api_client.delete(f"/v1/permissions/{permission.id}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# @pytest.mark.django_db
# def test_permission_delete_unauthorized(api_client, create_test_users):
#     """Test data prepper does not have access."""
#     permission = Permission.objects.first()
#     api_client.login(username="test__data_prepper", password="test_password")
#     response = api_client.delete(f"/v1/permissions/{permission.id}/")
#     assert response.status_code == status.HTTP_403_FORBIDDEN
