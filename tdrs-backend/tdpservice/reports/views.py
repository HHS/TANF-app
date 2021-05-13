"""Check if user is authorized."""
import logging

from rest_framework.parsers import MultiPartParser
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from tdpservice.reports.models import ReportFile
from tdpservice.reports.serializers import ReportFileSerializer
from tdpservice.users.permissions import CanUploadReport

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
        serializer = self.get_serializer(self.request.user, request.data)
