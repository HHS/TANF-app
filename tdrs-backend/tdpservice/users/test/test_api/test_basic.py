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
