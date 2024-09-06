"""Shared celery search_indexes tasks for beat."""

from __future__ import absolute_import
import time
import csv
import gzip
import os
from tdpservice.users.models import User
from celery import shared_task
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

    @param query_str: a sql string obtained via queryset.query.
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
            for obj in self.queryset.iterator():
                # for obj in self.queryset:
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

    Model = apps.get_model('search_indexes', model_name)
    queryset = Model.objects.raw(query_str, query_params)
    iterator = RowIterator(field_names, queryset)
    s3 = S3Client()

    # stream the creation of the file using smart_open
    # url = f's3://{settings.AWS_S3_DATAFILES_BUCKET_NAME}/{s3_filename}.csv'
    # with open(url, 'w', transport_params={'client': s3.client}) as fout:
    #     for _, s in enumerate(iterator):
    #         fout.write(s)

    # write + compress into tar/gz on filesystem - upload resulting file to s3
    # have to clean up resulting file

    tmp_filename = 'file.csv.gz'
    with gzip.open(tmp_filename, 'wt') as f:
        for _, s in enumerate(iterator):
            f.write(s)

    local_filename = os.path.basename(tmp_filename)
    s3.client.upload_file(local_filename, settings.AWS_S3_DATAFILES_BUCKET_NAME, s3_filename)

    os.remove(local_filename)
