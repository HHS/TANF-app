"""Shared celery search_indexes tasks for beat."""

from __future__ import absolute_import
import time
import csv
import gzip
import os
from tdpservice.users.models import User
from celery import shared_task
from botocore.exceptions import ClientError
from tdpservice.core.utils import log
import subprocess
from tdpservice.data_files.s3_client import S3Client
from django.conf import settings
from django.apps import apps


def prettify_time_delta(start, end):
    """Calculate minutes and seconds."""
    elapsed_seconds = int(end-start)
    elapsed_minutes = elapsed_seconds // 60
    remainder_seconds = int(elapsed_seconds - (elapsed_minutes*60))
    remainder_seconds = remainder_seconds if elapsed_minutes > 0 else elapsed_seconds

    return elapsed_minutes, remainder_seconds

@shared_task
def reindex_elastic_documents():
    """Run the django-elasticsearch-dsl management command to reindex the elastic instance."""
    system_user, created = User.objects.get_or_create(username='system')
    if created:
        log('Created reserved system user.')

    start = time.time()
    log('Starting elastic reindex.', {
        'user_id': system_user.pk,
        'object_id': None,
        'object_repr': ''
    })

    try:
        reindex_cmd = subprocess.Popen(['python', 'manage.py', 'search_index', '--rebuild', '--use-alias', '--parallel',
                                        '-f'], stderr=subprocess.DEVNULL, stdout=subprocess.PIPE,)
        reindex_cmd_out, reindex_cmd_error = reindex_cmd.communicate()
        reindex_cmd_out = "" if reindex_cmd_out is None else reindex_cmd_out.decode("utf-8")
        if reindex_cmd.returncode != 0:
            log(f'Received non-zero return code during Elastic re-index. Received code: {reindex_cmd.returncode}.',
                {
                    'user_id': system_user.pk,
                    'object_id': None,
                    'object_repr': ''
                },
                level='error')
        log(reindex_cmd_out)
    except Exception as e:
        end = time.time()
        min, sec = prettify_time_delta(start, end)
        log(f'Elastic reindex failed with an exception after {min} minutes and {sec} seconds. {e}', {
            'user_id': system_user.pk,
            'object_id': None,
            'object_repr': ''
        }, level='error')
        return

    end = time.time()
    min, sec = prettify_time_delta(start, end)

    log(f'Elastic reindex complete, took {min} minutes and {sec} seconds.', {
        'user_id': system_user.pk,
        'object_id': None,
        'object_repr': ''
    })


@shared_task
def export_queryset_to_s3_csv(query_str, query_params, field_names, model_name, s3_filename):
    """
    Export a selected queryset to a csv file stored in s3.

    @param query_str: a sql string obtained via queryset.query.sql_with_params().
    @param query_params: sql query params obtained via queryset.query.sql_with_params().
    @param field_names: a list of field names for the csv header.
    @param model_name: the `model._meta.model_name` of the model to export.
    @param s3_filename: a string representing the file path/name in s3.
    """
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
            self.writer = csv.writer(Echo())
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
            # queryset.iterator simply 'forgets' the record after iterating over it, instead of caching it
            # this is okay here since we only write out the contents and don't need the record again
            for obj in self.queryset.iterator():
                row = []

                if self.is_header_row:
                    self.is_header_row = False
                    yield self.writer.writerow(self.header_row)

                for field_name in self.field_names:
                    field = getattr(obj, field_name)
                    row.append(field)
                    if field and field_name == "datafile":
                        # print(field)
                        row.append(field.stt.stt_code)
                yield self.writer.writerow(row)

    system_user, _ = User.objects.get_or_create(username='system')
    Model = apps.get_model('search_indexes', model_name)
    queryset = Model.objects.raw(query_str, query_params)
    iterator = RowIterator(field_names, queryset)
    s3 = S3Client()

    tmp_filename = 'file.csv.gz'
    record_count = -1  # offset row count to account for the header
    with gzip.open(tmp_filename, 'wt') as f:
        for _, s in enumerate(iterator):
            record_count += 1
            f.write(s)

    local_filename = os.path.basename(tmp_filename)

    try:
        s3.client.upload_file(local_filename, settings.AWS_S3_DATAFILES_BUCKET_NAME, s3_filename)
    except ClientError as e:
        log(
            f'Export failed: {s3_filename}. {e}',
            {'user_id': system_user.pk, 'object_id': None, 'object_repr': ''},
            'error'
        )
    else:
        log(
            f'Export of {record_count} {model_name} objects complete: {s3_filename}',
            {'user_id': system_user.pk, 'object_id': None, 'object_repr': ''}
        )

    os.remove(local_filename)
