"""Check if user is authorized."""

import logging
from django.http import FileResponse
from django_filters import rest_framework as filters
from django.conf import settings
from django.contrib.auth.models import Group
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from wsgiref.util import FileWrapper
from rest_framework import status

from tdpservice.users.models import AccountApprovalStatusChoices, User
from tdpservice.data_files.serializers import DataFileSerializer
from tdpservice.data_files.models import DataFile, get_s3_upload_path
from tdpservice.users.permissions import DataFilePermissions
from tdpservice.scheduling import sftp_task, parser_task
from tdpservice.email.helpers.data_file import send_data_submitted_email
from tdpservice.data_files.s3_client import S3Client

logger = logging.getLogger(__name__)

class DataFileFilter(filters.FilterSet):
    """Filters that can be applied to GET requests as query parameters."""

    # Override the generated definition for the STT field so we can require it.
    stt = filters.NumberFilter(field_name='stt_id', required=True)

    class Meta:
        """Class metadata linking to the DataFile and fields accepted."""

        model = DataFile
        fields = ['stt', 'quarter', 'year']


class DataFileViewSet(ModelViewSet):
    """Data file views."""

    http_method_names = ['get', 'post', 'head']
    filterset_class = DataFileFilter
    parser_classes = [MultiPartParser]
    permission_classes = [DataFilePermissions]
    serializer_class = DataFileSerializer
    pagination_class = None

    # TODO: Handle versioning in queryset
    # Ref: https://github.com/raft-tech/TANF-app/issues/1007
    queryset = DataFile.objects.all()

    def create(self, request, *args, **kwargs):
        """Override create to upload in case of successful scan."""
        response = super().create(request, *args, **kwargs)

        # only if file is passed the virus scan and created successfully will we perform side-effects:
        # * Send to parsing
        # * Upload to ACF-TITAN
        # * Send email to user

        if response.status_code == status.HTTP_201_CREATED or response.status_code == status.HTTP_200_OK:
            user = request.user
            data_file_id = response.data.get('id')
            data_file = DataFile.objects.get(id=data_file_id)

            parser_task.parse.delay(data_file_id)
            logger.info("Submitted parse task to queue for datafile %s.", data_file_id)

            sftp_task.upload.delay(
                data_file_pk=data_file_id,
                server_address=settings.ACFTITAN_SERVER_ADDRESS,
                local_key=settings.ACFTITAN_LOCAL_KEY,
                username=settings.ACFTITAN_USERNAME,
                port=22
            )
            logger.info("Submitted upload task to redis for datafile %s.", data_file_id)

            app_name = settings.APP_NAME + '/'
            key = app_name + get_s3_upload_path(data_file, '')
            version_id = self.get_s3_versioning_id(response.data.get('original_filename'), key)

            data_file.s3_versioning_id = version_id
            data_file.save(update_fields=['s3_versioning_id'])

            # Send email to user to notify them of the file upload status
            subject = f"Data Submitted for {data_file.section}"
            email_context = {
                'stt_name': str(data_file.stt),
                'submission_date': data_file.created_at,
                'submitted_by': user.get_full_name(),
                'fiscal_year': data_file.fiscal_year,
                'section_name': data_file.section,
                'subject': subject,
            }

            recipients = User.objects.filter(
                stt=data_file.stt,
                account_approval_status=AccountApprovalStatusChoices.APPROVED,
                groups=Group.objects.get(name='Data Analyst')
            ).values_list('username', flat=True).distinct()

            if len(recipients) > 0:
                send_data_submitted_email(list(recipients), data_file, email_context, subject)

        return response

    def get_s3_versioning_id(self, file_name, prefix):
        """Get the version id of the file uploaded to S3."""
        s3 = S3Client()
        bucket_name = settings.AWS_S3_DATAFILES_BUCKET_NAME
        versions = s3.client.list_object_versions(Bucket=bucket_name, Prefix=prefix)
        for version in versions['Versions']:
            file_path = version['Key']
            if file_name in file_path:
                if version['IsLatest'] and version['VersionId'] != 'null':
                    return (version['VersionId'])
        return None

    def get_queryset(self):
        """Apply custom queryset filters."""
        queryset = super().get_queryset().order_by('-created_at')

        if self.request.query_params.get('file_type') == 'ssp-moe':
            queryset = queryset.filter(section__contains='SSP')
        else:
            queryset = queryset.exclude(section__contains='SSP')

        return queryset

    def filter_queryset(self, queryset):
        """Only apply filters to the list action."""
        if self.action != 'list':
            self.filterset_class = None

        return super().filter_queryset(queryset)

    def get_serializer_context(self):
        """Retrieve additional context required by serializer."""
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    @action(methods=["get"], detail=True)
    def download(self, request, pk=None):
        """Retrieve a file from s3 then stream it to the client."""
        record = self.get_object()
        response = None

        # If no versioning id, then download from django storage
        if not hasattr(record, 's3_versioning_id') or record.s3_versioning_id is None:
            response = FileResponse(
                FileWrapper(record.file),
                filename=record.original_filename
            )
        else:
            # If versioning id, then download from s3
            s3 = S3Client()
            file_path = record.file.name
            version_id = record.s3_versioning_id

            response = FileResponse(
                FileWrapper(s3.file_download(file_path, record.original_filename, version_id)),
                filename=record.original_filename
            )
        return response


class GetYearList(APIView):
    """Get list of years for which there are data_files."""

    query_string = False
    pattern_name = "data_file-list"
    permission_classes = [DataFilePermissions]

    # The DataFilePermissions subclasses DjangoModelPermissions which requires
    # declaration of a queryset in order to perform introspection to determine
    # Permissions needed. This is otherwise unused.
    queryset = DataFile.objects.none()

    @swagger_auto_schema(
        manual_parameters=[
            Parameter(
                name='stt',
                required=True,
                type='integer',
                in_='path',
                description=(
                    'The unique identifier of the target STT, if not specified '
                    'will default to user STT'
                ),
            )
        ]
    )
    def get(self, request, **kwargs):
        """Handle get action for get list of years there are data_files."""
        user = request.user
        is_ofa_admin = user.groups.filter(name="OFA Admin").exists()

        stt_id = kwargs.get('stt') if is_ofa_admin else user.stt.id
        if not stt_id:
            return Response(
                {'detail': 'Must supply a valid STT'},
                status=HTTP_400_BAD_REQUEST
            )

        available_years = DataFile.objects.filter(
            stt=stt_id
        ).values_list('year', flat=True).distinct()
        return Response(list(available_years))
