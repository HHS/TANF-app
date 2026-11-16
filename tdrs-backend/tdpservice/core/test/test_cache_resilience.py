"""Database-backed API responses and model changes survive Redis outages."""

from unittest.mock import patch

from django.core.cache.backends.redis import RedisCacheClient
from django.test import override_settings
from django.urls import reverse

import pytest
from redis.exceptions import ConnectionError, TimeoutError

from tdpservice.core.models import FeatureFlag
from tdpservice.settings.common import Common


@pytest.fixture
def unavailable_cache():
    """Inject failures at the Redis boundary while retaining the real cache backend."""
    with override_settings(CACHES=Common.CACHES):
        with (
            patch.object(RedisCacheClient, "get", return_value=None) as read,
            patch.object(RedisCacheClient, "set") as write,
            patch.object(RedisCacheClient, "clear", return_value=True) as clear,
        ):
            yield {"get": read, "set": write, "clear": clear}


@pytest.mark.django_db
@pytest.mark.parametrize("error", [ConnectionError, TimeoutError])
@pytest.mark.parametrize("operation", ["get", "set"])
@pytest.mark.parametrize("detail", [False, True])
def test_feature_flags_survive_cache_failure(
    api_client, user, unavailable_cache, operation, error, detail
) -> None:
    """Both feature-flag endpoints return database values after cache failures."""
    flag = FeatureFlag.objects.create(feature_name="cache_failure", enabled=True)
    unavailable_cache[operation].side_effect = error
    api_client.force_authenticate(user=user)
    url = (
        reverse("feature-flag-detail", args=[flag.feature_name])
        if detail
        else reverse("feature-flag-list")
    )

    response = api_client.get(url)

    assert response.status_code == 200
    result = (
        response.data
        if detail
        else next(
            item for item in response.data if item["feature_name"] == flag.feature_name
        )
    )
    assert result["feature_name"] == flag.feature_name
    assert result["enabled"] is True
    assert unavailable_cache[operation].called


@pytest.mark.django_db
@pytest.mark.parametrize("error", [ConnectionError, TimeoutError])
@pytest.mark.parametrize("operation", ["get", "set"])
def test_stts_survive_cache_failure(
    api_client, user, stt, unavailable_cache, operation, error
) -> None:
    """Page-cache read and deferred write failures preserve the STT response."""
    unavailable_cache[operation].side_effect = error
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("stts-alpha"))

    assert response.status_code == 200
    assert any(item["id"] == stt.id for item in response.data)
    names = [item["name"] for item in response.data]
    assert names == sorted(names)
    assert unavailable_cache[operation].called


@pytest.mark.django_db
@pytest.mark.parametrize("error", [ConnectionError, TimeoutError])
def test_flag_changes_survive_invalidation_failure(
    unavailable_cache, error, caplog
) -> None:
    """Failed invalidation does not undo a flag create, update, or delete."""
    unavailable_cache["clear"].side_effect = error

    flag = FeatureFlag.objects.create(feature_name="invalidation_failure")
    assert FeatureFlag.objects.filter(pk=flag.pk).exists()
    flag.enabled = True
    flag.save()
    flag.refresh_from_db()
    assert flag.enabled is True
    flag_id = flag.pk
    flag.delete()
    assert not FeatureFlag.objects.filter(pk=flag_id).exists()
    assert "invalidation failed" in caplog.text
