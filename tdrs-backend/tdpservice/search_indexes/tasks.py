"""Shared celery search_indexes tasks for beat."""

from __future__ import absolute_import
import time
from tdpservice.users.models import User
from celery import shared_task
from tdpservice.core.utils import log
from django.core.management import call_command


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
        'object_repr': 'Exception in search_index --rebuild'
    })

    call_command('tdp_search_index', '--rebuild', '--use-alias', '--parallel', '-f')

    end = time.time()
    elapsed_seconds = end-start
    elapsed_minutes = int(elapsed_seconds/60)
    remainder_seconds = int(elapsed_seconds - (elapsed_minutes*60))
    remainder_seconds = remainder_seconds if elapsed_minutes > 0 else elapsed_seconds

    log(f'Elastic reindex complete, took {elapsed_minutes} minutes and {remainder_seconds} seconds.', {
        'user_id': system_user.pk,
        'object_id': None,
        'object_repr': 'Exception in search_index --rebuild'
    })
