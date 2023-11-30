"""Admin class for DataFile objects."""
from django.contrib import admin

from ..core.utils import ReadOnlyAdminMixin
from .models import DataFile, LegacyFileTransfer
from tdpservice.parsers.models import DataFileSummary, ParserError
from django.conf import settings
from django.utils.html import format_html

DOMAIN = settings.FRONTEND_BASE_URL

class DataFileSummaryPrgTypeFilter(admin.SimpleListFilter):
    """Admin class filter for Program Type on datafile model."""

    title = 'Program Type'
    parameter_name = 'program_type'

    def lookups(self, request, model_admin):
        """Return a list of tuples."""
        return [
            ('TAN', 'TAN'),
            ('SSP', 'SSP'),
        ]

    def queryset(self, request, queryset):
        """Return a queryset."""
        if self.value():
            query_set_ids = [df.id for df in queryset if df.prog_type == self.value()]
            return queryset.filter(id__in=query_set_ids)
        else:
            return queryset

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
        DataFileSummaryPrgTypeFilter
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
