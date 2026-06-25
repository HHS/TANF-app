"""Check if user is authorized."""

import logging
from distutils.util import strtobool
from wsgiref.util import FileWrapper

from django.conf import settings
from django.db.models import Exists, OuterRef, Prefetch
from django.http import FileResponse, Http404, HttpResponse

from django_filters import rest_framework as filters
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from tdpservice.core.utils import get_feature_flag
from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.error_reports import ErrorReportFactory
from tdpservice.data_files.models import (
    DataFile,
    ReparseFileMeta,
    create_or_update_shadow_data_file,
)
from tdpservice.data_files.s3_client import S3Client
from tdpservice.data_files.serializers import DataFileSerializer
from tdpservice.data_files.submission_lifecycle import (
    complete_datafile_av_scan,
    transition_datafile,
)
from tdpservice.log_handler import S3FileHandler
from tdpservice.parsers.models import ParserError
from tdpservice.scheduling import parser_task
from tdpservice.scheduling.parser_task import set_error_report
from tdpservice.security.clients import ClamAVClient
from tdpservice.security.models import ClamAVFileScan
from tdpservice.users.permissions import DataFilePermissions, IsApprovedPermission

logger = logging.getLogger(__name__)


def get_log_file(request, remaining_path):
    """Get log file."""
    try:
        response = FileResponse(
            FileWrapper(S3FileHandler.download_file(key=remaining_path))
        )
        return HttpResponse(response, content_type="text/plain")
    except Exception as e:
        logger.error(f"Error retrieving log file: {e}")
        raise Http404("Log file not found.")


class DataFileFilter(filters.FilterSet):
    """Filters that can be applied to GET requests as query parameters."""

    # Override the generated definition for the STT field so we can require it.
    stt = filters.NumberFilter(field_name="stt_id", required=True)

    class Meta:
        """Class metadata linking to the DataFile and fields accepted."""

        model = DataFile
        fields = ["stt", "quarter", "year"]


class DataFileViewSet(ModelViewSet):
    """Data file views."""

    http_method_names = ["get", "post", "head"]
    filterset_class = DataFileFilter
    parser_classes = [MultiPartParser]
    permission_classes = [DataFilePermissions, IsApprovedPermission]
    serializer_class = DataFileSerializer
    pagination_class = None
    SSP_FILE_TYPE = "ssp-moe"
    PIA_FILE_TYPE = "program-integrity-audit"

    # TODO: Handle versioning in queryset
    # Ref: https://github.com/raft-tech/TANF-app/issues/1007
    queryset = (
        DataFile.objects.all()
        .select_related("stt", "user", "summary")
        .prefetch_related(
            Prefetch(
                "reparse_file_metas",
                queryset=ReparseFileMeta.objects.exclude(finished_at=None).order_by(
                    "-finished_at"
                ),
                to_attr="rfms",
            )
        )
        .annotate(
            has_error=Exists(
                ParserError.objects.filter(
                    file=OuterRef("pk"),
                    deprecated=False
                )
            )
        )
    )

    def _validate_pia_request(self, request):
        """Validate PIA feature flag/year range and return a failure response."""
        is_program_audit = False
        try:
            is_program_audit = strtobool(request.POST.get("is_program_audit", "false"))
        except ValueError:
            return Response(
                {"detail": "This file type is not supported."},
                status=HTTP_400_BAD_REQUEST,
            )

        if not is_program_audit:
            return None

        pia_feature_flag_enabled, pia_feature_flag_config = get_feature_flag(
            "program-integrity-audit"
        )

        if not pia_feature_flag_enabled:
            return Response(
                {"detail": "This file type is not supported."},
                status=HTTP_400_BAD_REQUEST,
            )

        pia_minYear = pia_feature_flag_config.get("minYear") or 2024
        pia_maxYear = pia_feature_flag_config.get("maxYear") or 2024
        year = int(request.data.get("year"))

        if year < pia_minYear or year > pia_maxYear:
            return Response(
                {
                    "detail": "This file was submitted for a reporting year not supported by this file type."
                },
                status=HTTP_400_BAD_REQUEST,
            )

        return None

    def _scan_uploaded_file(self, uploaded_file, user, data_file):
        """Run ClamAV before saving the uploaded file to persistent storage.

        Returns a ``(failure_response, scan_result)`` tuple. ``failure_response``
        is ``None`` when the file is clean (or scanning is disabled);,
        derived from the underlying :class:`ClamAVFileScan.Result` so that
        scanner ERRORs are not collapsed into INFECTED in lifecycle audit logs.
        """
        if not settings.CLAMAV_NEEDED or uploaded_file is None:
            return None, "clean"

        try:
            scan_result = ClamAVClient().scan_file(
                uploaded_file,
                uploaded_file.name,
                user,
                data_file=data_file,
            )
        except ClamAVClient.ServiceUnavailable:
            return (
                Response(
                    {
                        "detail": "Unable to complete security inspection, please try again or contact support for assistance"
                    },
                    status=HTTP_400_BAD_REQUEST,
                ),
                "error",
            )

        # Reset the stream because saving to storage will read the file again.
        uploaded_file.seek(0)

        if scan_result == ClamAVFileScan.Result.CLEAN:
            return None, "clean"

        if scan_result == ClamAVFileScan.Result.ERROR:
            return (
                Response(
                    {
                        "detail": "Unable to complete security inspection, please try again or contact support for assistance"
                    },
                    status=HTTP_400_BAD_REQUEST,
                ),
                "error",
            )

        return (
            Response(
                {
                    "detail": "Rejected: uploaded file did not pass security inspection"
                },
                status=HTTP_400_BAD_REQUEST,
            ),
            "infected",
        )

    def create(self, request, *args, **kwargs):
        """Create a DataFile and persist the file only after a successful AV scan."""
        logger.debug(f"{self.__class__.__name__}: {request}")

        pia_error = self._validate_pia_request(request)
        if pia_error is not None:
            return pia_error

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data.get("file")
        data_file = serializer.save(file=None)

        transition_datafile(
            data_file,
            SubmissionState.VIRUS_SCAN_STARTED,
            note="virus scan started",
        )

        scan_failure_response, scan_result = self._scan_uploaded_file(
            uploaded_file,
            request.user,
            data_file,
        )
        if scan_failure_response is not None:
            complete_datafile_av_scan(
                data_file,
                scan_result=scan_result,
                note=scan_failure_response.data["detail"],
            )
            if settings.GO_PARSER_SHADOW_MODE:
                create_or_update_shadow_data_file(data_file)
            return scan_failure_response

        complete_datafile_av_scan(
            data_file,
            scan_result=scan_result,
            note="file passed virus scan",
        )

        data_file.file = uploaded_file
        data_file.save()
        if settings.GO_PARSER_SHADOW_MODE:
            create_or_update_shadow_data_file(data_file)

        logger.info(
            f"Preparing parse task: User META -> user: {request.user}, stt: {data_file.stt}. "
            + f"Datafile META -> datafile: {data_file.id}, program type: {data_file.program_type}, "
            + f"section: {data_file.section}, "
            + f"quarter {data_file.quarter}, year {data_file.year}."
        )

        parser_task.queue_parse(data_file.id)
        logger.info("Submitted parse task to queue for datafile %s.", data_file.id)

        headers = self.get_success_headers(serializer.data)
        response = Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
        logger.debug(f"{self.__class__.__name__}: return val: {response}")
        return response

    def list(self, request, *args, **kwargs):
        """Override to handle the list request with url param validation."""
        queryset = self.get_queryset()

        file_type = self.request.query_params.get("file_type", None)

        if file_type == DataFileViewSet.SSP_FILE_TYPE:
            queryset = queryset.filter(program_type=DataFile.ProgramType.SSP)
        elif DataFile.Section.is_fra(file_type):
            queryset = queryset.filter(
                program_type=DataFile.ProgramType.FRA, section=file_type
            )
        else:
            pia_feature_flag_enabled, pia_feature_flag_config = get_feature_flag(
                "program-integrity-audit"
            )
            is_program_audit = file_type == DataFileViewSet.PIA_FILE_TYPE

            if is_program_audit and not pia_feature_flag_enabled:
                return Response(
                    {"detail": "This file type is not supported."},
                    status=HTTP_400_BAD_REQUEST,
                )
            elif is_program_audit:
                pia_minYear = pia_feature_flag_config.get("minYear") or 2024
                pia_maxYear = pia_feature_flag_config.get("maxYear") or 2024
                year = int(request.query_params.get("year"))

                if year < pia_minYear or year > pia_maxYear:
                    return Response(
                        {
                            "detail": "This request was submitted for a reporting year not supported by this file type."
                        },
                        status=HTTP_400_BAD_REQUEST,
                    )

            queryset = queryset.filter(
                program_type__in=[
                    DataFile.ProgramType.TANF,
                    DataFile.ProgramType.TRIBAL,
                ],
                is_program_audit=is_program_audit,
            )

        self.queryset = queryset
        response = super().list(request, *args, **kwargs)
        return response

    def get_queryset(self):
        """Apply custom queryset filters."""
        queryset = super().get_queryset().order_by("-created_at")
        return queryset

    def filter_queryset(self, queryset):
        """Only apply filters to the list action."""
        if self.action != "list":
            self.filterset_class = None

        return super().filter_queryset(queryset)

    def get_serializer_context(self):
        """Retrieve additional context required by serializer."""
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    @action(methods=["get"], detail=True)
    def download(self, request, pk=None):
        """Retrieve a file from s3 then stream it to the client."""
        record = self.get_object()
        response = None

        # If no versioning id, then download from django storage
        if not hasattr(record, "s3_versioning_id") or record.s3_versioning_id is None:
            response = FileResponse(
                FileWrapper(record.file), filename=record.original_filename
            )
        else:
            # If versioning id, then download from s3
            s3 = S3Client()
            file_path = record.file.name
            version_id = record.s3_versioning_id

            response = FileResponse(
                FileWrapper(
                    s3.file_download(file_path, record.original_filename, version_id)
                ),
                filename=record.original_filename,
            )
        return response

    @action(methods=["get"], detail=True)
    def download_error_report(self, request, pk=None):
        """Generate and return the parsing error report xlsx."""
        datafile = self.get_object()

        if not datafile.summary.error_report:
            error_report_generator = ErrorReportFactory.get_error_report_generator(
                datafile
            )
            error_report = error_report_generator.generate()
            set_error_report(datafile.summary, error_report)
            datafile = self.get_object()  # reload to get the newly added file

        return FileResponse(datafile.summary.error_report, "report.xlsx")


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
                name="stt",
                required=True,
                type="integer",
                in_="path",
                description=(
                    "The unique identifier of the target STT, if not specified "
                    "will default to user STT"
                ),
            )
        ]
    )
    def get(self, request, **kwargs):
        """Handle get action for get list of years there are data_files."""
        user = request.user
        is_ofa_admin = user.groups.filter(name="OFA Admin").exists()

        stt_id = kwargs.get("stt") if is_ofa_admin else user.stt.id
        if not stt_id:
            return Response(
                {"detail": "Must supply a valid STT"}, status=HTTP_400_BAD_REQUEST
            )

        available_years = (
            DataFile.objects.filter(stt=stt_id)
            .values_list("year", flat=True)
            .distinct()
        )
        return Response(list(available_years))
