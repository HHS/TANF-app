"""Meta data model for tracking reparsed files."""

from django.db import models, transaction
from django.db.utils import DatabaseError
from django.db.models import Max
from tdpservice.search_indexes.util import count_all_records
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

    finished = models.BooleanField(default=False)
    success = models.BooleanField(default=False, help_text="All files completed parsing.")

    num_files_to_reparse = models.PositiveIntegerField(default=0)
    files_completed = models.PositiveIntegerField(default=0)
    files_failed = models.PositiveIntegerField(default=0)

    num_records_deleted = models.PositiveIntegerField(default=0)
    num_records_created = models.PositiveIntegerField(default=0)

    total_num_records_initial = models.PositiveBigIntegerField(default=0)
    total_num_records_post = models.PositiveBigIntegerField(default=0)

    db_backup_location = models.CharField(max_length=512)

    # Options used to select the files to reparse
    fiscal_quarter = models.CharField(max_length=2, null=True)
    fiscal_year = models.PositiveIntegerField(null=True)
    all = models.BooleanField(default=False)
    new_indices = models.BooleanField(default=False)
    delete_old_indices = models.BooleanField(default=False)

    @staticmethod
    def assert_all_files_done(meta_model):
        """
        Check if all files have been parsed with or without exceptions.

        This function assumes the meta_model has been passed in a distributed/thread safe way. If the database row
        containing this model has not been locked the caller will experience race issues.
        """
        if meta_model.finished and (meta_model.files_completed == meta_model.num_files_to_reparse or
                                    meta_model.files_completed + meta_model.files_failed ==
                                    meta_model.num_files_to_reparse or
                                    meta_model.files_failed == meta_model.num_files_to_reparse):
            return True
        return False

    @staticmethod
    def set_reparse_finished(meta_model):
        """
        Set status/completion fields to appropriate values.

        This function assumes the meta_model has been passed in a distributed/thread safe way. If the database row
        containing this model has not been locked the caller will experience race issues.
        """
        meta_model.finished = True
        meta_model.success = meta_model.files_completed == meta_model.num_files_to_reparse
        meta_model.total_num_records_post = count_all_records()
        meta_model.save()

    @staticmethod
    def increment_files_completed(reparse_meta_models):
        """
        Increment the count of files that have completed parsing for the datafile's current/latest reparse model.

        Because this function can be called in parallel we use `select_for_update` because multiple parse tasks can
        referrence the same ReparseMeta object that is being queried below. `select_for_update` provides a DB lock on
        the object and forces other transactions on the object to wait until this one completes.
        """
        if reparse_meta_models.exists():
            with transaction.atomic():
                try:
                    meta_model = reparse_meta_models.select_for_update().latest("pk")
                    meta_model.files_completed += 1
                    if ReparseMeta.assert_all_files_done(meta_model):
                        ReparseMeta.set_reparse_finished(meta_model)
                    meta_model.save()
                except DatabaseError:
                    logger.exception("Encountered exception while trying to update the `files_reparsed` field on the "
                                     f"ReparseMeta object with ID: {meta_model.pk}.")

    @staticmethod
    def increment_files_failed(reparse_meta_models):
        """
        Increment the count of files that failed parsing for the datafile's current/latest reparse meta model.

        Because this function can be called in parallel we use `select_for_update` because multiple parse tasks can
        referrence the same ReparseMeta object that is being queried below. `select_for_update` provides a DB lock on
        the object and forces other transactions on the object to wait until this one completes.
        """
        if reparse_meta_models.exists():
            with transaction.atomic():
                try:
                    meta_model = reparse_meta_models.select_for_update().latest("pk")
                    meta_model.files_failed += 1
                    if ReparseMeta.assert_all_files_done(meta_model):
                        ReparseMeta.set_reparse_finished(meta_model)
                    meta_model.save()
                except DatabaseError:
                    logger.exception("Encountered exception while trying to update the `files_failed` field on the "
                                     f"ReparseMeta object with ID: {meta_model.pk}.")

    @staticmethod
    def increment_records_created(reparse_meta_models, num_created):
        """
        Increment the count of records created for the datafile's current/latest reparse meta model.

        Because this function can be called in parallel we use `select_for_update` because multiple parse tasks can
        referrence the same ReparseMeta object that is being queried below. `select_for_update` provides a DB lock on
        the object and forces other transactions on the object to wait until this one completes.
        """
        if reparse_meta_models.exists():
            with transaction.atomic():
                try:
                    meta_model = reparse_meta_models.select_for_update().latest("pk")
                    meta_model.num_records_created += num_created
                    meta_model.save()
                except DatabaseError:
                    logger.exception("Encountered exception while trying to update the `files_failed` field on the "
                                     f"ReparseMeta object with ID: {meta_model.pk}.")

    @staticmethod
    def get_latest():
        """Get the ReparseMeta model with the greatest pk."""
        max_pk = ReparseMeta.objects.all().aggregate(Max('pk'))
        if max_pk.get("pk__max", None) is None:
            return None
        return ReparseMeta.objects.get(pk=max_pk["pk__max"])
