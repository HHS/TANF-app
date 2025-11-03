"""Serialize report data."""
from django.utils.crypto import get_random_string
from rest_framework import serializers

from tdpservice.backends import DataFilesS3Storage
from tdpservice.reports.models import ReportFile, ReportIngest
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


class ReportIngestSerializer(serializers.ModelSerializer):
    """Serializer for Report Ingest."""

    master_zip = serializers.FileField(write_only=True)

    class Meta:
        """Metadata."""

        model = ReportIngest
        fields = [
            "id",
            "master_zip",  # write-only input
            "original_filename",  # populated from upload, read-only to clients
            "s3_key",  # read-only (where we stored it)
            "status",
            "created_at",
            "processed_at",
            "num_reports_created",
            "error_message",
        ]
        read_only_fields = [
            "id",
            "original_filename",
            "s3_key",
            "status",
            "created_at",
            "processed_at",
            "num_reports_created",
            "error_message",
        ]

    def create(self, validated_data):
        """Create a ReportIngest record for a master zip file upload."""
        file = validated_data.pop("master_zip")

        storage = DataFilesS3Storage()
        key = f"reports/master/{get_random_string(12)}-{file.name}"
        s3_key = storage.save(key, file)

        user = self.context["user"]
        ingest = ReportIngest.objects.create(
            original_filename=file.name,
            slug=file.name,
            extension="zip",
            uploaded_by=user,
            s3_key=s3_key,
        )

        return ingest

    def validate_master_zip(self, master_zip):
        """Validate the file field."""
        file_name = master_zip.name.lower()

        if not file_name.endswith(".zip"):
            raise serializers.ValidationError("File must be a zip folder")

        return master_zip
