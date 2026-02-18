"""Migration to add Feedback Report permissions to OFA System Admin.

This migration explicitly adds report permissions to OFA System Admin.

Background: Migration 0020 grants OFA System Admin "all permissions that exist
at the time the migration runs". However, since 0020 ran in 2021 before the
Reports app existed, OFA System Admin never received report permissions in
deployed environments. This migration fixes that.

Note: Migration 0054 was updated to include this, but if 0054 was already
applied before the update, this separate migration ensures the permissions
are granted.
"""

from django.db import migrations

from tdpservice.users.permissions import (
    add_permissions_q,
    create_perms,
    get_permission_ids_for_model,
    view_permissions_q,
)


def add_ofa_system_admin_report_permissions(apps, schema_editor):
    """Add report permissions to OFA System Admin group."""
    ofa_sys_admin = apps.get_model("auth", "Group").objects.get(name="OFA System Admin")

    # Get view and add permissions for ReportFile and ReportSource
    report_file_permissions = get_permission_ids_for_model(
        "reports", "reportfile", filters=[view_permissions_q, add_permissions_q]
    )
    report_source_permissions = get_permission_ids_for_model(
        "reports", "reportsource", filters=[view_permissions_q, add_permissions_q]
    )

    # Add permissions to OFA System Admin (idempotent - won't duplicate if already there)
    ofa_sys_admin.permissions.add(*report_file_permissions)
    ofa_sys_admin.permissions.add(*report_source_permissions)


def remove_ofa_system_admin_report_permissions(apps, schema_editor):
    """Remove report permissions from OFA System Admin group (reverse operation)."""
    ofa_sys_admin = apps.get_model("auth", "Group").objects.get(name="OFA System Admin")

    # Get view and add permissions for ReportFile and ReportSource
    report_file_permissions = get_permission_ids_for_model(
        "reports", "reportfile", filters=[view_permissions_q, add_permissions_q]
    )
    report_source_permissions = get_permission_ids_for_model(
        "reports", "reportsource", filters=[view_permissions_q, add_permissions_q]
    )

    # Remove permissions from OFA System Admin
    ofa_sys_admin.permissions.remove(*report_file_permissions)
    ofa_sys_admin.permissions.remove(*report_source_permissions)


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '__latest__'),
        ('users', '0054_update_feedback_report_permissions'),
    ]

    operations = [
        # Ensure permissions are created for the Reports app models
        migrations.RunPython(
            create_perms,
            reverse_code=migrations.RunPython.noop
        ),
        # Add report permissions to OFA System Admin
        migrations.RunPython(
            add_ofa_system_admin_report_permissions,
            reverse_code=remove_ofa_system_admin_report_permissions
        ),
    ]
