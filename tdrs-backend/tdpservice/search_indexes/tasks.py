"""Shared celery search_indexes tasks for beat."""

from __future__ import absolute_import

import gzip
import os

from django.apps import apps
from django.conf import settings

from botocore.exceptions import ClientError
from celery import shared_task

from tdpservice.core.utils import log
from tdpservice.data_files.s3_client import S3Client
from tdpservice.users.models import User


def prettify_time_delta(start, end):
    """Calculate minutes and seconds."""
    elapsed_seconds = int(end - start)
    elapsed_minutes = elapsed_seconds // 60
    remainder_seconds = int(elapsed_seconds - (elapsed_minutes * 60))
    remainder_seconds = remainder_seconds if elapsed_minutes > 0 else elapsed_seconds

    return elapsed_minutes, remainder_seconds


class RowIterator:
    """Iterator class to support custom CSV row generation."""

    def __init__(self, field_names, queryset):
        self.field_names = field_names
        self.queryset = queryset

    def _get_header(self, field_names):
        """Generate custom header row."""
        header_row = ""
        for name in field_names:
            header_row += f"{name},"
            if name == "datafile":
                header_row += "STT,"
        return header_row[:-1] + "\n"

    def __iter__(self):
        """Yield the next row in the csv export."""
        yield self._get_header(self.field_names)

        # queryset.iterator simply 'forgets' the record after iterating over it, instead of caching it
        # this is okay here since we only write out the contents and don't need the record again.
        for obj in self.queryset.iterator():
            row = ""
            for field_name in self.field_names:
                field = getattr(obj, field_name)
                row += f"{field},"
                if field and field_name == "datafile":
                    row += f"{field.stt.stt_code},"
            yield row[:-1] + "\n"


@shared_task
def export_queryset_to_s3_csv(
    query_str, query_params, field_names, model_name, s3_filename
):
    """
    Export a selected queryset to a csv file stored in s3.

    @param query_str: a sql string obtained via queryset.query.sql_with_params().
    @param query_params: sql query params obtained via queryset.query.sql_with_params().
    @param field_names: a list of field names for the csv header.
    @param model_name: the `model._meta.model_name` of the model to export.
    @param s3_filename: a string representing the file path/name in s3.
    """
    system_user, _ = User.objects.get_or_create(username="system")
    Model = apps.get_model("search_indexes", model_name)
    queryset = Model.objects.raw(query_str, query_params)
    iterator = RowIterator(field_names, queryset)
    s3 = S3Client()

    tmp_filename = "file.csv.gz"
    record_count = -1  # offset row count to account for the header
    with gzip.open(tmp_filename, "wt") as f:
        for row in iterator:
            record_count += 1
            f.write(row)

    local_filename = os.path.basename(tmp_filename)

    try:
        s3.client.upload_file(
            local_filename, settings.AWS_S3_DATAFILES_BUCKET_NAME, s3_filename
        )
    except ClientError as e:
        log(
            f"Export failed: {s3_filename}. {e}",
            {"user_id": system_user.pk, "object_id": None, "object_repr": ""},
            "error",
        )
    else:
        log(
            f"Export of {record_count} {model_name} objects complete: {s3_filename}",
            {"user_id": system_user.pk, "object_id": None, "object_repr": ""},
        )
    os.remove(local_filename)
