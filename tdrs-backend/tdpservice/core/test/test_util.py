"""Test the core util module."""

import pytest

from tdpservice.core.models import FeatureFlag
from tdpservice.core.utils import get_feature_flag


@pytest.mark.django_db
def test_get_feature_flag_exists():
    """Test the get feature flag method returns a feature flag."""
    FeatureFlag.objects.create(
        feature_name="test-flag", config={"test": "me"}, enabled=True
    )
    flag_enabled, flag_config = get_feature_flag("test-flag")
    assert flag_enabled is True
    assert flag_config == {"test": "me"}


@pytest.mark.django_db
def test_get_feature_flag_not_exists():
    """Test the get feature flag method returns a default when no feature flag exists."""
    flag_enabled, flag_config = get_feature_flag("test-flag")
    assert flag_enabled is False
    assert flag_config == {}


@pytest.mark.django_db
def test_get_feature_flag_evaluates_rollout_percentage():
    """Test the helper evaluates rollout flags for the current request."""
    FeatureFlag.objects.create(
        feature_name="rollout-flag",
        type=FeatureFlag.Type.RANDOM_ROLLOUT,
        enabled=True,
        rollout_percentage=25,
    )

    enabled, _ = get_feature_flag("rollout-flag", random_value=24.99)
    disabled, _ = get_feature_flag("rollout-flag", random_value=25)

    assert enabled is True
    assert disabled is False
