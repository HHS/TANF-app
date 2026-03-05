"""Serialize core model data."""

from rest_framework import serializers

from tdpservice.core.models import FeatureFlag


class FeatureFlagSerializer(serializers.ModelSerializer):
    """FeatureFlag serializer."""

    class Meta:
        """Metadata."""

        model = FeatureFlag
        fields = [
            "feature_name",
            "enabled",
            "config",
            "description",
        ]
