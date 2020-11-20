"""API User Tests."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
import pytest
from rest_framework import status
from ...stts.models import STT

User = get_user_model()


@pytest.mark.django_db
@pytest.fixture(scope="function")
def generate_groups():
    """Create groups and users under those groups."""
    call_command("generate_test_users")


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
    response = api_client.patch(
        "/v1/users/set_profile/",
        {"first_name": "Joe", "last_name": "Bloggs", "stt": {"id": stt.id}},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "email": user.username,
        "first_name": "Joe",
        "last_name": "Bloggs",
        "stt": {
            "id": stt.id,
            "type": stt.type,
            "code": stt.code,
            "name": stt.name,
        },
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
    response = api_client.patch(
        "/v1/users/set_profile/",
        {"first_name": "Mike", "last_name": "O'Hare", "stt": {"id": stt.id}},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "email": user.username,
        "first_name": "Mike",
        "last_name": "O'Hare",
        "stt": {
            "id": stt.id,
            "type": stt.type,
            "code": stt.code,
            "name": stt.name,
        },
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
    response = api_client.patch(
        "/v1/users/set_profile/",
        {
            "first_name": "Pat'Jack",
            "last_name": "Smith",
            "stt": {"id": stt.id},
        },
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "email": user.username,
        "first_name": "Pat'Jack",
        "last_name": "Smith",
        "stt": {
            "id": stt.id,
            "type": stt.type,
            "code": stt.code,
            "name": stt.name,
        },
    }
    user.refresh_from_db()
    assert user.first_name == "Pat'Jack"
    assert user.last_name == "Smith"
    assert user.stt.name == stt.name


@pytest.mark.django_db
def test_set_profile_data_empty_first_name(api_client, user):
    """Test profile data cannot be be set if first name is blank."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.patch(
        "/v1/users/set_profile/",
        {"first_name": "", "last_name": "Jones"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_set_profile_data_empty_last_name(api_client, user):
    """Test profile data cannot be set last name is blank."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.patch(
        "/v1/users/set_profile/",
        {"first_name": "John", "last_name": ""},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_set_profile_data_empty_first_name_and_last_name(api_client, user):
    """Test profile data cannot be set if first and last name are blank."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.patch(
        "/v1/users/set_profile/",
        {"first_name": "", "last_name": ""},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_set_profile_data_special_last_name(api_client, user):
    """Test profile data can be set if last name has multipe special characters."""
    api_client.login(username=user.username, password="test_password")
    stt = STT.objects.first()
    response = api_client.patch(
        "/v1/users/set_profile/",
        {
            "first_name": "John",
            "last_name": "Smith-O'Hare",
            "stt": {"id": stt.id},
        },
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "email": user.username,
        "first_name": "John",
        "last_name": "Smith-O'Hare",
        "stt": {
            "id": stt.id,
            "type": stt.type,
            "code": stt.code,
            "name": stt.name,
        },
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
    response = api_client.patch(
        "/v1/users/set_profile/",
        {
            "first_name": "John-Tom'",
            "last_name": "Jacobs",
            "stt": {"id": stt.id},
        },
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "email": user.username,
        "first_name": "John-Tom'",
        "last_name": "Jacobs",
        "stt": {
            "id": stt.id,
            "type": stt.type,
            "code": stt.code,
            "name": stt.name,
        },
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
    response = api_client.patch(
        "/v1/users/set_profile/",
        {
            "first_name": "Joan",
            "last_name": "Mary Ann",
            "stt": {"id": stt.id},
        },
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "email": user.username,
        "first_name": "Joan",
        "last_name": "Mary Ann",
        "stt": {
            "id": stt.id,
            "type": stt.type,
            "code": stt.code,
            "name": stt.name,
        },
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
    response = api_client.patch(
        "/v1/users/set_profile/",
        {
            "first_name": "John Jim",
            "last_name": "Smith",
            "stt": {"id": stt.id},
        },
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "email": user.username,
        "first_name": "John Jim",
        "last_name": "Smith",
        "stt": {
            "id": stt.id,
            "type": stt.type,
            "code": stt.code,
            "name": stt.name,
        },
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
    response = api_client.patch(
        "/v1/users/set_profile/",
        {
            "first_name": "Max",
            "last_name": "Grecheñ",
            "stt": {"id": stt.id},
        },
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "email": user.username,
        "first_name": "Max",
        "last_name": "Grecheñ",
        "stt": {
            "id": stt.id,
            "type": stt.type,
            "code": stt.code,
            "name": stt.name,
        },
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
    response = api_client.patch(
        "/v1/users/set_profile/",
        {
            "first_name": "Max",
            "last_name": "Glen~",
            "stt": {"id": stt.id},
        },
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "email": user.username,
        "first_name": "Max",
        "last_name": "Glen~",
        "stt": {
            "id": stt.id,
            "type": stt.type,
            "code": stt.code,
            "name": stt.name,
        },
    }
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
        response = api_client.patch(
            "/v1/users/set_profile/",
            {
                "first_name": "Heather",
                "last_name": "Class",
                "middle_initial": "Unknown",
                "stt": {"id": stt.id},
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        """Test to ensure response data does not include unknown field"""
        assert response.data == {
            "email": user.username,
            "first_name": "Heather",
            "last_name": "Class",
            "stt": {
                "id": stt.id,
                "type": stt.type,
                "code": stt.code,
                "name": stt.name,
            },
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
    response = api_client.patch(
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
    response = api_client.patch(
        "/v1/users/set_profile/",
        {
            "last_name": "Heather",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_role_list(api_client, generate_groups):
    """Test role list."""
    # Groups are populated in a data migrations, so are already available.
    api_client.login(username="test__ofa_admin", password="test_password")
    response = api_client.get("/v1/roles/")
    assert response.status_code == status.HTTP_200_OK
    role_names = {group["name"] for group in response.data}
    assert role_names == {"OFA Admin", "OFA Analyst", "Data Prepper"}


@pytest.mark.django_db
def test_role_list_unauthorized(api_client, generate_groups):
    """Data prepper does not have access."""
    # Groups are populated in a data migrations, so are already available.
    api_client.login(username="test__data_prepper", password="test_password")
    response = api_client.get("/v1/roles/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_role_create(api_client, generate_groups):
    """Test creating a role."""
    api_client.login(username="test__ofa_admin", password="test_password")
    response = api_client.post("/v1/roles/", {"name": "Test Role"})
    assert response.status_code == status.HTTP_201_CREATED
    assert Group.objects.filter(name="Test Role").exists()


@pytest.mark.django_db
def test_role_create_unauthorized(api_client, generate_groups):
    """Test data prepper does not have access."""
    api_client.login(username="test__data_prepper", password="test_password")
    response = api_client.post("/v1/roles/", {"name": "Test Role"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_role_create_with_permission(api_client, generate_groups):
    """Test creating a role with a permission."""
    permission = Permission.objects.first()
    api_client.login(username="test__ofa_admin", password="test_password")
    response = api_client.post(
        "/v1/roles/", {"name": "Test Role", "permissions": [permission.id]}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert Group.objects.filter(name="Test Role").exists()
    assert permission in Group.objects.get(name="Test Role").permissions.all()


@pytest.mark.django_db
def test_role_update(api_client, generate_groups):
    """Test role update."""
    group = Group.objects.get(name="OFA Admin")
    api_client.login(username="test__ofa_admin", password="test_password")
    response = api_client.patch(f"/v1/roles/{group.id}/", {"name": "staff"})
    assert response.status_code == status.HTTP_200_OK
    assert Group.objects.filter(name="staff").exists()
    assert not Group.objects.filter(name="admin").exists()


@pytest.mark.django_db
def test_role_update_unauthorized(api_client, generate_groups):
    """Test data prepper does not have access."""
    group = Group.objects.get(name="Data Prepper")
    api_client.login(username="test__data_prepper", password="test_password")
    response = api_client.patch(f"/v1/roles/{group.id}/", {"name": "staff"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_role_delete(api_client, generate_groups):
    """Test role deletion."""
    group = Group.objects.get(name="OFA Admin")
    api_client.login(username="test__ofa_admin", password="test_password")
    response = api_client.delete(f"/v1/roles/{group.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Group.objects.filter(name="admin").exists()


@pytest.mark.django_db
def test_role_delete_unauthorized(api_client, generate_groups):
    """Test data prepper does not have access."""
    group = Group.objects.get(name="Data Prepper")
    api_client.login(username="test__data_prepper", password="test_password")
    response = api_client.delete(f"/v1/roles/{group.id}/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_permission_list(api_client, generate_groups):
    """Test permission list."""
    # Django comes with some permissions, so we'll just test those.
    api_client.login(username="test__ofa_admin", password="test_password")
    response = api_client.get("/v1/permissions/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0  # Just check there's something here.


@pytest.mark.django_db
def test_permission_list_unauthorized(api_client, generate_groups):
    """Test data prepper does not have access."""
    # Django comes with some permissions, so we'll just test those.
    api_client.login(username="test__data_prepper", password="test_password")
    response = api_client.get("/v1/permissions/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_permission_create(api_client, generate_groups):
    """Test permission creation."""
    api_client.login(username="test__ofa_admin", password="test_password")
    response = api_client.post(
        "/v1/permissions/", {"codename": "foo", "name": "Foo", "content_type": None}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["codename"] == "foo"
    assert response.data["name"] == "Foo"
    assert Permission.objects.filter(codename="foo").exists()


@pytest.mark.django_db
def test_permission_create_unauthorized(api_client, generate_groups):
    """Test data prepper does not have access."""
    api_client.login(username="test__data_prepper", password="test_password")
    response = api_client.post(
        "/v1/permissions/", {"codename": "foo", "name": "Foo", "content_type": None}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_permission_create_with_content_type(api_client, generate_groups):
    """Test can create a permission with a content type."""
    content_type = ContentType.objects.get_for_model(User)
    api_client.login(username="test__ofa_admin", password="test_password")
    response = api_client.post(
        "/v1/permissions/",
        {
            "codename": "foo",
            "name": "Foo",
            "content_type": f"{content_type.app_label}.{content_type.model}",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["codename"] == "foo"
    assert response.data["name"] == "Foo"
    assert Permission.objects.filter(codename="foo").exists()


@pytest.mark.django_db
def test_permission_update(api_client, generate_groups):
    """Test permission update."""
    permission = Permission.objects.first()
    api_client.login(username="test__ofa_admin", password="test_password")
    response = api_client.patch(
        f"/v1/permissions/{permission.id}/", {"codename": "foo"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert not Permission.objects.filter(codename=permission.codename).exists()
    assert Permission.objects.filter(codename="foo").exists()


@pytest.mark.django_db
def test_permission_update_unauthorized(api_client, generate_groups):
    """Test data prepper does not have access."""
    permission = Permission.objects.first()
    api_client.login(username="test__data_prepper", password="test_password")
    response = api_client.patch(
        f"/v1/permissions/{permission.id}/", {"codename": "foo"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_permission_delete(api_client, generate_groups):
    """Test permission deletion."""
    permission = Permission.objects.first()
    api_client.login(username="test__ofa_admin", password="test_password")
    response = api_client.delete(f"/v1/permissions/{permission.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Permission.objects.filter(codename=permission.codename).exists()

@pytest.mark.django_db
def test_user_no_roles_list(api_client):
    """Test endpoint listing users with no roles."""
    api_client.login(username="test__admin", password="test_password")
    response = api_client.get('/v1/users/no_roles')
    groupless_users = User.objects.filter(groups=None).map(lambda u: u.id).sort()
    response_users = response.data.map(lambda u: u.id).sort()
    all(map(lambda groupless_id, response_id: groupless_id == response_id,
            groupless_users,
            response_users,))



@pytest.mark.django_db
def test_permission_delete_unauthorized(api_client, generate_groups):
    """Test data prepper does not have access."""
    permission = Permission.objects.first()
    api_client.login(username="test__data_prepper", password="test_password")
    response = api_client.delete(f"/v1/permissions/{permission.id}/")
    assert response.status_code == status.HTTP_403_FORBIDDEN
