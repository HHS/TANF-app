"""Shared celery search_indexes tasks for beat."""

from __future__ import absolute_import
import time
from tdpservice.users.models import User
from celery import shared_task
from tdpservice.core.utils import log
import subprocess


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
