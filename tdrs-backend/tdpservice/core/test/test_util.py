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
