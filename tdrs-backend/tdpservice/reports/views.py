"""Check if user is authorized."""
import logging

from rest_framework.mixins import CreateModelMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.viewsets import GenericViewSet

from ..users.permissions import CanUploadReport
from .models import User
from .serializers import ReportFileSerializer

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ReportFileViewSet(CreateModelMixin, GenericViewSet):
    """Report file views."""

    parser_classes = [MultiPartParser]
    permission_classes = [CanUploadReport]
    serializer_class = ReportFileSerializer
    queryset = User.objects.select_related("stt")
