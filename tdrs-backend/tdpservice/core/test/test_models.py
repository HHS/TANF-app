"""Module for testing the core model."""
from django.core.exceptions import ValidationError
from django.db import models

import pytest

from tdpservice.core.models import BaseLog, FeatureFlag, GlobalPermission


def test_base_log_primary_key_matches_initial_migration():
    """Keep the model state aligned with the BigAutoField created by migration 0007."""
    assert isinstance(BaseLog._meta.get_field("id"), models.BigAutoField)


@pytest.mark.django_db
def test_manager_get_queryset():
    """Test the get queryset method returns a query."""
    GlobalPermission.objects.create(
        name="Can View User Data", codename="view_user_data"
    )
    global_permissions = GlobalPermission.objects.first()
    assert global_permissions.name == "Can View User Data"


@pytest.mark.django_db
def test_base_log_manager_attaches_logs_to_any_model_instance():
    """Test BaseLog stores and queries generic model relations."""
    flag = FeatureFlag.objects.create(feature_name="logged_feature")

    log = BaseLog.objects.create_for_object(
        flag,
        event_type="feature_flag_test",
        note="Feature flag changed during test",
    )

    assert BaseLog.objects.for_object(flag).get() == log
    assert log.content_object == flag
    assert log.object_id == str(flag.pk)
    assert log.event_id is not None


@pytest.mark.django_db
class TestFeatureFlagModel:
    """Tests for the FeatureFlag model."""

    def test_create_feature_flag(self):
        """Test creating a feature flag with minimal fields."""
        flag = FeatureFlag.objects.create(feature_name="test_feature")
        assert flag.feature_name == "test_feature"
        assert flag.type == FeatureFlag.Type.ON_OFF
        assert flag.enabled is False
        assert flag.rollout_percentage is None
        assert flag.config == {}
        assert flag.description == ""
        assert flag.created_at is not None
        assert flag.updated_at is not None

    def test_create_feature_flag_enabled(self):
        """Test creating an enabled feature flag."""
        flag = FeatureFlag.objects.create(feature_name="enabled_feature", enabled=True)
        assert flag.enabled is True

    def test_create_feature_flag_with_config(self):
        """Test creating a feature flag with configuration."""
        config = {"max_users": 100, "regions": ["east", "west"]}
        flag = FeatureFlag.objects.create(
            feature_name="configured_feature", config=config
        )
        assert flag.config == config
        assert flag.config["max_users"] == 100
        assert "east" in flag.config["regions"]

    def test_create_feature_flag_with_description(self):
        """Test creating a feature flag with description."""
        flag = FeatureFlag.objects.create(
            feature_name="described_feature",
            description="This feature enables PIA datafile submission",
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
            feature_name="datafiles_pia_submission", enabled=False
        )
        assert str(flag) == "datafiles_pia_submission (disabled)"

    def test_str_representation_enabled(self):
        """Test string representation for enabled flag."""
        flag = FeatureFlag.objects.create(feature_name="reports_feedback", enabled=True)
        assert str(flag) == "reports_feedback (enabled)"

    def test_ordering(self):
        """Test that flags are ordered by feature_name."""
        FeatureFlag.objects.create(feature_name="zebra_feature")
        FeatureFlag.objects.create(feature_name="alpha_feature")
        FeatureFlag.objects.create(feature_name="beta_feature")

        flags = list(
            FeatureFlag.objects.filter(
                feature_name__in=[
                    "zebra_feature",
                    "alpha_feature",
                    "beta_feature",
                ]
            )
        )
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

    def test_rollout_percentage_is_required_for_rollout_flag(self):
        """Test rollout flags require a percentage."""
        flag = FeatureFlag(
            feature_name="missing_percentage",
            type=FeatureFlag.Type.RANDOM_ROLLOUT,
        )

        with pytest.raises(ValidationError) as exc_info:
            flag.full_clean()

        assert "rollout_percentage" in exc_info.value.message_dict

    def test_on_off_flag_rejects_rollout_percentage(self):
        """Test on/off flags cannot retain rollout configuration."""
        flag = FeatureFlag(
            feature_name="unexpected_percentage",
            type=FeatureFlag.Type.ON_OFF,
            rollout_percentage=50,
        )

        with pytest.raises(ValidationError) as exc_info:
            flag.full_clean()

        assert "rollout_percentage" in exc_info.value.message_dict

    @pytest.mark.parametrize("rollout_percentage", [-1, 101])
    def test_rollout_percentage_must_be_between_zero_and_one_hundred(
        self, rollout_percentage
    ):
        """Test percentages outside the supported range are rejected."""
        flag = FeatureFlag(
            feature_name="invalid_percentage",
            type=FeatureFlag.Type.RANDOM_ROLLOUT,
            rollout_percentage=rollout_percentage,
        )

        with pytest.raises(ValidationError) as exc_info:
            flag.full_clean()

        assert "rollout_percentage" in exc_info.value.message_dict

    def test_disabled_rollout_flag_is_never_enabled(self):
        """Test the master switch disables a rollout flag."""
        flag = FeatureFlag(
            enabled=False,
            type=FeatureFlag.Type.RANDOM_ROLLOUT,
            rollout_percentage=100,
        )

        assert flag.is_enabled(random_value=0) is False

    @pytest.mark.parametrize(
        ("rollout_percentage", "random_value", "expected"),
        [
            (0, 0, False),
            (50, 49.99, True),
            (50, 50, False),
            (100, 99.99, True),
        ],
    )
    def test_rollout_flag_evaluation(self, rollout_percentage, random_value, expected):
        """Test rollout boundaries and partial rollout behavior."""
        flag = FeatureFlag(
            enabled=True,
            type=FeatureFlag.Type.RANDOM_ROLLOUT,
            rollout_percentage=rollout_percentage,
        )

        assert flag.is_enabled(random_value=random_value) is expected

    def test_unknown_flag_type_fails_closed(self):
        """Test unsupported future flag types do not enable a feature."""
        flag = FeatureFlag(enabled=True, type="unsupported")

        assert flag.is_enabled(random_value=0) is False
