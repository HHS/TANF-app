import logging
from datetime import datetime

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION

from .users.models import User

logger = logging.getLogger(__name__)


def log_event_for_model():
    logger.info('Test')
