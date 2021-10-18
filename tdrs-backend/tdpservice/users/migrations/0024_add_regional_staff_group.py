from django.contrib.auth.models import Group
from django.db import migrations

from tdpservice.users.permissions import (
    add_permissions_q,
    delete_permissions_q,
    get_permission_ids_for_model,
    view_permissions_q
)





def add_regional_staff(apps, schema_editor):
    regional_staff, _ = (
        apps.get_model('auth', 'Group')
            .objects
            .get_or_create(name='OFA Regional Staff')
    )

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

def remove_regional_staff(apps, schema_editor):
    Group.objects.delete(name="OFA Regional Staff")


class Migration(migrations.Migration):
    dependencies = [
        ('users',"0020_ofa_system_admin_permissions")
    ]
    operations = [
        migrations.RunPython(add_regional_staff, remove_regional_staff)
    ]

