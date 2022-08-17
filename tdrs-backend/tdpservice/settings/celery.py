"""Celey configuration file."""
from __future__ import absolute_import
import os
from celery import Celery
import configurations

# Set the default Django settings module for the 'celery' program.
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tdpservice.settings.local")
# os.environ.setdefault("DJANGO_CONFIGURATION", "Local")
import logging
logger = logging.getLogger(__name__)

configurations.setup()

app = Celery('settings')
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
logger.debug('+++++++++++++++++++++ ' + str(app.__dict__))
# Load task modules from all registered Django apps.
app.autodiscover_tasks()