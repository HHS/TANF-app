from django.utils.crypto import get_random_string
from rest_framework import serializers

from tdpservice.reports.models import ReportFile
from tdpservice.stts.models import STT
from tdpservice.users.models import User


class ReportFileSerializer(serializers.ModelSerializer):
    """Serializer for Report Files."""
    file = serializers.FileField(write_only=True)
    stt = serializers.PrimaryKeyRelatedField(queryset=STT.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        """Metadata."""

        model = ReportFile
        fields = [
            "id",
            "stt",
            "user",
            "section",
            "quarter",
            "year",
            "version",
            "original_filename",
            "extension",
            "created_at",
            "file",
        ]

        read_only_fields = [
            "id",
            "version",
        ]

    def create(self, validated_data):
        """Admins may directly create a single ReportFile."""
        # Set filename/slug/extension defaults if missing
        upload = validated_data.get("file")

        validated_data.setdefault("original_filename", upload.name)
        validated_data.setdefault("slug", upload.name)
        validated_data.setdefault("extension", "zip")

        # create and bump the version
        return ReportFile.create_new_version(validated_data)

    def validate_file(self, file):
        """Validate the file field."""
        file_name = file.name.lower()

        if not file_name.endswith(".zip"):
            raise serializers.ValidationError("File must be a zip folder")

        return file
            
