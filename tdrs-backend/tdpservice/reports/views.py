"""Check if user is authorized."""
import logging

from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from tdpservice.reports.models import ReportFile
from tdpservice.reports.serializers import ReportFileSerializer
from tdpservice.users.permissions import CanDownloadReport, CanUploadReport

logger = logging.getLogger()


class ReportFileViewSet(ModelViewSet):
    """Report file views."""

    http_method_names = ['get', 'post', 'head']
    parser_classes = [MultiPartParser]
    permission_classes = [CanUploadReport]
    serializer_class = ReportFileSerializer
    queryset = ReportFile.objects.all()


class GetYearList(APIView):
    """Get list of years for which there are reports."""

    query_string = False
    pattern_name = "report-list"
    permission_classes = [CanDownloadReport]

    def get(self, request, **kargs):
        """Handle get action for get list of years there are reports."""
        user = request.user
        is_ofa_admin = user.groups.filter(name="OFA Admin").exists()

        stt_id = kargs.get('stt') if is_ofa_admin else user.stt.id

        available_years = ReportFile.objects.filter(
            stt=stt_id
        ).values_list('year', flat=True).distinct()
        return Response(list(available_years))
