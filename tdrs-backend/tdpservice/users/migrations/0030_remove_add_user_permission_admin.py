from django.db import migrations

from tdpservice.users.permissions import (
    get_permission_ids_for_model,
    add_permissions_q,
    view_permissions_q
)


def set_system_admin_permissions(apps, schema_editor):
    """Set relevant Group Permissions for OFA Admin group."""
    system_admin = (
        apps.get_model('auth', 'Group').objects.get(name='OFA System Admin')
    )

    user_permissions = get_permission_ids_for_model(
        'users',
        'user',
        filters=[add_permissions_q]
    )

    # Assign correct permissions
    system_admin.permissions.remove(*user_permissions)


def unset_system_admin_permissions(apps, schema_editor):
    """Remove all Group Permissions added to OFA Admin."""
    system_admin = (
        apps.get_model('auth', 'Group').objects.get(name='OFA System Admin')
    )

    user_permissions = get_permission_ids_for_model(
        'users',
        'user',
        filters=[add_permissions_q]
    )

    # Assign correct permissions
    system_admin.permissions.add(*user_permissions)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0029_use_location'),
    ]

    operations = [
        migrations.RunPython(
            set_system_admin_permissions,
            reverse_code=unset_system_admin_permissions
        )
    ]
