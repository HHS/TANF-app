from django.db import migrations

from tdpservice.users.permissions import (
    get_permission_ids_for_model,
    add_permissions_q,
    view_permissions_q
)

def set_fra_submitters_group_and_permissions(apps, shcema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # Create Group
    group, _ = Group.objects.get_or_create(name='FRA Submitter')

    # Get the same permissions as data analyst
    datafile_permissions = get_permission_ids_for_model(
        'data_files',
        'datafile',
        filters=[add_permissions_q, view_permissions_q]
    )

    # Creat Permission and assign to group
    # TODO: 4972 - should i make use of the get_permission_ids_for_model function here?
    contentType = ContentType.objects.get(app_label='users', model='user')
    fra_permission, _ = Permission.objects.get_or_create(
        codename='has_fra_access',
        name='Can access FRA Data Files',
        content_type=contentType,
    )

    # Clear old permissions and set the new one
    group.permissions.clear()
    group.permissions.add(*datafile_permissions, fra_permission)

def unset_fra_submitters_group_and_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='FRA Submitter').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '__latest__'),
        ('users', '0045_regional_staff_permissions_update'),
    ]

    operations = [
        migrations.RunPython(
            set_fra_submitters_group_and_permissions,
            reverse_code=unset_fra_submitters_group_and_permissions
        ),
    ]


