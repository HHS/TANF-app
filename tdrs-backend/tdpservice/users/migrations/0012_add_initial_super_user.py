import os
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0011_auto_20210108_1741'),
    ]

    def generate_superuser(apps, schema_editor):
        from ..models import User

        # DJANGO_DB_NAME = os.environ.get('DJANGO_DB_NAME', "default")
        DJANGO_SU_NAME = os.environ.get('DJANGO_SU_NAME','admin')
        DJANGO_SU_EMAIL = os.environ.get('DJANGO_SU_EMAIL','admin@example.com')
        DJANGO_SU_PASSWORD = os.environ.get('DJANGO_SU_PASSWORD','StrongPassword') # only use the default case for password in development

        superuser = User.objects.create_superuser(
            username=DJANGO_SU_NAME,
            email=DJANGO_SU_EMAIL,
            password=DJANGO_SU_PASSWORD)

        superuser.save()

    operations = [
        migrations.RunPython(generate_superuser),
    ]
