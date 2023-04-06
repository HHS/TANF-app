"""API User Set Profile Tests."""
from django.core.management import call_command

import pytest
from rest_framework import status


@pytest.mark.django_db
@pytest.fixture(scope="function")
def create_test_users():
    """Create users for each group."""
    call_command("generate_test_users")


@pytest.mark.django_db
def test_set_profile_data(api_client, user):
    """Test profile data can be set."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.patch(
        "/v1/users/set_profile/",
        {"first_name": "Joe", "last_name": "Bloggs"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "id": user.id,
        "first_name": "Joe",
        "last_name": "Bloggs",
        "email": user.username,
        "stt": None,
        "region": None,
        "login_gov_uuid": user.login_gov_uuid,
        "hhs_id": user.hhs_id,
        "roles": [],
        "groups": [],
        "is_superuser": False,
        "is_staff": False,
        "last_login": user.last_login,
        "date_joined": user.date_joined,
        "access_request": False,
        "account_approval_status": "Initial"
    }
    user.refresh_from_db()
    assert user.first_name == "Joe"
    assert user.last_name == "Bloggs"


@pytest.mark.django_db
def test_cannot_set_account_approval_status_through_api(api_client, user):
    """Test that the `account_approval_status` field cannot be updated through an api call to `set_profile`."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.patch(
        "/v1/users/set_profile/",
        {
            "first_name": "Mike",  # required field
            "last_name": "O'Hare",  # required field
            "account_approval_status": "Approved"
        },
        impformat="json"
    )
    assert response.data['account_approval_status'] == "Initial"  # value doesn't update
    assert response.status_code == status.HTTP_200_OK  # even though the request succeeds

@pytest.mark.django_db
def test_set_profile_data_last_name_apostrophe(api_client, user):
    """Test profile data last name  can be set with an apostrophe."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.patch(
        "/v1/users/set_profile/",
        {"first_name": "Mike", "last_name": "O'Hare"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "id": user.id,
        "first_name": "Mike",
        "last_name": "O'Hare",
        "email": user.username,
        "stt": None,
        "region": None,
        "login_gov_uuid": user.login_gov_uuid,
        "hhs_id": user.hhs_id,
        "roles": [],
        "groups": [],
        "is_superuser": False,
        "is_staff": False,
        "last_login": user.last_login,
        "date_joined": user.date_joined,
        "access_request": False,
        "account_approval_status": "Initial"
    }
    user.refresh_from_db()
    assert user.first_name == "Mike"
    assert user.last_name == "O'Hare"


@pytest.mark.django_db
def test_set_profile_data_first_name_apostrophe(api_client, user):
    """Test profile data first name can be set with an apostrophe."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.patch(
        "/v1/users/set_profile/",
        {"first_name": "Pat'Jack", "last_name": "Smith"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "id": user.id,
        "first_name": "Pat'Jack",
        "last_name": "Smith",
        "email": user.username,
        "login_gov_uuid": user.login_gov_uuid,
        "hhs_id": user.hhs_id,
        "roles": [],
        "groups": [],
        "is_superuser": False,
        "is_staff": False,
        "last_login": user.last_login,
        "date_joined": user.date_joined,
        "access_request": False,
        "account_approval_status": "Initial"
    }
    user.refresh_from_db()
    assert user.first_name == "Pat'Jack"
    assert user.last_name == "Smith"


@pytest.mark.django_db
def test_set_profile_data_empty_first_name(api_client, user):
    """Test profile data cannot be be set if first name is blank."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.patch(
        "/v1/users/set_profile/", {"first_name": "", "last_name": "Jones"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_set_profile_data_empty_last_name(api_client, user):
    """Test profile data cannot be set last name is blank."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.patch(
        "/v1/users/set_profile/", {"first_name": "John", "last_name": ""},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_set_profile_data_empty_first_name_and_last_name(api_client, user):
    """Test profile data cannot be set if first and last name are blank."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.patch(
        "/v1/users/set_profile/", {"first_name": "", "last_name": ""},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_set_profile_data_special_last_name(api_client, user):
    """Test profile data can be set if last name has multipe special characters."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.patch(
        "/v1/users/set_profile/",
        {"first_name": "John", "last_name": "Smith-O'Hare"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "id": user.id,
        "first_name": "John",
        "last_name": "Smith-O'Hare",
        "email": user.username,
        "stt": None,
        "region": None,
        "login_gov_uuid": user.login_gov_uuid,
        "hhs_id": user.hhs_id,
        "roles": [],
        "groups": [],
        "is_superuser": False,
        "is_staff": False,
        "last_login": user.last_login,
        "date_joined": user.date_joined,
        "access_request": False,
        "account_approval_status": "Initial"
    }
    user.refresh_from_db()
    assert user.first_name == "John"
    assert user.last_name == "Smith-O'Hare"


@pytest.mark.django_db
def test_set_profile_data_special_first_name(api_client, user):
    """Test profile data can be set if first name has multiple special characters."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.patch(
        "/v1/users/set_profile/",
        {"first_name": "John-Tom'", "last_name": "Jacobs"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "id": user.id,
        "first_name": "John-Tom'",
        "last_name": "Jacobs",
        "email": user.username,
        "stt": None,
        "region": None,
        "login_gov_uuid": user.login_gov_uuid,
        "hhs_id": user.hhs_id,
        "roles": [],
        "groups": [],
        "is_superuser": False,
        "is_staff": False,
        "last_login": user.last_login,
        "date_joined": user.date_joined,
        "access_request": False,
        "account_approval_status": "Initial"
    }
    user.refresh_from_db()
    assert user.first_name == "John-Tom'"
    assert user.last_name == "Jacobs"


@pytest.mark.django_db
def test_set_profile_data_spaced_last_name(api_client, user):
    """Test profile data can be set if last name has a space."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.patch(
        "/v1/users/set_profile/",
        {"first_name": "Joan", "last_name": "Mary Ann"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "id": user.id,
        "first_name": "Joan",
        "last_name": "Mary Ann",
        "email": user.username,
        "stt": None,
        "region": None,
        "login_gov_uuid": user.login_gov_uuid,
        "hhs_id": user.hhs_id,
        "roles": [],
        "groups": [],
        "is_superuser": False,
        "is_staff": False,
        "last_login": user.last_login,
        "date_joined": user.date_joined,
        "access_request": False,
        "account_approval_status": "Initial"
    }
    user.refresh_from_db()
    assert user.first_name == "Joan"
    assert user.last_name == "Mary Ann"


@pytest.mark.django_db
def test_set_profile_data_spaced_first_name(api_client, user):
    """Test profile data can be set if first name has a space."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.patch(
        "/v1/users/set_profile/",
        {"first_name": "John Jim", "last_name": "Smith"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "id": user.id,
        "first_name": "John Jim",
        "last_name": "Smith",
        "email": user.username,
        "stt": None,
        "region": None,
        "login_gov_uuid": user.login_gov_uuid,
        "hhs_id": user.hhs_id,
        "roles": [],
        "groups": [],
        "is_superuser": False,
        "is_staff": False,
        "last_login": user.last_login,
        "date_joined": user.date_joined,
        "access_request": False,
        "account_approval_status": "Initial"
    }
    user.refresh_from_db()
    assert user.first_name == "John Jim"
    assert user.last_name == "Smith"


@pytest.mark.django_db
def test_set_profile_data_last_name_with_tilde_over_char(api_client, user):
    """Test profile data can be set if last name includes a tilde character."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.patch(
        "/v1/users/set_profile/",
        {"first_name": "Max", "last_name": "Grecheñ"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "id": user.id,
        "first_name": "Max",
        "last_name": "Grecheñ",
        "email": user.username,
        "stt": None,
        "region": None,
        "login_gov_uuid": user.login_gov_uuid,
        "hhs_id": user.hhs_id,
        "roles": [],
        "groups": [],
        "is_superuser": False,
        "is_staff": False,
        "last_login": user.last_login,
        "date_joined": user.date_joined,
        "access_request": False,
        "account_approval_status": "Initial"
    }
    user.refresh_from_db()
    assert user.first_name == "Max"
    assert user.last_name == "Grecheñ"


@pytest.mark.django_db
def test_set_profile_data_last_name_with_tilde(api_client, user):
    """Test profile data can be set if last name includes alternate tilde character."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.patch(
        "/v1/users/set_profile/",
        {"first_name": "Max", "last_name": "Glen~"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "id": user.id,
        "first_name": "Max",
        "last_name": "Glen~",
        "email": user.username,
        "stt": None,
        "region": None,
        "login_gov_uuid": user.login_gov_uuid,
        "hhs_id": user.hhs_id,
        "roles": [],
        "groups": [],
        "is_superuser": False,
        "is_staff": False,
        "last_login": user.last_login,
        "date_joined": user.date_joined,
        "access_request": False,
        "account_approval_status": "Initial"
    }

    user.refresh_from_db()
    assert user.first_name == "Max"
    assert user.last_name == "Glen~"


@pytest.mark.django_db
def test_set_profile_data_extra_field_include_required(api_client, user):
    """Test profile data will ignore any extra fields passed in via request body."""
    with pytest.raises(AttributeError):
        """This test will fail if it does not trigger an AttributeError exception"""
        api_client.login(username=user.username, password="test_password")
        response = api_client.patch(
            "/v1/users/set_profile/",
            {
                "first_name": "Heather",
                "last_name": "Class",
                "middle_initial": "Unknown",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        """Test to ensure response data does not include unknown field"""
        assert response.data == {
            "id": user.id,
            "first_name": "Heather",
            "last_name": "Class",
            "email": user.username,
            "stt": None,
            "region": None,
            "login_gov_uuid": user.login_gov_uuid,
            "hhs_id": user.hhs_id,
            "roles": [],
            "groups": [],
            "is_superuser": False,
            "is_staff": False,
            "last_login": user.last_login,
            "date_joined": user.date_joined,
            "access_request": False,
            "account_approval_status": "Initial"
        }
        user.refresh_from_db()
        assert user.first_name == "Heather"
        assert user.last_name == "Class"
        """Test fails if AttributeError exception isn"t thrown"""
        assert user.middle_name == "Unknown"


@pytest.mark.django_db
def test_set_profile_data_missing_last_name_field(api_client, user):
    """Test profile data cannot be set if last name field is missing."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.patch("/v1/users/set_profile/", {"first_name": "Heather", },)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_set_profile_data_missing_first_name_field(api_client, user):
    """Test profile data cannot be set if first name field is missing."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.patch("/v1/users/set_profile/", {"last_name": "Heather", },)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
