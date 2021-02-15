import os
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0011_auto_20210108_1741'),
    ]

    def generate_superuser(apps, schema_editor):
        from ..models import User

        # set the environment variable to the username of the
        # initial superuser
        su_username = os.environ.get('DJANGO_SU_NAME', 'admin')

        superuser = User.objects.create_superuser(
            username=su_username,
            email=su_username)
        superuser.set_unusable_password()

        superuser.save()

    operations = [
        migrations.RunPython(generate_superuser),
    ]
