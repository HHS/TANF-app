"""Check if user is authorized."""
import logging

from rest_framework.parsers import MultiPartParser
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from tdpservice.reports.models import ReportFile
from tdpservice.reports.serializers import ReportFileSerializer, DownloadReportFileSerializer
from tdpservice.users.permissions import CanUploadReport

from django.http import StreamingHttpResponse

logger = logging.getLogger()


class ReportFileViewSet(ModelViewSet):
    """Report file views."""

    http_method_names = ['get', 'post', 'head']
    parser_classes = [MultiPartParser]
    permission_classes = [CanUploadReport]
    serializer_class = ReportFileSerializer
    queryset = ReportFile.objects.all()

    @action(methods=["get"], detail=True)
    def download(self, request, pk=None):
        """Retrieve a file from s3 then stream it to the client."""

        record = DownloadReportFileSerializer(id=pk)

        response = StreamingHttpResponse(streaming_content=record.file)
        response['Content-Disposition'] = f'attachement; filename="{record.file_name}"'
        return response
