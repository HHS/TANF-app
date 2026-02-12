"""Core API tests."""

import uuid
from unittest.mock import MagicMock, patch

from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.core.cache import caches
from django.test import TestCase, override_settings
from django.urls import reverse

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from tdpservice.conftest import UserFactory
from tdpservice.core.models import FeatureFlag
from tdpservice.core.views import FeatureFlagView
from tdpservice.data_files.models import DataFile


@pytest.mark.django_db
def test_write_logs(api_client, ofa_admin):
    """Test endpoint consumption of arbitrary JSON to be logged."""
    user = ofa_admin
    api_client.login(username=user.username, password="test_password")
    data = {
        "original_filename": "data_file.txt",
        "quarter": "Q1",
        "slug": uuid.uuid4(),
        "user": user.id,
        "year": 2020,
        "section": "Active Case Data",
        "timestamp": "2021-04-26T18:32:43.330Z",
        "type": "error",
        "message": "Something strange happened",
    }
    response = api_client.post("/v1/logs/", data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == "Success"


@pytest.mark.django_db
def test_log_output(api_client, ofa_admin, caplog):
    """Test endpoint's writing of logs to the output."""
    user = ofa_admin
    api_client.login(username=user.username, password="test_password")
    data = {
        "original_filename": "data_file.txt",
        "quarter": "Q1",
        "slug": uuid.uuid4(),
        "user": user.id,
        "year": 2020,
        "section": "Active Case Data",
        "timestamp": "2021-04-26T18:32:43.330Z",
        "type": "alert",
        "message": "User submitted 1 file(s)",
    }

    api_client.post("/v1/logs/", data)

    assert "User submitted 1 file(s)" in caplog.text


@pytest.mark.django_db
def test_log_entry_creation(api_client, data_file_instance):
    """Test endpoint's creation of LogEntry objects."""
    api_client.login(
        username=data_file_instance.user.username, password="test_password"
    )
    data = {
        "original_filename": data_file_instance.original_filename,
        "quarter": data_file_instance.quarter,
        "slug": data_file_instance.slug,
        "user": data_file_instance.user.username,
        "year": data_file_instance.year,
        "section": data_file_instance.section,
        "timestamp": "2021-04-26T18:32:43.330Z",
        "type": "alert",
        "message": "User submitted file(s)",
        "files": [data_file_instance.pk],
    }

    api_client.post("/v1/logs/", data)

    assert LogEntry.objects.filter(
        content_type_id=ContentType.objects.get_for_model(DataFile).pk,
        object_id=data_file_instance.pk,
    ).exists()


@override_settings(
    CACHES={
        "feature-flags": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-test-cache-location",  # Unique location to avoid conflicts
            "KEY_PREFIX": "test",
        },
    }
)
class TestFeatureFlagView(TestCase):
    """Tests for the FeatureFlagView class."""

    api_client = APIClient()

    def setUp(self):
        """Run before all tests in TestCase."""
        super().setUp()
        cache = caches["feature-flags"]
        cache.clear()

        user = UserFactory.create()
        self.api_client.login(username=user.username, password="test_password")

    def test_existing_cache_avoids_lookup(self):
        """Test that no lookup is performed if flags exist in the cache."""
        mock_queryset = MagicMock()
        with patch.object(
            FeatureFlagView, "get_queryset", return_value=mock_queryset
        ) as mock_method:
            # request and check the cache was cold
            response = self.api_client.get(reverse("feature-flags"))
            assert response.status_code == status.HTTP_200_OK
            assert mock_method.called

            mock_method.reset_mock()

            # the cache should be warm now, request again
            response = self.api_client.get(reverse("feature-flags"))
            assert response.status_code == status.HTTP_200_OK
            assert not mock_method.called

    def test_no_cache_forces_lookup(self):
        """Test that a lookup is performed if there are no flags in the cache."""
        mock_queryset = MagicMock()
        with patch.object(
            FeatureFlagView, "get_queryset", return_value=mock_queryset
        ) as mock_method:
            # request and check the cache was cold
            response = self.api_client.get(reverse("feature-flags"))
            assert response.status_code == status.HTTP_200_OK
            assert mock_method.called

    def test_saving_flag_invalidates_cache(self):
        """Test saving a feature flag invalidates existing cache."""
        mock_queryset = MagicMock()
        with patch.object(
            FeatureFlagView, "get_queryset", return_value=mock_queryset
        ) as mock_method:
            # request and check the cache was cold
            response = self.api_client.get(reverse("feature-flags"))
            assert response.status_code == status.HTTP_200_OK
            assert mock_method.called

            mock_method.reset_mock()

            # the cache should be warm now, request again
            response = self.api_client.get(reverse("feature-flags"))
            assert response.status_code == status.HTTP_200_OK
            assert not mock_method.called

            mock_method.reset_mock()

            # create a new feature flag
            FeatureFlag.objects.create(feature_name="unit-test")

            # check that the cache was invalidated
            response = self.api_client.get(reverse("feature-flags"))
            assert response.status_code == status.HTTP_200_OK
            assert mock_method.called
