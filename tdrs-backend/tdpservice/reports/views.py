"""Define API views for reports app."""

import logging
from wsgiref.util import FileWrapper

from django.db import DatabaseError
from django.db.models import Count, F, Min, Q
from django.http import FileResponse
from django.utils import timezone

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from tdpservice.reports.models import ReportFile, ReportSource
from tdpservice.reports.serializers import (
    ReportFileSerializer,
    ReportSourceDownloadStatisticsSerializer,
    ReportSourceSerializer,
)
from tdpservice.reports.tasks import process_report_source
from tdpservice.users.permissions import (
    IsApprovedPermission,
    ReportFilePermissions,
    ReportSourcePermissions,
)

logger = logging.getLogger(__name__)


class ReportFileViewSet(ModelViewSet):
    """Report file views."""

    http_method_names = ["get", "post", "head"]
    queryset = (
        ReportFile.objects.all()
        .order_by("-created_at")
        .select_related("stt", "user", "source")
    )
    serializer_class = ReportFileSerializer
    permission_classes = [ReportFilePermissions, IsApprovedPermission]

    def get_queryset(self):
        """Filter reports by STT for Data Analysts and optionally by year."""
        queryset = super().get_queryset()

        # Data Analysts should only see reports for their assigned STT
        if self.request.user.is_data_analyst and hasattr(self.request.user, "stt"):
            queryset = queryset.filter(stt=self.request.user.stt)

        # Regional Staff should only see reports for STTs in their region
        if self.request.user.is_regional_staff and hasattr(
            self.request.user, "regions"
        ):
            user_regions = self.request.user.regions.all()
            queryset = queryset.filter(stt__region__in=user_regions)

        # Query params for adding additional filters to queryset
        year = self.request.query_params.get('year')
        latest = self.request.query_params.get('latest')
        stt = self.request.query_params.get('stt')
        report_type = self.request.query_params.get('report_type')

        if stt:
            queryset = queryset.filter(stt_id=stt)
        if year:
            queryset = queryset.filter(year=year)
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        if latest and latest.lower() == 'true':
            queryset = queryset.order_by('-created_at')[:1]

        return queryset

    def get_serializer_context(self):
        """Retrieve additional context required by serializer."""
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    @action(methods=["get"], detail=True)
    def download(self, request, pk=None):
        """Stream a report and record its first Data Analyst download."""
        report_file = self.get_object()
        response = FileResponse(
            FileWrapper(report_file.file), filename=report_file.original_filename
        )

        if request.method == "GET" and request.user.is_data_analyst:
            try:
                ReportFile.objects.filter(
                    pk=report_file.pk,
                    downloaded_at__isnull=True,
                ).update(downloaded_at=timezone.now())
            except DatabaseError:
                logger.exception(
                    "Failed to record download for report file %s", report_file.pk
                )

        return response


class ReportSourceViewSet(ModelViewSet):
    """Report source views for batch uploading report files."""

    http_method_names = ["get", "post", "head", "options"]
    queryset = ReportSource.objects.annotate(
        downloaded_count=Count(
            "report_files__stt",
            filter=Q(report_files__downloaded_at__isnull=False),
            distinct=True,
        ),
        total_count=Count("report_files__stt", distinct=True),
    ).order_by("-created_at")
    serializer_class = ReportSourceSerializer
    permission_classes = [ReportSourcePermissions, IsApprovedPermission]

    def get_queryset(self):
        """Filter report sources by year and/or report_type if provided."""
        queryset = super().get_queryset()

        # Query params for filtering
        year = self.request.query_params.get('year')
        report_type = self.request.query_params.get('report_type')

        if year:
            queryset = queryset.filter(year=year)
        if report_type:
            queryset = queryset.filter(report_type=report_type)

        return queryset

    def get_serializer_context(self):
        """Retrieve additional context required by serializer."""
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    def create(self, request, *args, **kwargs):
        """Create a new report source and trigger async processing."""
        response = super().create(request, *args, **kwargs)

        # Process the report source zip file
        process_report_source.delay(response.data.get("id"))

        return response

    @action(methods=["get"], detail=True, url_path="download-statistics")
    def download_statistics(self, request, pk=None):
        """Return region-grouped STT download statistics for a report source."""
        report_source = self.get_object()
        report_rows = list(
            report_source.report_files.filter(stt__isnull=False)
            .values("stt_id", "stt__name", "stt__region_id")
            .annotate(downloaded_at=Min("downloaded_at"))
            .order_by(
                F("stt__region_id").asc(nulls_last=True),
                "stt__name",
            )
        )

        regions = []
        for row in report_rows:
            region_id = row["stt__region_id"]
            if not regions or regions[-1]["id"] != region_id:
                regions.append({"id": region_id, "stts": []})

            regions[-1]["stts"].append(
                {
                    "id": row["stt_id"],
                    "name": row["stt__name"],
                    "downloaded_at": row["downloaded_at"],
                }
            )

        response_data = {
            "report_source_id": report_source.id,
            "downloaded_count": sum(
                row["downloaded_at"] is not None for row in report_rows
            ),
            "total_count": len(report_rows),
            "regions": regions,
        }
        return Response(ReportSourceDownloadStatisticsSerializer(response_data).data)
