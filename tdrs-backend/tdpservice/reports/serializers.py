"""Serialize report data."""
from rest_framework import serializers

from tdpservice.reports.models import ReportFile, ReportIngest
from tdpservice.stts.models import STT


class ReportFileSerializer(serializers.ModelSerializer):
    """Serializer for Report Files."""

    file = serializers.FileField(write_only=True)
    stt = serializers.PrimaryKeyRelatedField(queryset=STT.objects.all())
    user = serializers.PrimaryKeyRelatedField(read_only=True)

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
            "user",
            "version",
            "original_filename",
            "slug",
            "extension",
            "created_at",
        ]

    def create(self, validated_data):
        """Admins may directly create a single ReportFile."""
        request_user = self.context["user"]
        validated_data["user"] = request_user

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

    class Meta:
        """Metadata."""

        model = ReportIngest
        fields = [
            "id",
            "original_filename",
            "status",
            "uploaded_by",
            "created_at",
            "processed_at",
            "num_reports_created",
            "error_message",
            "quarter",
            "file",
        ]
        read_only_fields = [
            "id",
            "original_filename",
            "status",
            "uploaded_by",
            "created_at",
            "processed_at",
            "num_reports_created",
            "error_message",
        ]

    def create(self, validated_data):
        """Create a ReportIngest record for a master zip file upload."""
        file = validated_data.get("file")
        quarter = validated_data.get("quarter")  # optional
        user = self.context["user"]

        ingest = ReportIngest.objects.create(
            original_filename=file.name,
            slug=file.name,
            extension="zip",
            uploaded_by=user,
            quarter=quarter,
            file=file,
        )

        return ingest

    def validate_file(self, file):
        """Validate the file field."""
        file_name = file.name.lower()

        if not file_name.endswith(".zip"):
            raise serializers.ValidationError("File must be a zip folder")

        return file
