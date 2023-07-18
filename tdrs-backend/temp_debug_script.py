import logging
from django.conf import settings
from django.contrib.auth.models import User

logger = logging.getLogger()


logger.info('_____ start debugging _____')
logger.info('_____ settings.DATABASES:: ' + str(settings.DATABASES))
user_ = User.objects.all()
logger.info('_____ user_:: ' + str(user_))
logger.info('_____ end debugging _____')