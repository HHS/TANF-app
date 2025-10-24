
from wsgiref.util import FileWrapper
from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from tdpservice.reports.models import ReportFile
from tdpservice.reports.serializers import ReportFileSerializer
from tdpservice.users.permissions import ReportFilePermissions


class ReportFileViewSet(ModelViewSet):
    """Report file views."""

    http_method_names = ["get", "post", "head"]
    queryset = ReportFile.objects.all().order_by("-created_at")
    serializer_class = ReportFileSerializer
    permission_classes = [ReportFilePermissions]

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

