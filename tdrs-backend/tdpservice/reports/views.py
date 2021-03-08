"""Check if user is authorized."""
import logging

from rest_framework import mixins, viewsets

from ..users.permissions import CanUploadReport
from .models import User
from .serializers import ReportFileSerializer

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class ReportFileViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet,
):
    """Report file views."""

    queryset = User.objects.select_related("stt")

    def get_permissions(self):
        """Get permissions for the viewset."""
        permission_classes = {"create": [CanUploadReport]}.get(self.action)
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return the serializer class."""
        return {"create": ReportFileSerializer, }.get(self.action, ReportFileSerializer)
