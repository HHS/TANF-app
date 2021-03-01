import os
import logging
from django.contrib.auth.hashers import make_password
from django.db import migrations
from django.utils import timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0011_auto_20210108_1741'),
    ]

    def generate_superuser(apps, schema_editor):
        # set the environment variable to the username of the
        # initial superuser
        su_username = os.environ.get('DJANGO_SU_NAME')

        # Get current time for date_joined
        now = timezone.now()

        # Sets a password the user won't be able to log in with
        # Needed because we defer to Login.gov for authentication
        # and users mustn't be allowed to login directly.
        unusable_password = make_password(None)

        # Use the historical model to prevent this from failing on clean
        # builds if the User model changes in the future
        # https://docs.djangoproject.com/en/3.1/topics/migrations/#historical-models  noqa
        superuser, was_created = apps.get_model('users', 'User').objects.get_or_create(
            username=su_username,
            defaults={'email': su_username, 'date_joined': now, 'password': unusable_password},
        )
        # log the success of the operation
        logger.info(f"SUPERUSER CREATED: {was_created}")
        # if the user already exists we need to make sure they have the correct
        # flags set. This can't be updated in `get_or_create()`
        superuser.is_active = True
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.save()

    operations = [
        migrations.RunPython(generate_superuser, reverse_code=migrations.RunPython.noop),
    ]
