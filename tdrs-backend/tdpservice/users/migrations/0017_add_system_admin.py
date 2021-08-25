
from django.contrib.auth.models import Group
from django.db import migrations

def add_sys_admin(apps, schema_editor):
    Group.objects.create(name="OFA System Admin")
def remove_sys_admin(apps, schema_editor):
    Group.objects.delete(name="OFA System Admin")


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0014_add_user_deactivated'),
        ('users', '0015_replace_data_analyst_role'),
    ]
    operations = [
        migrations.RunPython(add_sys_admin,remove_sys_admin),
    ]