"""API User Tests."""
from django.contrib.auth import get_user_model
import pytest
from rest_framework import status
from ...stts.models import STT

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
    stt = STT.objects.first()
    response = api_client.post(
        "/v1/users/set_profile/",
        {"first_name": "Joe", "last_name": "Bloggs", "stt": stt.id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "first_name": "Joe",
        "last_name": "Bloggs",
        "stt": stt.name,
    }
    user.refresh_from_db()
    assert user.first_name == "Joe"
    assert user.last_name == "Bloggs"
    assert user.stt.name == stt.name


@pytest.mark.django_db
def test_set_profile_data_last_name_apostrophe(api_client, user):
    """Test profile data last name  can be set with an apostrophe."""
    api_client.login(username=user.username, password="test_password")
    stt = STT.objects.first()
    response = api_client.post(
        "/v1/users/set_profile/",
        {"first_name": "Mike", "last_name": "O'Hare", "stt": stt.id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "first_name": "Mike",
        "last_name": "O'Hare",
        "stt": stt.name,
    }
    user.refresh_from_db()
    assert user.first_name == "Mike"
    assert user.last_name == "O'Hare"
    assert user.stt.name == stt.name


@pytest.mark.django_db
def test_set_profile_data_first_name_apostrophe(api_client, user):
    """Test profile data first name can be set with an apostrophe."""
    api_client.login(username=user.username, password="test_password")
    stt = STT.objects.first()
    response = api_client.post(
        "/v1/users/set_profile/",
        {"first_name": "Pat'Jack", "last_name": "Smith", "stt": stt.id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "first_name": "Pat'Jack",
        "last_name": "Smith",
        "stt": stt.name,
    }
    user.refresh_from_db()
    assert user.first_name == "Pat'Jack"
    assert user.last_name == "Smith"
    assert user.stt.name == stt.name


@pytest.mark.django_db
def test_set_profile_data_empty_first_name(api_client, user):
    """Test profile data cannot be be set if first name is blank."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.post(
        "/v1/users/set_profile/",
        {"first_name": "", "last_name": "Jones"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_set_profile_data_empty_last_name(api_client, user):
    """Test profile data cannot be set last name is blank."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.post(
        "/v1/users/set_profile/",
        {"first_name": "John", "last_name": ""},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_set_profile_data_empty_first_name_and_last_name(api_client, user):
    """Test profile data cannot be set if first and last name are blank."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.post(
        "/v1/users/set_profile/",
        {"first_name": "", "last_name": ""},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_set_profile_data_special_last_name(api_client, user):
    """Test profile data can be set if last name has multipe special characters."""
    api_client.login(username=user.username, password="test_password")
    stt = STT.objects.first()
    response = api_client.post(
        "/v1/users/set_profile/",
        {"first_name": "John", "last_name": "Smith-O'Hare", "stt": stt.id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "first_name": "John",
        "last_name": "Smith-O'Hare",
        "stt": stt.name,
    }
    user.refresh_from_db()
    assert user.first_name == "John"
    assert user.last_name == "Smith-O'Hare"
    assert user.stt.name == stt.name


@pytest.mark.django_db
def test_set_profile_data_special_first_name(api_client, user):
    """Test profile data can be set if first name has multiple special characters."""
    api_client.login(username=user.username, password="test_password")
    stt = STT.objects.first()
    response = api_client.post(
        "/v1/users/set_profile/",
        {"first_name": "John-Tom'", "last_name": "Jacobs", "stt": stt.id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "first_name": "John-Tom'",
        "last_name": "Jacobs",
        "stt": stt.name,
    }
    user.refresh_from_db()
    assert user.first_name == "John-Tom'"
    assert user.last_name == "Jacobs"
    assert user.stt.name == stt.name


@pytest.mark.django_db
def test_set_profile_data_spaced_last_name(api_client, user):
    """Test profile data can be set if last name has a space."""
    stt = STT.objects.first()
    api_client.login(username=user.username, password="test_password")
    response = api_client.post(
        "/v1/users/set_profile/",
        {"first_name": "Joan", "last_name": "Mary Ann", "stt": stt.id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "first_name": "Joan",
        "last_name": "Mary Ann",
        "stt": stt.name,
    }
    user.refresh_from_db()
    assert user.first_name == "Joan"
    assert user.last_name == "Mary Ann"
    assert user.stt.name == stt.name


@pytest.mark.django_db
def test_set_profile_data_spaced_first_name(api_client, user):
    """Test profile data can be set if first name has a space."""
    api_client.login(username=user.username, password="test_password")
    stt = STT.objects.first()
    response = api_client.post(
        "/v1/users/set_profile/",
        {"first_name": "John Jim", "last_name": "Smith", "stt": stt.id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "first_name": "John Jim",
        "last_name": "Smith",
        "stt": stt.name,
    }
    user.refresh_from_db()
    assert user.first_name == "John Jim"
    assert user.last_name == "Smith"
    assert user.stt.name == stt.name


@pytest.mark.django_db
def test_set_profile_data_last_name_with_tilde_over_char(api_client, user):
    """Test profile data can be set if last name includes a tilde character."""
    api_client.login(username=user.username, password="test_password")
    stt = STT.objects.first()
    response = api_client.post(
        "/v1/users/set_profile/",
        {"first_name": "Max", "last_name": "Grecheñ", "stt": stt.id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "first_name": "Max",
        "last_name": "Grecheñ",
        "stt": stt.name,
    }
    user.refresh_from_db()
    assert user.first_name == "Max"
    assert user.last_name == "Grecheñ"
    assert user.stt.name == stt.name


@pytest.mark.django_db
def test_set_profile_data_last_name_with_tilde(api_client, user):
    """Test profile data can be set if last name includes alternate tilde character."""
    api_client.login(username=user.username, password="test_password")
    stt = STT.objects.first()
    response = api_client.post(
        "/v1/users/set_profile/",
        {"first_name": "Max", "last_name": "Glen~", "stt": stt.id},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"first_name": "Max", "last_name": "Glen~", "stt": stt.name}
    user.refresh_from_db()
    assert user.first_name == "Max"
    assert user.last_name == "Glen~"
    assert user.stt.name == stt.name


@pytest.mark.django_db
def test_set_profile_data_extra_field_include_required(api_client, user):
    """Test profile data will ignore any extra fields passed in via request body."""
    with pytest.raises(AttributeError):
        """This test will fail if it does not trigger an AttributeError exception"""
        api_client.login(username=user.username, password="test_password")
        stt = STT.objects.first()
        response = api_client.post(
            "/v1/users/set_profile/",
            {
                "first_name": "Heather",
                "last_name": "Class",
                "middle_initial": "Unknown",
                "stt": stt.id,
            },
        )
        assert response.status_code == status.HTTP_200_OK
        """Test to ensure response data does not include unknown field"""
        assert response.data == {
            "first_name": "Heather",
            "last_name": "Class",
            "stt": stt.name,
        }
        user.refresh_from_db()
        assert user.first_name == "Heather"
        assert user.last_name == "Class"
        assert user.stt.name == stt.name
        """Test fails if AttributeError exception isn't thrown"""
        assert user.middle_name == "Unknown"


@pytest.mark.django_db
def test_set_profile_data_missing_last_name_field(api_client, user):
    """Test profile data cannot be set if last name field is missing."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.post(
        "/v1/users/set_profile/",
        {
            "first_name": "Heather",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_set_profile_data_missing_first_name_field(api_client, user):
    """Test profile data cannot be set if first name field is missing."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.post(
        "/v1/users/set_profile/",
        {
            "last_name": "Heather",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
