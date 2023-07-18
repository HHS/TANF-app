import logging
from django.conf import settings
from tdpservice.users.models import User

logger = logging.getLogger()


print('__________ see if print works __________')
print('_____ start debugging _____')
print('_____ settings.DATABASES:: ' + str(settings.DATABASES))
user_ = User.objects.all()
print('_____ user_:: ' + str(user_))
print('_____ end debugging ______')