"""Mixin classes supproting custom functionality."""

from django.http import StreamingHttpResponse
import csv


class ExportCsvMixin:
    """Mixin class to support CSV exporting."""

    class Echo:
        """An object that implements just the write method of the file-like
        interface.
        """

        def write(self, value):
            """Write the value by returning it, instead of storing in a buffer."""
            return value

    def export_as_csv(self, request, queryset):
        """Convert queryset to CSV."""
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        pseudo_buffer = ExportCsvMixin.Echo()

        writer = csv.writer(pseudo_buffer)
        writer.writerow(field_names)

        return StreamingHttpResponse(
            (writer.writerow([getattr(obj, field) for field in field_names]) for obj in queryset),
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{meta}.csv"'},
        )

    export_as_csv.short_description = "Export Selected as CSV"


class SttCodeMixin:
    """Mixin class to display a record's associated stt code."""

    def stt_code(self, obj):
        """Return stt code."""
        return obj.datafile.stt.stt_code
