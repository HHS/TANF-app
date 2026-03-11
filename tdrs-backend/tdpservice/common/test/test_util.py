"""Test the common utils."""

import pytest

from tdpservice.common.util import get_cloudgov_broker_db_numbers


@pytest.mark.parametrize(
    "env,expected",
    [
        # dev envs
        ("raft", {"celery": "0", "caches": {"stts": "1", "feature-flags": "2"}}),
        ("qasp", {"celery": "3", "caches": {"stts": "4", "feature-flags": "5"}}),
        ("a11y", {"celery": "6", "caches": {"stts": "7", "feature-flags": "8"}}),
        # staging
        ("develop", {"celery": "0", "caches": {"stts": "1", "feature-flags": "2"}}),
        ("staging", {"celery": "3", "caches": {"stts": "4", "feature-flags": "5"}}),
        # prod
        ("prod", {"celery": "0", "caches": {"stts": "1", "feature-flags": "2"}}),
    ],
)
@pytest.mark.django_db
def test_get_cloudgov_broker_db_numbers(env, expected):
    """Test redis broker db number generation for deployed envs."""
    result = get_cloudgov_broker_db_numbers(env)
    assert result == expected
