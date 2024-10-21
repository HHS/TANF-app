"""Check if user is authorized."""
import logging
from django.db.models import Q
from django.http import FileResponse
from django_filters import rest_framework as filters
from django.conf import settings
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

from tdpservice.data_files.serializers import DataFileSerializer
from tdpservice.data_files.util import get_xls_serialized_file
from tdpservice.data_files.models import DataFile, get_s3_upload_path
from tdpservice.users.permissions import DataFilePermissions, IsApprovedPermission
from tdpservice.scheduling import parser_task
from tdpservice.data_files.s3_client import S3Client
from tdpservice.parsers.models import ParserError, ParserErrorCategoryChoices

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
    permission_classes = [DataFilePermissions, IsApprovedPermission]
    serializer_class = DataFileSerializer
    pagination_class = None

    # TODO: Handle versioning in queryset
    # Ref: https://github.com/raft-tech/TANF-app/issues/1007
    queryset = DataFile.objects.all()

    def create(self, request, *args, **kwargs):
        """Override create to upload in case of successful scan."""
        logger.debug(f"{self.__class__.__name__}: {request}")
        response = super().create(request, *args, **kwargs)

        # only if file is passed the virus scan and created successfully will we perform side-effects:
        # * Send to parsing
        # * Send email to user

        logger.debug(f"{self.__class__.__name__}: status: {response.status_code}")
        if response.status_code == status.HTTP_201_CREATED or response.status_code == status.HTTP_200_OK:
            data_file_id = response.data.get('id')
            data_file = DataFile.objects.get(id=data_file_id)

            logger.info(f"Preparing parse task: User META -> user: {request.user}, stt: {data_file.stt}. " +
                        f"Datafile META -> datafile: {data_file_id}, section: {data_file.section}, " +
                        f"quarter {data_file.quarter}, year {data_file.year}.")

            parser_task.parse.delay(data_file_id)
            logger.info("Submitted parse task to queue for datafile %s.", data_file_id)

            app_name = settings.APP_NAME + '/'
            key = app_name + get_s3_upload_path(data_file, '')
            version_id = self.get_s3_versioning_id(response.data.get('original_filename'), key)

            data_file.s3_versioning_id = version_id
            data_file.save(update_fields=['s3_versioning_id'])

        logger.debug(f"{self.__class__.__name__}: return val: {response}")
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
        if self.action == 'list':
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

    @action(methods=["get"], detail=True)
    def download_error_report(self, request, pk=None):
        """Generate and return the parsing error report xlsx."""
        datafile = self.get_object()
        all_errors = ParserError.objects.filter(file=datafile)
        filtered_errors = None
        user = self.request.user
        is_active = "Active" in datafile.section
        is_closed = "Closed" in datafile.section

        # We only filter Active and Closed submissions. Aggregate and Stratum return all errors.
        if not (user.is_ofa_sys_admin or user.is_ofa_admin) and (is_active or is_closed):
            # All cat1/4 errors
            error_type_query = Q(error_type=ParserErrorCategoryChoices.PRE_CHECK) | \
                Q(error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY)
            filtered_errors = all_errors.filter(error_type_query)

            # All cat2 errors associated with FAMILY_AFFILIATION and (CITIZENSHIP_STATUS or CLOSURE_REASON)
            second_field = "CITIZENSHIP_STATUS" if is_active else "CLOSURE_REASON"
            field_query = Q(field_name="FAMILY_AFFILIATION") | Q(field_name=second_field)
            filtered_errors = filtered_errors.union(all_errors.filter(
                field_query,
                error_type=ParserErrorCategoryChoices.FIELD_VALUE
                ))

            # All cat3 errors associated with FAMILY_AFFILIATION and SSN
            filtered_errors = filtered_errors.union(all_errors.filter(fields_json__friendly_name__has_keys=[
                "FAMILY_AFFILIATION",
                "SSN"
                ],
                error_type=ParserErrorCategoryChoices.VALUE_CONSISTENCY))

            # All cat3 errors associated with FAMILY_AFFILIATION and CITIZENSHIP_STATUS
            filtered_errors = filtered_errors.union(all_errors.filter(fields_json__friendly_name__has_keys=[
                "FAMILY_AFFILIATION",
                "CITIZENSHIP_STATUS"
                ],
                error_type=ParserErrorCategoryChoices.VALUE_CONSISTENCY))

            if is_active:
                # All cat3 errors associated with summed fields: AMT_FOOD_STAMP_ASSISTANCE, AMT_SUB_CC, CASH_AMOUNT,
                # CC_AMOUNT, TRANSP_AMOUNT
                filtered_errors = filtered_errors.union(all_errors.filter(fields_json__friendly_name__has_keys=[
                    "AMT_FOOD_STAMP_ASSISTANCE", "AMT_SUB_CC", "CASH_AMOUNT", "CC_AMOUNT", "TRANSP_AMOUNT"
                    ],
                    error_type=ParserErrorCategoryChoices.VALUE_CONSISTENCY))

                # All cat3 errors associated with FAMILY_AFFILIATION and SSN and CITIZENSHIP_STATUS
                filtered_errors = filtered_errors.union(all_errors.filter(fields_json__friendly_name__has_keys=[
                    "FAMILY_AFFILIATION",
                    "SSN",
                    "CITIZENSHIP_STATUS"
                    ],
                    error_type=ParserErrorCategoryChoices.VALUE_CONSISTENCY))

                # All cat3 errors associated with FAMILY_AFFILIATION and PARENT_MINOR_CHILD
                filtered_errors = filtered_errors.union(all_errors.filter(fields_json__friendly_name__has_keys=[
                    "FAMILY_AFFILIATION",
                    "PARENT_MINOR_CHILD",
                    ],
                    error_type=ParserErrorCategoryChoices.VALUE_CONSISTENCY))

                # All cat3 errors associated with FAMILY_AFFILIATION and EDUCATION_LEVEL
                filtered_errors = filtered_errors.union(all_errors.filter(fields_json__friendly_name__has_keys=[
                    "FAMILY_AFFILIATION",
                    "EDUCATION_LEVEL",
                    ],
                    error_type=ParserErrorCategoryChoices.VALUE_CONSISTENCY))

                # All cat3 errors associated with FAMILY_AFFILIATION and WORK_ELIGIBLE_INDICATOR
                filtered_errors = filtered_errors.union(all_errors.filter(fields_json__friendly_name__has_keys=[
                    "FAMILY_AFFILIATION",
                    "WORK_ELIGIBLE_INDICATOR",
                    ],
                    error_type=ParserErrorCategoryChoices.VALUE_CONSISTENCY))

                # All cat3 errors associated with CITIZENSHIP_STATUS and WORK_ELIGIBLE_INDICATOR
                filtered_errors = filtered_errors.union(all_errors.filter(fields_json__friendly_name__has_keys=[
                    "CITIZENSHIP_STATUS",
                    "WORK_ELIGIBLE_INDICATOR",
                    ],
                    error_type=ParserErrorCategoryChoices.VALUE_CONSISTENCY))
        else:
            filtered_errors = all_errors

        filtered_errors.order_by('pk')
        return Response(get_xls_serialized_file(filtered_errors))


class GetYearList(APIView):
    """Get list of years for which there are data_files."""

    query_string = False
    pattern_name = "data_file-list"
    permission_classes = [DataFilePermissions, IsApprovedPermission]

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
