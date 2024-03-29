"""Mixin classes supproting custom functionality."""

from django.http import HttpResponse
import csv

class ExportCsvMixin:
    """Mixin class to support CSV exporting."""

    def export_as_csv(self, request, queryset):
        """Convert queryset to CSV."""
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected as CSV"


class SttCodeMixin:
    """Mixin class to display a record's associated stt code."""

    def stt_code(self, obj):
        """Return stt code."""
        return obj.datafile.stt.stt_code