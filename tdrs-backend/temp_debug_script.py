import logging
from django.conf import settings
from tdpservice.users.models import User

logger = logging.getLogger()


print('__________ see if print works __________')
logger.info('_____ start debugging _____')
logger.info('_____ settings.DATABASES:: ' + str(settings.DATABASES))
user_ = User.objects.all()
logger.info('_____ user_:: ' + str(user_))
logger.info('_____ end debugging ______')