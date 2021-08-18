"""Serialize stt data."""

from rest_framework import serializers

from tdpservice.data_files.errors import ImmutabilityError
from tdpservice.data_files.models import DataFile
from tdpservice.data_files.validators import validate_data_file
from tdpservice.stts.models import STT
from tdpservice.users.models import User


class DataFileSerializer(serializers.ModelSerializer):
    """Serializer for Data files."""

    file = serializers.FileField(
        write_only=True,
        validators=[validate_data_file]
    )
    stt = serializers.PrimaryKeyRelatedField(queryset=STT.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        """Metadata."""

        model = DataFile
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
        return DataFile.create_new_version(validated_data)

    def update(self, instance, validated_data):
        """Throw an error if a user tries to update a data_file."""
        raise ImmutabilityError(instance, validated_data)
