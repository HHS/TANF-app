"""Mixin classes supproting custom functionality."""
from datetime import datetime
from django.contrib import admin
from ..tasks import export_queryset_to_s3_csv

class ExportCsvMixin:
    """Mixin class to support CSV exporting."""

    def export_as_csv(self, request, queryset):
        """Convert queryset to CSV."""
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        if queryset.exists():
            model = queryset.first()
            datafile_name = f"{meta}_FY{model.datafile.year}{model.datafile.quarter}_" +\
                str(datetime.now().strftime("%d%m%y-%H-%M-%S"))

        # https://stackoverflow.com/a/5359612
        # https://github.com/piskvorky/smart_open

        sql, params = queryset.query.sql_with_params()

        file_path = f'exports/{datafile_name}.csv.gz'

        export_queryset_to_s3_csv.delay(
            sql,
            params,
            field_names,
            meta.model_name,
            file_path,
        )

        self.message_user(request, f'Your s3 file url is: {file_path}')

    export_as_csv.short_description = "Export Selected as CSV"


class SttMixin:
    """Mixin class to display a record's associated stt code."""

    def stt_code(self, obj):
        """Return stt code."""
        return obj.datafile.stt.stt_code

    def stt_name(self, obj):
        """Return stt name."""
        return obj.datafile.stt.name


class AdminModelMixin(admin.ModelAdmin):
    """Base class for all mixin classes needing to modify ModelAdmin methods. Needed to satisfy Python MRO."""

    pass

class CsvExportAdminMixin(AdminModelMixin, ExportCsvMixin, SttMixin):
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
