"""Define API views for reports app."""

from wsgiref.util import FileWrapper
from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from tdpservice.reports.models import ReportFile
from tdpservice.reports.serializers import ReportFileSerializer, ReportIngestSerializer
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

    @action(methods=["post"], detail=False)
    def master(self, request, pk=None):
        """Admins can upload a master zips containing multiple zips."""
        serializer = ReportIngestSerializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)

        # creates a ReportIngest record and stores master zip to S3
        ingest = (
            serializer.save()
        )

        # TODO: implement celery task: process_master_zip.delay(ingest.id)

        return Response(
            ReportIngestSerializer(ingest).data, status=status.HTTP_202_ACCEPTED
        )

    @action(methods=["get"], detail=True)
    def download(self, request, pk=None):
        """Retrieve a file from s3 then stream it to the client."""
        obj = self.get_object()
        return FileResponse(FileWrapper(obj.file), filename=obj.original_filename)
