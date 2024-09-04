"""Admin class for DataFile objects."""
from django.contrib import admin
from tdpservice.core.utils import ReadOnlyAdminMixin
# from tdpservice.core.filters import custom_filter_title
from tdpservice.data_files.models import DataFile, LegacyFileTransfer
from tdpservice.parsers.models import DataFileSummary, ParserError
from tdpservice.data_files.admin.filters import DataFileSummaryPrgTypeFilter, LatestReparseEvent, VersionFilter
from django.conf import settings
from django.utils.html import format_html

DOMAIN = settings.FRONTEND_BASE_URL


class DataFileInline(admin.TabularInline):
    """Inline model for many to many relationship."""

    model = DataFile.reparse_meta_models.through
    can_delete = False
    ordering = ["-pk"]

    def has_change_permission(self, request, obj=None):
        """Read only permissions."""
        return False


@admin.register(DataFile)
class DataFileAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin class for DataFile models."""

    def status(self, obj):
        """Return the status of the data file summary."""
        return DataFileSummary.objects.get(datafile=obj).status

    def case_totals(self, obj):
        """Return the case totals."""
        return DataFileSummary.objects.get(datafile=obj).case_aggregates

    def error_report_link(self, obj):
        """Return the link to the error report."""
        pe_len = ParserError.objects.filter(file=obj).count()

        filtered_parserror_list_url = f'{DOMAIN}/admin/parsers/parsererror/?file=' + str(obj.id)
        # have to find the error id from obj
        return format_html("<a href='{url}'>{field}</a>",
                           field="Parser Errors: " + str(pe_len),
                           url=filtered_parserror_list_url)

    error_report_link.allow_tags = True

    def data_file_summary(self, obj):
        """Return the data file summary."""
        df = DataFileSummary.objects.get(datafile=obj)
        return format_html("<a href='{url}'>{field}</a>",
                           field=f'{df.id}' + ":" + df.get_status(),
                           url=f"{DOMAIN}/admin/parsers/datafilesummary/{df.id}/change/")

    inlines = [DataFileInline]

    list_display = [
        'id',
        'stt',
        'year',
        'quarter',
        'section',
        'version',
        'data_file_summary',
        'error_report_link',
    ]

    list_filter = [
        'quarter',
        'section',
        'stt',
        'user',
        'year',
        'version',
        'summary__status',
        DataFileSummaryPrgTypeFilter,
        LatestReparseEvent,
        VersionFilter,
    ]

@admin.register(LegacyFileTransfer)
class LegacyFileTransferAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin class for LegacyFileTransfer models."""

    list_display = [
        'id',
        'sent_at',
        'result',
        'uploaded_by',
        'file_name',
        'file_shasum',
    ]

    list_filter = [
        'sent_at',
        'result',
        'uploaded_by',
        'file_name',
        'file_shasum',
    ]
