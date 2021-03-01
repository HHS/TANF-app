"""Check if user is authorized."""
import logging

from rest_framework import mixins, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from ..users.permissions import CanDownloadReport, CanUploadReport

from .models import User, ReportFile
from .serializers import ReportFileSerializer

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def to_space_case(snake_str):
    """Create a string of space seperated tokens from a one with _ seperated."""
    return "".join(x.title() + " " for x in snake_str.split("_")).strip()


class GetReport(APIView):
    """Get latest version of specified report file."""

    query_string = False
    pattern_name = "report"
    permission_classes = [CanDownloadReport]

    def get(self, request, year, quarter, section, stt=None):
        """Handle get action for get report route."""
        latest = ReportFile.find_latest_version(
            year=year,
            quarter=quarter,
            section=to_space_case(section),
            stt=stt or request.user.stt.id,
        )
        serializer = ReportFileSerializer(latest)
        data = serializer.data
        return Response(data, template_name="report.json")
class GetList(APIView):
    """Get list of years for which there are reports."""

    query_string = False
    pattern_name = "report-list"
    permission_classes = [CanDownloadReport]

    def get(self, request, stt):
        """Handle get action for get list of years there are reports."""
        available_years = ReportFile.objects.filter(
            stt=stt
        ).values_list('year', flat=True).distinct()
        return Response(list(available_years))


class ReportFileViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet,
):
    """Report file views."""

    queryset = User.objects.select_related("stt")

    def get_permissions(self):
        """Get permissions for the viewset."""
        permission_classes = {
            "create": [CanUploadReport],
        }.get(self.action)
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return the serializer class."""
        return {
            "create": ReportFileSerializer,
        }.get(self.action, ReportFileSerializer)
