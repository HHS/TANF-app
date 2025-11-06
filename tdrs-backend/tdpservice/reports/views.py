"""Define API views for reports app."""

from wsgiref.util import FileWrapper
from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
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

    def get_serializer_class(self):
        """Retrieve additional context required by serializer."""
        if getattr(self, "action", None) == "report_source":
            return ReportSourceSerializer
        return super().get_serializer_class()

    @action(methods=["get", "post"], detail=False)
    def report_source(self, request, pk=None):
        """Admins can upload report source zips containing multiple zips."""
        if request.method.lower() == "get":
            sources = ReportSource.objects.all().order_by("-created_at")
            serializer = self.get_serializer(sources, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)

        # creates a ReportSource record and stores report source zip to S3
        source = serializer.save()

        # Process the report source zip file
        process_report_source.delay(source.id)

        return Response(
            ReportSourceSerializer(source).data,
            status=status.HTTP_202_ACCEPTED
        )

    @action(methods=["get"], detail=True)
    def download(self, request, pk=None):
        """Retrieve a file from s3 then stream it to the client."""
        obj = self.get_object()
        return FileResponse(FileWrapper(obj.file), filename=obj.original_filename)
