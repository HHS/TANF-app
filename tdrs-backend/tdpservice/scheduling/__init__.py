from __future__ import absolute_import
import logging
import os
from django.conf import settings

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from tdpservice.scheduling.celery import app as celery_app

__all__ = ['celery_app']
