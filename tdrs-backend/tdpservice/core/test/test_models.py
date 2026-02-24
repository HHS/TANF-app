"""Module for testing the core model."""
import pytest

from tdpservice.core.models import FeatureFlag, GlobalPermission


@pytest.mark.django_db
def test_manager_get_queryset():
    """Test the get queryset method returns a query."""
    GlobalPermission.objects.create(
        name="Can View User Data", codename="view_user_data"
    )
    global_permissions = GlobalPermission.objects.first()
    assert global_permissions.name == "Can View User Data"


@pytest.mark.django_db
class TestFeatureFlagModel:
    """Tests for the FeatureFlag model."""

    def test_create_feature_flag(self):
        """Test creating a feature flag with minimal fields."""
        flag = FeatureFlag.objects.create(feature_name="test_feature")
        assert flag.feature_name == "test_feature"
        assert flag.enabled is False
        assert flag.config == {}
        assert flag.description == ""
        assert flag.created_at is not None
        assert flag.updated_at is not None

    def test_create_feature_flag_enabled(self):
        """Test creating an enabled feature flag."""
        flag = FeatureFlag.objects.create(
            feature_name="enabled_feature",
            enabled=True
        )
        assert flag.enabled is True

    def test_create_feature_flag_with_config(self):
        """Test creating a feature flag with configuration."""
        config = {"max_users": 100, "regions": ["east", "west"]}
        flag = FeatureFlag.objects.create(
            feature_name="configured_feature",
            config=config
        )
        assert flag.config == config
        assert flag.config["max_users"] == 100
        assert "east" in flag.config["regions"]

    def test_create_feature_flag_with_description(self):
        """Test creating a feature flag with description."""
        flag = FeatureFlag.objects.create(
            feature_name="described_feature",
            description="This feature enables PIA datafile submission"
        )
        assert flag.description == "This feature enables PIA datafile submission"

    def test_feature_name_uniqueness(self):
        """Test that feature_name must be unique."""
        FeatureFlag.objects.create(feature_name="unique_feature")
        with pytest.raises(Exception):
            FeatureFlag.objects.create(feature_name="unique_feature")

    def test_str_representation_disabled(self):
        """Test string representation for disabled flag."""
        flag = FeatureFlag.objects.create(
            feature_name="datafiles_pia_submission",
            enabled=False
        )
        assert str(flag) == "datafiles_pia_submission (disabled)"

    def test_str_representation_enabled(self):
        """Test string representation for enabled flag."""
        flag = FeatureFlag.objects.create(
            feature_name="reports_feedback",
            enabled=True
        )
        assert str(flag) == "reports_feedback (enabled)"

    def test_ordering(self):
        """Test that flags are ordered by feature_name."""
        FeatureFlag.objects.create(feature_name="zebra_feature")
        FeatureFlag.objects.create(feature_name="alpha_feature")
        FeatureFlag.objects.create(feature_name="beta_feature")

        flags = list(FeatureFlag.objects.all())
        assert flags[0].feature_name == "alpha_feature"
        assert flags[1].feature_name == "beta_feature"
        assert flags[2].feature_name == "zebra_feature"

    def test_updated_at_changes_on_update(self):
        """Test that updated_at changes when the flag is updated."""
        flag = FeatureFlag.objects.create(feature_name="update_test")
        original_updated_at = flag.updated_at

        flag.enabled = True
        flag.save()
        flag.refresh_from_db()

        assert flag.updated_at > original_updated_at

    def test_config_defaults_to_empty_dict(self):
        """Test that config defaults to an empty dict, not None."""
        flag = FeatureFlag.objects.create(feature_name="config_default_test")
        assert flag.config is not None
        assert isinstance(flag.config, dict)
        assert flag.config == {}
