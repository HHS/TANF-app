"""Mixin classes supproting custom functionality."""
from datetime import datetime
from django.contrib import admin
from tdpservice.search_indexes.tasks import export_queryset_to_s3_csv
from tdpservice.core.utils import log
from tdpservice.users.models import User

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

        system_user, _ = User.objects.get_or_create(username='system')
        log(
            f'Beginning export of {queryset.count()} {meta.model_name} objects to s3: {file_path}',
            {'user_id': system_user.pk, 'object_id': None, 'object_repr': ''}
        )

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
