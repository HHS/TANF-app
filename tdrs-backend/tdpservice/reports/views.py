"""Define API views for reports app."""

from wsgiref.util import FileWrapper
from django.http import FileResponse
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from tdpservice.reports.models import ReportFile, ReportSource
from tdpservice.reports.serializers import ReportFileSerializer, ReportSourceSerializer
from tdpservice.reports.tasks import process_report_source
from tdpservice.users.permissions import IsApprovedPermission, ReportFilePermissions


class ReportFileViewSet(ModelViewSet):
    """Report file views."""

    http_method_names = ["get", "post", "head"]
    queryset = ReportFile.objects.all().order_by("-created_at")
    serializer_class = ReportFileSerializer
    permission_classes = [ReportFilePermissions, IsApprovedPermission]

    def get_serializer_context(self):
        """Retrieve additional context required by serializer."""
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    @action(methods=["get"], detail=True)
    def download(self, request, pk=None):
        """Retrieve a file from s3 then stream it to the client."""
        obj = self.get_object()
        return FileResponse(FileWrapper(obj.file), filename=obj.original_filename)


class ReportSourceViewSet(ModelViewSet):
    """Report source views for batch uploading report files."""

    http_method_names = ["get", "post", "head", "options"]
    queryset = ReportSource.objects.all().order_by("-created_at")
    serializer_class = ReportSourceSerializer
    permission_classes = [ReportFilePermissions, IsApprovedPermission]

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
