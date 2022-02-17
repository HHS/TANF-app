from django.contrib.auth.models import Group
from django.db import migrations

from tdpservice.users.permissions import (
    create_perms,
    get_permission_ids_for_model,
    view_permissions_q,
)


def add_ocio_group(apps, schema_editor):
    Group.objects.create(name="ACF OCIO")


def remove_ocio_group(apps, schema_editor):
    Group.objects.filter(name__in={"ACF OCIO"}).delete()


def assign_ocio_permissions(apps, schema_editor):
    acf_ocio, _ = apps.get_model('auth', 'Group').objects.get(name="ACF OCIO")

    zap_scan_permissions = get_permission_ids_for_model(
        'security',
        'owaspzapscan',
        filters=[view_permissions_q]
    )

    av_scan_permissions = get_permission_ids_for_model(
        'security',
        'clamavfilescan',
        filters=[view_permissions_q]
    )

    acf_ocio.permissions.clear()
    acf_ocio.permissions.add(*zap_scan_permissions, *av_scan_permissions)


class Migration(migrations.Migration):
    dependencies = [
        ("users", "TODO"),
    ]

    operations = [
        migrations.RunPython(
            add_ocio_group,
            reverse_code=remove_ocio_group
        ),
        migrations.RunPython(
            create_perms,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(assign_ocio_permissions),
    ]
