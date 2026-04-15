from django.db import migrations

from tdpservice.users.permissions import (
    create_perms,
    get_permission_ids_for_model,
    view_permissions_q,
)


def set_regional_staff_permissions(apps, schema_editor):
    """Add view_reportfile permission to OFA Regional Staff group."""
    regional_staff = apps.get_model("auth", "Group").objects.get(
        name="OFA Regional Staff"
    )

    report_file_permissions = get_permission_ids_for_model(
        "reports", "reportfile", filters=[view_permissions_q]
    )

    regional_staff.permissions.add(*report_file_permissions)


def unset_regional_staff_permissions(apps, schema_editor):
    """Remove view_reportfile permission from OFA Regional Staff group."""
    regional_staff = apps.get_model("auth", "Group").objects.get(
        name="OFA Regional Staff"
    )

    report_file_permissions = get_permission_ids_for_model(
        "reports", "reportfile", filters=[view_permissions_q]
    )

    regional_staff.permissions.remove(*report_file_permissions)


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "__latest__"),
        ("users", "0055_add_ofa_sys_admin_report_permissions"),
    ]

    operations = [
        migrations.RunPython(
            create_perms,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            set_regional_staff_permissions,
            reverse_code=unset_regional_staff_permissions,
        ),
    ]
