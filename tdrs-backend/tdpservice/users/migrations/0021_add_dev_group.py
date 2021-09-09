
from django.db import migrations
from django.contrib.auth.models import Group
from django.conf import settings


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
            *apps.get_model('auth', 'Permission').objects.all()
                .values_list('id', flat=True)
        )



class Migration(migrations.Migration):
    dependencies = [
        ('users', '0020_ofa_system_admin_permissions'),
        ('users', '0017_unset_superuser_flag')

    ]
    operations = [
        migrations.RunPython(add_dev_group,
            reverse_code=migrations.RunPython.noop)
    ]
