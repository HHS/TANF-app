import logging
from django.conf import settings
from tdpservice.users.models import User

logger = logging.getLogger()


print('_____ start debugging _____')
print('___')
print('_____ settings.DATABASES:: ' + str(settings.DATABASES))
user_ = User.objects.all()
print('_____ user_:: ' + str(user_))
print('_____ end debugging ______')