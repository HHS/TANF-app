"""Serialize stt data."""

from rest_framework import serializers

from tdpservice.reports.errors import ImmutabilityError
from tdpservice.reports.models import ReportFile
from tdpservice.reports.validators import validate_data_file
from tdpservice.stts.models import STT
from tdpservice.users.models import User


class ReportFileSerializer(serializers.ModelSerializer):
    """Serializer for Report files."""

    file = serializers.FileField(
        write_only=True,
        validators=[validate_data_file]
    )
    stt = serializers.PrimaryKeyRelatedField(queryset=STT.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        """Metadata."""

        model = ReportFile
        fields = [
            "file",
            "id",
            "original_filename",
            "slug",
            "extension",
            "user",
            "stt",
            "year",
            "quarter",
            "section",
            "created_at"
        ]

    def create(self, validated_data):
        """Create a new entry with a new version number."""
        return ReportFile.create_new_version(validated_data)

    def update(self, instance, validated_data):
        """Throw an error if a user tries to update a report."""
        raise ImmutabilityError(instance, validated_data)


class DownloadReportFileSerializer(serializers.ModelSerializer):
    """Serializer for Report files."""

    file = serializers.FileField(
        read_only=True,
    )

    class Meta:
        """Metadata."""

        model = ReportFile
        fields = [
            "file",
            "original_filename",
        ]
