"""Serialize report data."""
from rest_framework import serializers

from tdpservice.reports.models import ReportFile, ReportSource, ReportType
from tdpservice.stts.models import STT


class ReportDownloadStatisticsSTTSerializer(serializers.Serializer):
    """Serialize one STT's feedback report download status."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    downloaded_at = serializers.DateTimeField(allow_null=True)


class ReportDownloadStatisticsRegionSerializer(serializers.Serializer):
    """Serialize feedback report download statuses grouped by region."""

    id = serializers.IntegerField(allow_null=True)
    stts = ReportDownloadStatisticsSTTSerializer(many=True)


class ReportSourceDownloadStatisticsSerializer(serializers.Serializer):
    """Serialize download statistics for one report source."""

    report_source_id = serializers.IntegerField()
    downloaded_count = serializers.IntegerField()
    total_count = serializers.IntegerField()
    regions = ReportDownloadStatisticsRegionSerializer(many=True)


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
            "report_type",
            "version",
            "original_filename",
            "extension",
            "created_at",
            "downloaded_at",
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
            "downloaded_at",
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

    downloaded_count = serializers.SerializerMethodField()
    total_count = serializers.SerializerMethodField()

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
            "report_type",
            "file",
            "downloaded_count",
            "total_count",
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

    def get_downloaded_count(self, obj):
        """Return the annotated distinct count without issuing another query."""
        return getattr(obj, "downloaded_count", 0)

    def get_total_count(self, obj):
        """Return the annotated distinct count without issuing another query."""
        return getattr(obj, "total_count", 0)

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
            report_type=validated_data.get("report_type", ReportType.TANF_SSP),
            file=file,
        )

        return source

    def validate_file(self, file):
        """Validate the file field."""
        file_name = file.name.lower()

        if not file_name.endswith(".zip"):
            raise serializers.ValidationError("File must be a zip folder")

        return file
