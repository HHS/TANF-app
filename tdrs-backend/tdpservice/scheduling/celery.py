from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tdpservice.settings.local")
os.environ.setdefault("DJANGO_CONFIGURATION", "Local")

import configurations
configurations.setup()

app = Celery('settings')
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')


# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task
def add(x, y):
    return x + y

@app.task()
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

