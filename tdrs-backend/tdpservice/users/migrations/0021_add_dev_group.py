
from django.db import migrations
from django.contrib.auth.models import Group
from django.conf import settings

from tdpservice.users.permissions import delete_permissions_q

def add_dev_group(apps, schema_editor):
    """Add super user group for devs that is only present in non production environments."""
    if settings.ENABLE_DEVELOPER_GROUP:
        developer, _ = (
            apps.get_model('auth', 'Group')
                .objects
                .get_or_create(name='Developer')
        )

    # Clear existing permissions that may be set so we can ensure pristine state
    developer.permissions.clear()
    developer.permissions.add(
        apps.get_model('auth', 'Permission').objects.all()
    )

class Migration(migrations.Migration):
    dependencies = [

    ]
    operations = [
        migrations.RunPython(add_dev_group,remove_dev_group)
    ]
