"""API STT Tests."""
import pytest
import logging
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from ...stts.models import STT, Region

User = get_user_model()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


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
    """Test an unauthorized user cannot successfully query the STT alphaendpoint."""
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
    logger.info(len(response.data))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == STT.objects.count()

    state_name = response.data[0]["name"]
    assert STT.objects.filter(name=state_name).exists()


@pytest.mark.django_db
def test_can_get_alpha_stts(api_client, user, stts):
    """Test endpoint returns the alphabetized listing of STTs."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get(reverse("stts-alpha"))
    logger.info(len(response.data))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == STT.objects.count()

    state_name = response.data[0]["name"]
    assert STT.objects.filter(name=state_name).exists()


@pytest.mark.django_db
def test_can_get_by_region_stts(api_client, user, stts):
    """Test endpoint returns the alphabetized listing of STTs."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get(reverse("stts-by-region"))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == Region.objects.count()

    state_name = response.data[0]["stts"][0]["name"]
    assert STT.objects.filter(name=state_name).exists()

    region_id = response.data[0]["id"]
    assert Region.objects.filter(id=region_id).exists()
