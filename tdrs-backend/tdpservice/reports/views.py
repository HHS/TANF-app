"""Check if user is authorized."""
import logging

from django.http import StreamingHttpResponse
from django_filters import rest_framework as filters
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from wsgiref.util import FileWrapper

from tdpservice.reports.serializers import ReportFileSerializer
from tdpservice.reports.models import ReportFile
from tdpservice.users.permissions import ReportFilePermissions, is_in_group

logger = logging.getLogger()


class ReportFileFilter(filters.FilterSet):
    """Filters that can be applied to GET requests as query parameters."""
    stt = filters.NumberFilter(field_name='stt_id', required=True)

    class Meta:
        model = ReportFile
        fields = ['stt', 'quarter', 'year']


class ReportFileViewSet(ModelViewSet):
    """Report file views."""

    http_method_names = ['get', 'post', 'head']
    filterset_class = ReportFileFilter
    parser_classes = [MultiPartParser]
    permission_classes = [ReportFilePermissions]
    serializer_class = ReportFileSerializer

    # TODO: Handle versioning in queryset
    # Ref: https://github.com/raft-tech/TANF-app/issues/1007
    queryset = ReportFile.objects.all()

    # NOTE: This is a temporary hack to make sure the latest version of the file
    # is the one presented in the UI. Once we implement the above linked issue
    # we will be able to appropriately refer to the latest versions only.
    ordering = ['-version']

    def filter_queryset(self, queryset):
        """Only apply filters to the list action."""
        if self.action != 'list':
            self.filterset_class = None
        return super().filter_queryset(queryset)

    @action(methods=["get"], detail=True)
    def download(self, request, pk=None):
        """Retrieve a file from s3 then stream it to the client."""
        record = self.get_object()

        response = StreamingHttpResponse(
            FileWrapper(record.file),
            content_type='txt/plain'
        )
        file_name = record.original_filename
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class GetYearList(APIView):
    """Get list of years for which there are reports."""

    query_string = False
    pattern_name = "report-list"
    permission_classes = [ReportFilePermissions]

    def get(self, request, **kwargs):
        """Handle get action for get list of years there are reports."""
        user = request.user
        is_ofa_admin = user.groups.filter(name="OFA Admin").exists()

        stt_id = kwargs.get('stt') if is_ofa_admin else user.stt.id
        if not stt_id:
            return Response(
                {'detail': 'Must supply a valid STT'},
                status=HTTP_400_BAD_REQUEST
            )

        available_years = ReportFile.objects.filter(
            stt=stt_id
        ).values_list('year', flat=True).distinct()
        return Response(list(available_years))
