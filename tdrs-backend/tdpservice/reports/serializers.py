"""Serialize stt data."""

from rest_framework import serializers
from ..stts.models import STT
from ..users.models import User
from .models import ReportFile

from .errors import ImmutabilityError

class ReportFileSerializer(serializers.ModelSerializer):
    """Serializer for Report files."""

    stt = serializers.PrimaryKeyRelatedField(queryset=STT.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        """Metadata."""

        model = ReportFile
        fields = [
            "original_filename",
            "slug",
            "extension",
            "user",
            "stt",
            "year",
            "quarter",
            "section",
        ]

    def create(self, validated_data):
        """Create a new entry with a new version number."""
        return ReportFile.create_new_version(validated_data)

    def update(self, instance, validated_data):
        """Throw an error if a user tries to update a report."""
        raise ImmutabilityError(instance, validated_data)
