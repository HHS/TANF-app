import os
from django.contrib.auth.hashers import make_password
from django.db import migrations
from django.utils import timezone

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0011_auto_20210108_1741'),
    ]

    def generate_superuser(apps, schema_editor):
        # Use the historical model to prevent this from failing on clean
        # builds if the User model changes in the future
        User = apps.get_model('users', 'User')

        # set the environment variable to the username of the
        # initial superuser
        su_username = os.environ.get('DJANGO_SU_NAME', 'admin')

        # Get current time for date_joined
        now = timezone.now()

        # Sets a password the user won't be able to log in with
        # Needed because we defer to Login.gov for authentication
        # and users mustn't be allowed to login directly.
        unusable_password = make_password(None)

        # Note we manually call `create` instead of `create_superuser`
        # This allows us to operate on Historical Models, which
        # do not have access to arbitrary model methods.
        # https://docs.djangoproject.com/en/3.1/topics/migrations/#historical-models  noqa
        User.objects.create(
            username=su_username,
            email=su_username,
            date_joined=now,
            is_active=True,
            is_staff=True,
            is_superuser=True,
            password=unusable_password
        )

    operations = [
        migrations.RunPython(generate_superuser),
    ]
