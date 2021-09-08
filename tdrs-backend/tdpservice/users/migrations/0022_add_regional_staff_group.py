from django.contrib.auth.models import Group
from django.db import migrations

from tdpservice.users.permissions import (
    add_permissions_q,
    delete_permissions_q,
    get_permission_ids_for_model,
    view_permissions_q
)

def create_perms(apps, schema_editor):
    """Creates permissions for all installed apps.

    This is needed because Django does not actually create any Content Types
    or Permissions until a post_migrate signal is raised after the completion
    of `manage.py migrate`. When this migration is run as part of a set for a
    freshly created database, that signal will not run until all migrations are
    complete - resulting in no permissions for any Group.

    For more info: https://code.djangoproject.com/ticket/29843
    """
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None


def set_regional_staff_permissions(apps, schema_editor):
    """Set relevant Group Permissions for OFA Regional Staff group."""
    regional_staff = apps.get_model('auth', 'Group').objects.get(name='OFA Regional Staff')

    # For the User model OFA Regional Staff will have all permissions *except* delete
    user_permissions = get_permission_ids_for_model(
        'users',
        'user',
        exclusions=[delete_permissions_q]
    )

    # The rest of the permissions are view only
    region_permissions = get_permission_ids_for_model(
        'stts',
        'region',
        filters=[view_permissions_q]
    )
    stt_permissions = get_permission_ids_for_model(
        'stts',
        'stt',
        filters=[view_permissions_q]
    )
    datafile_permissions = get_permission_ids_for_model(
        'data_files',
        'datafile',
        filters=[add_permissions_q, view_permissions_q]
    )
    logentry_permissions = get_permission_ids_for_model(
        'admin',
        'logentry',
        filters=[view_permissions_q]
    )
    group_permissions = get_permission_ids_for_model(
        'auth',
        'group',
        filters=[view_permissions_q]
    )

    # Clear existing permissions that may be set so we can ensure pristine state
    regional_staff.permissions.clear()

    # Assign correct permissions
    regional_staff.permissions.add(*user_permissions)
    regional_staff.permissions.add(*region_permissions)
    regional_staff.permissions.add(*stt_permissions)
    regional_staff.permissions.add(*datafile_permissions)
    regional_staff.permissions.add(*logentry_permissions)
    regional_staff.permissions.add(*group_permissions)

# def unset_regional_staff_permissions(apps, schema_editor):
#     """Remove all Group Permissions added to OFA Regional Staff."""
#     regional_staff = apps.get_model('auth', 'Group').objects.get(name='OFA Regional Staff')
#     regional_staff.permissions.clear()

def add_regional_staff(apps, schema_editor):
    regional_staff, _ = (
        apps.get_model('auth', 'Group')
            .objects
            .get_or_create(name='OFA Regional Staff')
    )

    # Clear existing permissions that may be set so we can ensure pristine state
    regional_staff.permissions.clear()
    regional_staff.permissions.add(
        *apps.get_model('auth', 'Permission').objects.all()
            .values_list('id', flat=True)
    )

def remove_regional_staff(apps, schema_editor):
    Group.objects.delete(name="OFA Regional Staff")


class Migration(migrations.Migration):
    dependencies = [
        ('users',"0020_ofa_system_admin_permissions")
    ]
    operations = [
        migrations.RunPython(add_regional_staff, remove_regional_staff)
    ]

