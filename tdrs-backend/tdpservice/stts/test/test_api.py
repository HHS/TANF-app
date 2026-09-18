"""API STT Tests."""

from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.test import TestCase, override_settings
from django.urls import reverse

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from tdpservice.conftest import UserFactory
from tdpservice.stts.models import STT, Region
from tdpservice.stts.views import STTApiAlphaView

User = get_user_model()


def _participations_by_slug(response_stt):
    return {
        participation["program"]["slug"]: participation
        for participation in response_stt["program_participations"]
    }


@pytest.mark.django_db
def test_stts_is_valid_endpoint(api_client, stt_user):
    """Test an authorized user can successfully query the STT endpoint."""
    api_client.login(username=stt_user.username, password="test_password")
    response = api_client.get(reverse("stts"))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_stts_blocks_unauthorized(api_client, stt_user):
    """Test an unauthorized user cannot successfully query the STT endpoint."""
    response = api_client.get(reverse("stts"))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_stts_alpha_valid_endpoint(api_client, stt_user):
    """Test an authorized user can successfully query the STT alphabetized endpoint."""
    api_client.login(username=stt_user.username, password="test_password")
    response = api_client.get(reverse("stts-alpha"))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_stts_alpha_blocks_unauthorized(api_client, stt_user):
    """Test an unauthorized user cannot successfully query the STT alpha endpoint."""
    response = api_client.get(reverse("stts-alpha"))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_stts_by_region_valid_endpoint(api_client, stt_user):
    """Test an authorized user can successfully query the STT by region endpoint."""
    api_client.login(username=stt_user.username, password="test_password")
    response = api_client.get(reverse("stts-by-region"))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_stts_by_region_blocks_unauthorized(api_client, stt_user):
    """Test an unauthorized user cannot query the STT by region endpoint."""
    response = api_client.get(reverse("stts-by-region"))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_can_get_stts(api_client, stt_user, stts):
    """Test endpoint returns a listing of states, tribes and territories."""
    stt = STT.objects.get(name="California")

    api_client.login(username=stt_user.username, password="test_password")
    response = api_client.get(reverse("stts"))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == STT.objects.count()

    state_name = response.data[0]["name"]
    assert STT.objects.filter(name=state_name).exists()

    response_stt = next(datum for datum in response.data if datum["id"] == stt.id)
    assert "ssp" in response_stt
    participations = _participations_by_slug(response_stt)
    assert set(participations) == {"tanf", "ssp"}
    for participation in participations.values():
        assert participation["status"] == "ACTIVE"
        assert {section["name"] for section in participation["sections"]} == {
            "Active Case Data",
            "Closed Case Data",
            "Aggregate Data",
            "Stratum Data",
        }
        assert all(
            section["program"]["slug"] == participation["program"]["slug"]
            for section in participation["sections"]
        )

    tribe = STT.objects.get(name="Santo Domingo Pueblo")
    response_tribe = next(datum for datum in response.data if datum["id"] == tribe.id)
    tribal_participation = _participations_by_slug(response_tribe)["tribal"]
    assert tribal_participation["status"] == "ACTIVE"
    assert {section["name"] for section in tribal_participation["sections"]} == {
        "Active Case Data",
        "Closed Case Data",
        "Aggregate Data",
    }


@pytest.mark.django_db
def test_can_get_by_region_stts(api_client, stt_user, stts):
    """Test endpoint returns the alphabetized listing of STTs."""
    stt = STT.objects.filter(type=STT.EntityType.STATE).first()

    api_client.login(username=stt_user.username, password="test_password")
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

    state_code = response.data[0]["stts"][0]["postal_code"]
    assert STT.objects.filter(postal_code=state_code).exists()

    region_id = response.data[0]["id"]
    assert Region.objects.filter(id=region_id).exists()

    response_stts = [
        response_stt
        for region in response.data
        for response_stt in region["stts"]
        if response_stt["id"] == stt.id
    ]
    assert response_stts[0]["program_participations"][0]["status"] == "ACTIVE"


@pytest.mark.django_db
@override_settings(
    CACHES={
        "stts": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-test-cache-location",  # Unique location to avoid conflicts
            "KEY_PREFIX": "test",
        },
    }
)
def test_stts_and_stts_alpha_are_dissimilar(api_client, stt_user, stts):
    """The default STTs endpoint is not sorted the same as the alpha."""
    api_client.login(username=stt_user.username, password="test_password")
    alpha_response = api_client.get(reverse("stts-alpha"))
    default_response = api_client.get(reverse("stts"))
    assert not alpha_response.data == default_response.data


@pytest.mark.django_db
@override_settings(
    CACHES={
        "stts": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-test-cache-location",  # Unique location to avoid conflicts
            "KEY_PREFIX": "test",
        },
    }
)
def test_can_get_alpha_stts(api_client, stt_user, stts):
    """Test endpoint returns the alphabetized listing of STTs."""
    stt = STT.objects.filter(type=STT.EntityType.STATE).first()
    caches["stts"].clear()

    api_client.login(username=stt_user.username, password="test_password")
    response = api_client.get(reverse("stts-alpha"))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == STT.objects.count()

    state_name = response.data[0]["name"]
    assert STT.objects.filter(name=state_name).exists()

    response_stt = next(datum for datum in response.data if datum["id"] == stt.id)
    assert response_stt["program_participations"][0]["status"] == "ACTIVE"


@pytest.mark.django_db
@override_settings(
    CACHES={
        "stts": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-test-cache-location",  # Unique location to avoid conflicts
            "KEY_PREFIX": "test",
        },
    }
)
def test_alpha_stts_is_sorted(api_client, stt_user, stts):
    """Test alphabetized endpoint is alphabetized."""
    api_client.login(username=stt_user.username, password="test_password")
    response = api_client.get(reverse("stts-alpha"))
    response_names = [datum["name"] for datum in response.data]
    database_names = STT.objects.values_list("name", flat=True).order_by("name")
    assert response_names == list(database_names)


@override_settings(
    CACHES={
        "stts": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-test-cache-location",  # Unique location to avoid conflicts
            "KEY_PREFIX": "test",
        },
    }
)
class TestSTTApiAlphaViewCache(TestCase):
    """Tests for the STTApiAlphaView class."""

    api_client = APIClient()

    def setUp(self):
        """Run before all tests in TestCase."""
        super().setUp()
        cache = caches["stts"]
        cache.clear()

        user = UserFactory.create()
        self.api_client.login(username=user.username, password="test_password")

    def test_existing_cache_avoids_lookup(self):
        """Test that no lookup is performed if flags exist in the cache."""
        mock_queryset = MagicMock()
        with patch.object(
            STTApiAlphaView, "get_queryset", return_value=mock_queryset
        ) as mock_method:
            # request and check the cache was cold
            response = self.api_client.get(reverse("stts-alpha"))
            assert response.status_code == status.HTTP_200_OK
            assert mock_method.called

            mock_method.reset_mock()

            # the cache should be warm now, request again
            response = self.api_client.get(reverse("stts-alpha"))
            assert response.status_code == status.HTTP_200_OK
            assert not mock_method.called

    def test_no_cache_forces_lookup(self):
        """Test that a lookup is performed if there are no flags in the cache."""
        mock_queryset = MagicMock()
        with patch.object(
            STTApiAlphaView, "get_queryset", return_value=mock_queryset
        ) as mock_method:
            # request and check the cache was cold
            response = self.api_client.get(reverse("stts-alpha"))
            assert response.status_code == status.HTTP_200_OK
            assert mock_method.called
