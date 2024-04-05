"""Mixin classes supproting custom functionality."""
from django.contrib import admin
from django.http import StreamingHttpResponse
import csv


class ExportCsvMixin:
    """Mixin class to support CSV exporting."""

    class Echo:
        """An object that implements just the write method of the file-like interface."""

        def write(self, value):
            """Write the value by returning it, instead of storing in a buffer."""
            return value

    class RowIterator:
        """Iterator class to support custom CSV row generation."""

        def __init__(self, field_names, queryset):
            self.field_names = field_names
            self.queryset = queryset
            self.writer = csv.writer(ExportCsvMixin.Echo())
            self.is_header_row = True
            self.header_row = self.__init_header_row(field_names)

        def __init_header_row(self, field_names):
            """Generate custom header row."""
            header_row = []
            for name in field_names:
                header_row.append(name)
                if name == "datafile":
                    header_row.append("STT")
            return header_row

        def __iter__(self):
            """Yield the next row in the csv export."""
            for obj in self.queryset:
                row = []

                if self.is_header_row:
                    self.is_header_row = False
                    yield self.writer.writerow(self.header_row)

                for field_name in self.field_names:
                    field = getattr(obj, field_name)
                    row.append(field)
                    if field_name == "datafile":
                        row.append(field.stt.stt_code)
                yield self.writer.writerow(row)

    def export_as_csv(self, request, queryset):
        """Convert queryset to CSV."""
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        iterator = ExportCsvMixin.RowIterator(field_names, queryset)

        return StreamingHttpResponse(
            iterator,
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{meta}.csv"'},
        )

    export_as_csv.short_description = "Export Selected as CSV"


class SttCodeMixin:
    """Mixin class to display a record's associated stt code."""

    def stt_code(self, obj):
        """Return stt code."""
        return obj.datafile.stt.stt_code


class AdminModelMixin(admin.ModelAdmin):
    """Base class for all mixin classes needing to modify ModelAdmin methods. Needed to satisfy Python MRO."""

    pass

class CsvExportAdminMixin(AdminModelMixin, ExportCsvMixin, SttCodeMixin):
    """Class to encapsulate CSV related mixins."""
    actions = ["export_as_csv"]
    ordering = ['datafile__stt__stt_code']


class ReadOnlyAdminMixin(AdminModelMixin):
    """Force ModelAdmin to be READ only."""

    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        """Force all fields to read only."""
        return list(self.readonly_fields) + [field.name for field in obj._meta.fields] +\
            [field.name for field in obj._meta.many_to_many]

    def has_add_permission(self, request):
        """Deny add permisison."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Deny delete permission."""
        return False
