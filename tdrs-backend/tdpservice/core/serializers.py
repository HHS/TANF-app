"""Serialize core model data."""

from rest_framework import serializers

from tdpservice.core.models import FeatureFlag


class FeatureFlagSerializer(serializers.ModelSerializer):
    """FeatureFlag serializer."""

    enabled = serializers.SerializerMethodField()

    def get_enabled(self, obj: FeatureFlag) -> bool:
        """Evaluate the flag for the current request."""
        return obj.is_enabled()

    class Meta:
        """Metadata."""

        model = FeatureFlag
        fields = [
            "feature_name",
            "type",
            "enabled",
            "rollout_percentage",
            "config",
            "description",
        ]
