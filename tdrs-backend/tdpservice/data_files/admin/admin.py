"""Admin class for DataFile objects."""

import logging
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.utils.html import format_html
from django.utils.translation import ngettext

from botocore.exceptions import ClientError

from tdpservice.core.utils import ReadOnlyAdminMixin
from tdpservice.data_files.admin.filters import LatestReparseEvent, VersionFilter
from tdpservice.data_files.models import DataFile, LegacyFileTransfer
from tdpservice.data_files.s3_client import S3Client
from tdpservice.data_files.tasks import reparse_files
from tdpservice.log_handler import S3FileHandler
from tdpservice.parsers.models import DataFileSummary, ParserError

logger = logging.getLogger(__name__)

DOMAIN = settings.FRONTEND_BASE_URL


class DataFileInline(admin.TabularInline):
    """Inline model for many to many relationship."""

    model = DataFile.reparses.through
    can_delete = False
    ordering = ["-pk"]

    def has_change_permission(self, request, obj=None):
        """Read only permissions."""
        return False


@admin.register(DataFile)
class DataFileAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin class for DataFile models."""

    class Media:
        """Media class for DataFileAdmin."""

        js = ("admin/js/admin/admin_datafile_model.js",)

    actions = ["reparse"]

    readonly_fields = ("versioned_file_download_link",)

    def versioned_file_download_link(self, obj):
        """Generate a custom download link for the file."""
        try:
            s3 = S3Client()
            version = obj.s3_versioning_id
            bucket = settings.AWS_S3_DATAFILES_BUCKET_NAME
            key = obj.s3_location
            app_name = settings.APP_NAME + "/"
            key = app_name + key

            url = s3.client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": bucket, "Key": key, "VersionId": version},
                ExpiresIn=3600,  # one hour in seconds, increase if needed
            )
            # url = url.replace("localstack", "localhost")
            return format_html("<a href='{0}'>{1}</a>", url, key)
        except (ClientError, KeyError, Exception) as e:
            # If the file is not available, return a placeholder
            logger.info(
                f"File version not available for DataFile ID: {obj.id}. Error: {e}"
            )
            return None

    versioned_file_download_link.short_description = (
        "File"  # Optional: Renames the field in the admin
    )

    exclude = ("file",)

    fieldsets = (
        (
            "Properties",
            {
                "fields": (
                    "created_at",
                    "quarter",
                    "year",
                    "section",
                    "program_type",
                    "is_program_audit",
                    "stt",
                    "version",
                ),
                "classes": ("wide", "extrapretty"),
            },
        ),
        (
            "File",
            {
                "fields": (
                    "versioned_file_download_link",
                    "s3_versioning_id",
                    "filename",
                ),
            },
        ),
        (
            "Logs",
            {
                "fields": ("log_file",),
            },
        ),
    )
    readonly_fields = ("year",)

    def get_fieldsets(self, request, obj):
        """Return the fieldsets."""
        field_sets = super().get_fieldsets(request, obj)

        # Remove the 'Logs' fieldset if the file doesn't exist
        datafile = obj
        if datafile:
            link = (
                f"{datafile.year}/{datafile.quarter}/"
                f"{datafile.stt}/{datafile.section}"
            )
            response = S3FileHandler.download_file(key=link)
            if response is not None:
                return field_sets
            else:
                # If the log file is not available, remove the field from the fieldsets
                for field_set in field_sets:
                    if field_set[0] == "Logs" and response is None:
                        field_sets_list = list(field_sets)
                        field_sets_list.remove(field_set)
                        return tuple(field_sets_list)
        return field_sets

    def get_queryset(self, request):
        """Return the queryset."""
        qs = super().get_queryset(request)
        # return data files based on user's section
        if not (request.user.has_fra_access or request.user.is_an_admin):
            filtered_for_fra = qs.exclude(section__in=DataFile.get_fra_section_list())
            return filtered_for_fra
        else:
            return qs

    def reparse(self, request, queryset):
        """Reparse the selected data files."""
        files = queryset.values_list("id", flat=True)
        reparse_files.delay(list(files))

        self.message_user(
            request,
            ngettext(
                "%d file successfully submitted for reparsing.",
                "%d files successfully submitted for reparsing.",
                files.count(),
            )
            % files.count(),
            messages.SUCCESS,
        )
        return redirect("/admin/search_indexes/reparsemeta/")

    def get_actions(self, request):
        """Return the actions."""
        actions = super().get_actions(request)
        if not request.user.groups.filter(
            name__in=["OFA System Admin", "OFA Admin"]
        ).exists():
            actions.pop("reparse", None)
        else:
            if "reparse" not in actions:
                actions["reparse"] = (
                    self.reparse,
                    "reparse",
                    "Reparse selected data files)",
                )
        return actions

    def status(self, obj):
        """Return the status of the data file summary."""
        return DataFileSummary.objects.get(datafile=obj).status

    def case_totals(self, obj):
        """Return the case totals."""
        return DataFileSummary.objects.get(datafile=obj).case_aggregates

    def error_report_link(self, obj):
        """Return the link to the error report."""
        pe_len = ParserError.objects.filter(file=obj).count()

        filtered_parserror_list_url = (
            f"{DOMAIN}/admin/parsers/parsererror/?file=" + str(obj.id)
        )
        # have to find the error id from obj
        return format_html(
            "<a href='{url}'>{field}</a>",
            field="Parser Errors: " + str(pe_len),
            url=filtered_parserror_list_url,
        )

    error_report_link.allow_tags = True

    def data_file_summary(self, obj):
        """Return the data file summary."""
        df = DataFileSummary.objects.get(datafile=obj)
        return format_html(
            "<a href='{url}'>{field}</a>",
            field=f"{df.id}" + ":" + df.get_status(),
            url=f"{DOMAIN}/admin/parsers/datafilesummary/{df.id}/change/",
        )

    class SubmissionDateFilter(admin.SimpleListFilter):
        """filter data files by month."""

        title = "submission date"
        parameter_name = "Submission Day/Month/Year"

        def lookups(self, request, model_admin):
            """Return a list of tuples."""
            return [
                ("0", "Today"),
                ("1", "Yesterday"),
                ("7", "Past 7 days"),
                ("30", "This month"),
                ("365", "This year"),
            ]

        def queryset(self, request, queryset):
            """Return a queryset."""
            if self.value() == "1":
                yesterday = (datetime.now(tz=timezone.utc) - timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                query_set_ids = [
                    df.id
                    for df in queryset
                    if df.created_at.replace(hour=0, minute=0, second=0, microsecond=0)
                    == yesterday
                ]
                return queryset.filter(id__in=query_set_ids)
            elif self.value() in ["0", "7"]:
                last_week_today = datetime.now(tz=timezone.utc) - timedelta(
                    days=int(self.value())
                )
                last_week_today = last_week_today.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                query_set_ids = [
                    df.id for df in queryset if df.created_at >= last_week_today
                ]
                return queryset.filter(id__in=query_set_ids)
            elif self.value() == "30":
                this_month = datetime.now(tz=timezone.utc).replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )
                query_set_ids = [
                    df.id for df in queryset if df.created_at >= this_month
                ]
                return queryset.filter(id__in=query_set_ids)
            elif self.value() == "365":
                this_year = datetime.now(tz=timezone.utc).replace(
                    month=1, day=1, hour=0, minute=0, second=0, microsecond=0
                )
                query_set_ids = [df.id for df in queryset if df.created_at >= this_year]
                return queryset.filter(id__in=query_set_ids)
            else:
                return queryset

    class FRA_AccessFilter(admin.SimpleListFilter):
        """Filter datafile based on user access to FRA files."""

        title = "FRA/Non FRA Files"
        parameter_name = "fra_access"

        def lookups(self, request, model_admin):
            """Return a list of tuples."""
            return [
                ("1", "FRA Datafile"),
                ("0", "Non FRA Datafile"),
            ]

        def queryset(self, request, queryset):
            """Return a queryset."""
            if self.value() == "1":
                return queryset.filter(section__in=DataFile.get_fra_section_list())
            elif self.value() == "0":
                return queryset.exclude(section__in=DataFile.get_fra_section_list())
            else:
                return queryset

    inlines = [DataFileInline]

    list_display = [
        "id",
        "stt",
        "year",
        "quarter",
        "program_type",
        "section",
        "version",
        "data_file_summary",
        "error_report_link",
    ]

    list_filter = [
        "stt",
        "year",
        "quarter",
        "program_type",
        "section",
        "summary__status",
        "stt__type",
        "stt__region",
        "user",
        SubmissionDateFilter,
        LatestReparseEvent,
        VersionFilter,
    ]

    def get_list_filter(self, request):
        """Get filter list in DataFile admin page."""
        list_filter = super().get_list_filter(request)
        user = request.user
        if (
            user.is_an_admin or user.has_fra_access
        ) and self.FRA_AccessFilter not in list_filter:
            list_filter.append(self.FRA_AccessFilter)
        elif not user.has_fra_access and self.FRA_AccessFilter in list_filter:
            list_filter.remove(self.FRA_AccessFilter)
        return list_filter


@admin.register(LegacyFileTransfer)
class LegacyFileTransferAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin class for LegacyFileTransfer models."""

    list_display = [
        "id",
        "sent_at",
        "result",
        "uploaded_by",
        "file_name",
        "file_shasum",
    ]

    list_filter = [
        "sent_at",
        "result",
        "uploaded_by",
        "file_name",
        "file_shasum",
    ]
