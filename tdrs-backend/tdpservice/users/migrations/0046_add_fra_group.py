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

    # Get or create groups that need FRA access
    fra_submitter, _ = Group.objects.get_or_create(name='FRA Submitter')
    developer = Group.objects.get(name='Developer')

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
    fra_submitter.permissions.clear()
    fra_submitter.permissions.add(*datafile_permissions, fra_permission)

    # add FRA permissions to other groups
    developer.permissions.add(fra_permission)
    # TODO: 4972 - What other groups need fra access?

def unset_fra_submitters_group_and_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    # Groups to reove fra from
    fra_submitter = Group.objects.get(name='FRA Submitter')
    developer = Group.objects.get(name='Developer')

    # Delete fra submitter group
    fra_submitter.delete()

    # Remove fra permissions from other groups
    fra_access_permission = Permission.objects.get(codename='has_fra_access')
    developer.permissions.remove(fra_access_permission)

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


