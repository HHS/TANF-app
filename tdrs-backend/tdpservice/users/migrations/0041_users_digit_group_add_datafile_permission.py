# Generated by Django 3.2.5 on 2021-08-16 14:10
from django.contrib.auth.models import Group
from django.db import migrations

from tdpservice.users.permissions import (
    add_permissions_q,
    get_permission_ids_for_model,
    view_permissions_q
)


def set_digit_team_permissions(apps, schema_editor):
    """Set relevant Group Permissions for DIGIT Team group."""
    digit = (
        apps.get_model('auth', 'Group').objects.get(name='DIGIT Team')
    )

    stt_permissions = get_permission_ids_for_model(
        'stts',
        'stt',
        filters=[view_permissions_q]
    )


    datafile_permissions = get_permission_ids_for_model(
        'data_files',
        'datafile',
        filters=[view_permissions_q, add_permissions_q]
    )

    # Assign model permissions
    digit.permissions.add(*datafile_permissions, *stt_permissions)

def unset_digit_team_permissions(apps, schema_editor):
    """Remove all Group Permissions added to DIGIT Team."""
    digit = (
        apps.get_model('auth', 'Group').objects.get(name='DIGIT Team')
    )
    datafile_permissions = get_permission_ids_for_model(
        'data_files',
        'datafile',
        filters=[view_permissions_q, add_permissions_q]
    )
    digit.permissions.remove(*datafile_permissions)

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '__latest__'),
        ('users', '0040_users_digit_group_permissions'),
    ]

    operations = [
        migrations.RunPython(
            set_digit_team_permissions,
            reverse_code=unset_digit_team_permissions
        )
    ]
