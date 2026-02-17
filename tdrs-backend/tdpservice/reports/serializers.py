"""Serialize report data."""
from rest_framework import serializers

from tdpservice.reports.models import ReportFile, ReportSource
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
            "date_extracted_on",
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


class ReportSourceSerializer(serializers.ModelSerializer):
    """Serializer for Report Source."""

    class Meta:
        """Metadata."""

        model = ReportSource
        fields = [
            "id",
            "original_filename",
            "status",
            "uploaded_by",
            "created_at",
            "processed_at",
            "num_reports_created",
            "error_message",
            "date_extracted_on",
            "year",
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
        """Create a ReportSource record for a report source zip file upload."""
        file = validated_data.get("file")
        date_extracted_on = validated_data.get("date_extracted_on")  # optional
        year = validated_data.get("year")  # optional
        user = self.context["user"]

        source = ReportSource.objects.create(
            original_filename=file.name,
            slug=file.name,
            extension="zip",
            uploaded_by=user,
            date_extracted_on=date_extracted_on,
            year=year,
            file=file,
        )

        return source

    def validate_file(self, file):
        """Validate the file field."""
        file_name = file.name.lower()

        if not file_name.endswith(".zip"):
            raise serializers.ValidationError("File must be a zip folder")

        return file
