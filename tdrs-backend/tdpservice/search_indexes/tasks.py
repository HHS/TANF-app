"""Shared celery search_indexes tasks for beat."""

from __future__ import absolute_import
import time
from tdpservice.users.models import User
from celery import shared_task
from tdpservice.core.utils import log
import subprocess


def prettify_time_delta(start, end):
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
        reindex_cmd = subprocess.Popen(
            ['python', 'manage.py', 'search_index', '--rebuild', '--use-alias', '--parallel', '-f'],
            stderr=subprocess.DEVNULL, stdout=subprocess.PIPE,
        )
        reindex_cmd.wait()
        reindex_cmd_out, reindex_cmd_error = reindex_cmd.communicate()
        log(reindex_cmd_out)
        log(reindex_cmd_error)
    except Exception as e:
        end = time.time()
        min, sec = prettify_time_delta(start, end)
        log(f'Elastic reindex failed with an exception after {min} minutes and {sec} seconds. {e}', {
            'user_id': system_user.pk,
            'object_id': None,
            'object_repr': ''
        })
        return

    end = time.time()
    min, sec = prettify_time_delta(start, end)

    log(f'Elastic reindex complete, took {min} minutes and {sec} seconds.', {
        'user_id': system_user.pk,
        'object_id': None,
        'object_repr': ''
    })
