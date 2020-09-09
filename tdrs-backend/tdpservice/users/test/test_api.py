"""API Tests."""
from django.contrib.auth import get_user_model
import pytest
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
def test_retrieve_user(api_client, user):
    """Test user retrieval."""
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
def test_create_user(api_client, user_data):
    """Test user creation."""
    response = api_client.post("/v1/users/", user_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(username=user_data["username"]).exists()


@pytest.mark.django_db
def test_set_profile_data(api_client, user):
    """Test profile data can be set."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.post(
        "/v1/users/set_profile/", {"first_name": "Joe", "last_name": "Bloggs"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"first_name": "Joe", "last_name": "Bloggs"}
    user.refresh_from_db()
    assert user.first_name == "Joe"
    assert user.last_name == "Bloggs"


@pytest.mark.django_db
def test_set_profile_data_last_name_apostrophe(api_client, user):
    """Test profile data can be set."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.post(
        "/v1/users/set_profile/", {"first_name": "Mike", "last_name": "O'Hare"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"first_name": "Mike", "last_name": "O'Hare"}
    user.refresh_from_db()
    assert user.first_name == "Mike"
    assert user.last_name == "O'Hare"


@pytest.mark.django_db
def test_set_profile_data_first_name_apostrophe(api_client, user):
    """Test profile data can be set."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.post(
        "/v1/users/set_profile/", {"first_name": "Pat'Jack", "last_name": "Smith"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"first_name": "Pat'Jack", "last_name": "Smith"}
    user.refresh_from_db()
    assert user.first_name == "Pat'Jack"
    assert user.last_name == "Smith"


@pytest.mark.django_db
def test_set_profile_data_empty_first_name(api_client, user):
    """Test profile data can be set."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.post(
        "/v1/users/set_profile/", {"first_name": "", "last_name": "Jones"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"first_name": "", "last_name": "Jones"}
    user.refresh_from_db()
    assert user.first_name == ""
    assert user.last_name == "Jones"


@pytest.mark.django_db
def test_set_profile_data_empty_last_name(api_client, user):
    """Test profile data can be set."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.post(
        "/v1/users/set_profile/", {"first_name": "John", "last_name": ""},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"first_name": "John", "last_name": ""}
    user.refresh_from_db()
    assert user.first_name == "John"
    assert user.last_name == ""


@pytest.mark.django_db
def test_set_profile_data_special_last_name(api_client, user):
    """Test profile data can be set."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.post(
        "/v1/users/set_profile/", {"first_name": "John", "last_name": "Smith-O'Hare"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"first_name": "John", "last_name": "Smith-O'Hare"}
    user.refresh_from_db()
    assert user.first_name == "John"
    assert user.last_name == "Smith-O'Hare"


@pytest.mark.django_db
def test_set_profile_data_special_first_name(api_client, user):
    """Test profile data can be set."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.post(
        "/v1/users/set_profile/", {"first_name": "John-Tom'", "last_name": "Jacobs"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"first_name": "John-Tom'", "last_name": "Jacobs"}
    user.refresh_from_db()
    assert user.first_name == "John-Tom'"
    assert user.last_name == "Jacobs"


@pytest.mark.django_db
def test_set_profile_data_spaced_last_name(api_client, user):
    """Test profile data can be set."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.post(
        "/v1/users/set_profile/", {"first_name": "Joan", "last_name": "Mary Ann"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"first_name": "Joan", "last_name": "Mary Ann"}
    user.refresh_from_db()
    assert user.first_name == "Joan"
    assert user.last_name == "Mary Ann"
