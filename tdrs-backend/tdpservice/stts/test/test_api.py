"""API STT Tests."""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from ...stts.models import STT, Region

User = get_user_model()


@pytest.mark.django_db
def test_stts_is_valid_endpoint(api_client, user):
    """Test an authorized user can successfully query the STT endpoint."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get(reverse("stts"))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_stts_blocks_unauthorized(api_client, user):
    """Test an unauthorized user cannot successfully query the STT endpoint."""
    response = api_client.get(reverse("stts"))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_stts_alpha_valid_endpoint(api_client, user):
    """Test an authorized user can successfully query the STT alphabetized endpoint."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get(reverse("stts-alpha"))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_stts_alpha_blocks_unauthorized(api_client, user):
    """Test an unauthorized user cannot successfully query the STT alpha endpoint."""
    response = api_client.get(reverse("stts-alpha"))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_stts_by_region_valid_endpoint(api_client, user):
    """Test an authorized user can successfully query the STT by region endpoint."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get(reverse("stts-by-region"))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_stts_by_region_blocks_unauthorized(api_client, user):
    """Test an unauthorized user cannot query the STT by region endpoint."""
    response = api_client.get(reverse("stts-by-region"))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_can_get_stts(api_client, user, stts):
    """Test endpoint returns a listing of states, tribes and territories."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get(reverse("stts"))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == STT.objects.count()

    state_name = response.data[0]["name"]
    assert STT.objects.filter(name=state_name).exists()


@pytest.mark.django_db
def test_can_get_alpha_stts(api_client, user, stts):
    """Test endpoint returns the alphabetized listing of STTs."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get(reverse("stts-alpha"))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == STT.objects.count()

    state_name = response.data[0]["name"]
    assert STT.objects.filter(name=state_name).exists()


@pytest.mark.django_db
def test_alpha_stts_is_sorted(api_client, user, stts):
    """Test alphabetized endpoint is alphabetized."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get(reverse("stts-alpha"))
    response_names = [datum["name"] for datum in response.data]
    database_names = STT.objects.values_list("name", flat=True).order_by("name")
    assert response_names == list(database_names)


@pytest.mark.django_db
def test_can_get_by_region_stts(api_client, user, stts):
    """Test endpoint returns the alphabetized listing of STTs."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get(reverse("stts-by-region"))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == Region.objects.count()

    # Data is where it is supposed exist and is valid data
    state_id = response.data[0]["stts"][0]["id"]
    assert STT.objects.filter(id=state_id).exists()

    state_name = response.data[0]["stts"][0]["name"]
    assert STT.objects.filter(name=state_name).exists()

    state_type = response.data[0]["stts"][0]["type"]
    assert STT.objects.filter(type=state_type).exists()

    state_code = response.data[0]["stts"][0]["code"]
    assert STT.objects.filter(code=state_code).exists()

    region_id = response.data[0]["id"]
    assert Region.objects.filter(id=region_id).exists()


@pytest.mark.django_db
def test_stts_and_stts_alpha_are_dissimilar(api_client, user, stts):
    """The default STTs endpoint is not sorted the same as the alpha."""
    api_client.login(username=user.username, password="test_password")
    alpha_response = api_client.get(reverse("stts-alpha"))
    default_response = api_client.get(reverse("stts"))
    assert not alpha_response.data == default_response.data
