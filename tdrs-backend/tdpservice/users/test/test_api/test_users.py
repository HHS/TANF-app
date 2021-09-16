"""Basic API User Tests."""
from django.contrib.auth import get_user_model
import pytest
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
def test_retrieve_user(api_client, user):
    """Test user retrieval."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get(f"/v1/users/{user.pk}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["username"] == user.username


@pytest.mark.django_db
def test_retrieve_user_as_ofa_admin(api_client, ofa_admin, user):
    """Test OFA Admin can retrieve a User."""
    api_client.login(username=ofa_admin.username, password="test_password")
    response = api_client.get(f"/v1/users/{user.pk}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["username"] == user.username


@pytest.mark.django_db
def test_can_update_own_user(api_client, user):
    """Test a user can update their own user."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.patch(f"/v1/users/{user.pk}/", {"first_name": "Jane"})
    assert response.status_code == status.HTTP_200_OK
    assert response.data["first_name"] == "Jane"
    assert User.objects.filter(first_name="Jane").exists()


@pytest.mark.django_db
def test_cannot_update_user_anonymously(api_client, user):
    """Test an unauthenticated user cannot update a user."""
    response = api_client.patch(f"/v1/users/{user.pk}/", {"first_name": "Jane"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_user_endpoint_not_present(api_client, user_data):
    """Test removed endpoint is no longer there."""
    response = api_client.post("/v1/users/", user_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_regional_user_update_user_in_region(api_client, regional_user, user_in_region):
    """Test regional staff can update users in their region."""
    assert regional_user.region.id == user_in_region.region.id
    assert regional_user.stt.region.id == user_in_region.stt.region.id
    api_client.login(username=regional_user.username, password="test_password")
    response = api_client.patch(f"/v1/users/{user_in_region.pk}/", {
        "first_name": "Jane"
    })
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_regional_user_cannot_update_user_not_in_region(
        api_client,
        regional_user,
        user_in_other_region
):
    """Test regional staff cannot update users not in their region."""
    assert regional_user.region.id != user_in_other_region.region.id
    assert regional_user.stt.region.id != user_in_other_region.stt.region.id
    api_client.login(username=regional_user.username, password="test_password")
    response = api_client.patch(f"/v1/users/{user_in_other_region.pk}/", {
        "first_name": "Jane"
    })
    assert response.status_code == status.HTTP_403_FORBIDDEN
