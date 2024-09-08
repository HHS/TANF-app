"""Admin class for DataFile objects."""
from django.contrib import admin
from tdpservice.core.utils import ReadOnlyAdminMixin
from tdpservice.data_files.models import DataFile, LegacyFileTransfer
from tdpservice.parsers.models import DataFileSummary, ParserError
from tdpservice.data_files.admin.filters import DataFileSummaryPrgTypeFilter, LatestReparseEvent
from django.conf import settings
from django.utils.html import format_html
from datetime import datetime, timedelta, timezone

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

    class SubmissionDateFilter(admin.SimpleListFilter):
        """filter data files by month."""

        title = 'submission date'
        parameter_name = 'Submission Day/Month/Year'

        def lookups(self, request, model_admin):
            """Return a list of tuples."""
            return [
                ('0', 'Today'),
                ('1', 'Yesterday'),
                ('7', 'Past 7 days'),
                ('30', 'This month'),
                ('365', 'This year'),
            ]

        def queryset(self, request, queryset):
            """Return a queryset."""
            if self.value() == '1':
                yesterday = (datetime.now(tz=timezone.utc) - timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                    )
                query_set_ids = [df.id for df in queryset if df.created_at.replace(
                    hour=0, minute=0, second=0, microsecond=0
                    ) == yesterday]
                return queryset.filter(id__in=query_set_ids)
            elif self.value() in ['0', '7']:
                last_week_today = datetime.now(tz=timezone.utc) - timedelta(days=int(self.value()))
                last_week_today = last_week_today.replace(hour=0, minute=0, second=0, microsecond=0)
                query_set_ids = [df.id for df in queryset if df.created_at >= last_week_today]
                return queryset.filter(id__in=query_set_ids)
            elif self.value() == '30':
                this_month = datetime.now(tz=timezone.utc).replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0)
                query_set_ids = [df.id for df in queryset if df.created_at >= this_month]
                return queryset.filter(id__in=query_set_ids)
            elif self.value() == '365':
                this_year = datetime.now(tz=timezone.utc).replace(
                    month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                query_set_ids = [df.id for df in queryset if df.created_at >= this_year]
                return queryset.filter(id__in=query_set_ids)
            else:
                return queryset

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
        SubmissionDateFilter,
        'version',
        'summary__status',
        DataFileSummaryPrgTypeFilter,
        LatestReparseEvent
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
