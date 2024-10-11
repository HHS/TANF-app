"""Meta data model for tracking reparsed files."""

from django.db import models
from django.db.models import Max
import logging

logger = logging.getLogger(__name__)


class ReparseMeta(models.Model):
    """
    Meta data model representing a single execution of `clean_and_reparse`.

    Because this model is intended to be queried in a distributed and parrallel fashion, all queries should rely on
    database level locking to ensure race conditions aren't introduced. See `increment_files_reparsed` for an example.
    """

    class Meta:
        """Meta class for the model."""

        verbose_name = "Reparse Meta Model"

    created_at = models.DateTimeField(auto_now_add=True)
    timeout_at = models.DateTimeField(auto_now_add=False, null=True)

    num_records_deleted = models.PositiveIntegerField(default=0)
    total_num_records_initial = models.PositiveBigIntegerField(default=0)
    total_num_records_post = models.PositiveBigIntegerField(default=0)

    db_backup_location = models.CharField(max_length=512)

    # Options used to select the files to reparse (from mgmt cmd only, remove if command deprecated)
    fiscal_quarter = models.CharField(max_length=2, null=True)
    fiscal_year = models.PositiveIntegerField(null=True)
    all = models.BooleanField(default=False)
    new_indices = models.BooleanField(default=False)
    delete_old_indices = models.BooleanField(default=False)

    @property
    def is_finished(self):
        """Return True if all associated ReparseFileMeta objects are finished."""
        if self.num_files > 0:
            return all([r.finished for r in self.reparse_file_metas.all()])
        return False

    @property
    def is_success(self):
        """Return True if all associated ReparseFileMeta objects are successful."""
        if self.is_finished:
            return all([r.success for r in self.reparse_file_metas.all()])
        return False

    @property
    def finished_at(self):
        """Return the finished_at timestamp of the last ReparseFileMeta object."""
        last_parse = self.reparse_file_metas.order_by('-finished_at').first()
        return last_parse.finished_at if last_parse else None

    @property
    def num_files(self):
        """Return the number of associated ReparseFileMeta objects."""
        return self.reparse_file_metas.count()

    @property
    def num_files_completed(self):
        """Return the number of completed ReparseFileMeta objects."""
        return self.reparse_file_metas.filter(finished=True).count()

    @property
    def num_files_succeeded(self):
        """Return the number of successful ReparseFileMeta objects."""
        return self.reparse_file_metas.filter(finished=True, success=True).count()

    @property
    def num_files_failed(self):
        """Return the number of failed ReparseFileMeta objects."""
        return self.reparse_file_metas.filter(finished=True, success=False).count()

    @property
    def num_records_created(self):
        """Return the sum of records created for all associated ReparseFileMeta objects."""
        return sum([r.num_records_created for r in self.reparse_file_metas.all()])

    # remove unused statics or change to utils funcs in own app and/or make new cleanup ticket for future

    @staticmethod
    def file_counts_match(meta_model):
        """
        Check whether the file counts match.

        This function assumes the meta_model has been passed in a distributed/thread safe way. If the database row
        containing this model has not been locked the caller will experience race issues.
        """
        print("\n\nINSIDE FILE COUNTS MATCH:")
        print(f"{meta_model.num_files }, {meta_model.num_files_completed}, {meta_model.num_files_failed}\n\n")
        return (meta_model.num_files_completed == meta_model.num_files or
                meta_model.num_files_completed + meta_model.num_files_failed ==
                meta_model.num_files or meta_model.num_files_failed == meta_model.num_files)

    @staticmethod
    def assert_all_files_done(meta_model):
        """
        Check if all files have been parsed with or without exceptions.

        This function assumes the meta_model has been passed in a distributed/thread safe way. If the database row
        containing this model has not been locked the caller will experience race issues.
        """
        if meta_model.is_finished and ReparseMeta.file_counts_match(meta_model):
            return True
        return False

    @staticmethod
    def get_latest():
        """Get the ReparseMeta model with the greatest pk."""
        max_pk = ReparseMeta.objects.all().aggregate(Max('pk'))
        if max_pk.get("pk__max", None) is None:
            return None
        return ReparseMeta.objects.get(pk=max_pk["pk__max"])
