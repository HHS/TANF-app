"""ModelAdmin class for the ReparseMeta model."""
from tdpservice.data_files.admin.admin import DataFileInline

from .mixins import ReadOnlyAdminMixin


class ReparseMetaAdmin(ReadOnlyAdminMixin):
    """ModelAdmin class for parsed M1 data files."""

    inlines = [DataFileInline]

    def reparse_is_finished(self, instance):
        """Overload instance property for ui checkboxes."""
        return instance.is_finished

    reparse_is_finished.boolean = True

    def reparse_is_success(self, instance):
        """Overload instance property for ui checkboxes."""
        return instance.is_success

    reparse_is_success.boolean = True

    list_display = [
        "id",
        "created_at",
        "timeout_at",
        "reparse_is_finished",
        "reparse_is_success",
        "db_backup_location",
    ]

    list_filter = [
        "fiscal_year",
        "fiscal_quarter",
    ]

    readonly_fields = [
        "reparse_is_finished",
        "reparse_is_success",
        "finished_at",
        "num_files",
        "num_files_completed",
        "num_files_succeeded",
        "num_files_failed",
        "num_records_created",
    ]
