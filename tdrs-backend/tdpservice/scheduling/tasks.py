from __future__ import absolute_import
from celery import shared_task
import logging
from .db_backup import run_backup

logger = logging.getLogger(__name__)

@shared_task
def nightly_postgres(*args):
    logger.debug("We have nightly registered w/ arg: " + ''.join(args))
    #run_backup(arg)
    return True
