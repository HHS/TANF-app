"""Serialize stt data."""

from django.db.models import Max

from rest_framework import serializers

from ..stts.models import STT
from ..users.models import User
from .models import ReportFile


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
        # EDGE CASE
        # We may need to try to get this all in one sql query
        # if we ever encounter race conditions.
        version = 1
        latest_report = ReportFile.objects.filter(
            slug__exact=validated_data["slug"],
        ).aggregate(Max("version"))

        if latest_report["version__max"] is not None:
            version = latest_report["version__max"] + 1

        return ReportFile.objects.create(version=version, **validated_data,)
        # I think I should have this here?

    def update():
        """Throw an error if a user tries to update a report."""
        raise "Cannot update, reports are immutable. Create a new one instead."
