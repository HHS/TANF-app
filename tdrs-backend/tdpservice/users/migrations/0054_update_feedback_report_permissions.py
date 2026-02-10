"""Migration to update Feedback Report permissions.

This migration:
- Removes all report permissions from "OFA Admin" group
- Adds report permissions to "DIGIT Team" group
- Adds report permissions to "OFA System Admin" group

Note: Migration 0020 grants OFA System Admin "all permissions that exist
at the time the migration runs". However, since 0020 ran in 2021 before
the Reports app existed, OFA System Admin never received report permissions
in deployed environments. We must explicitly add them here.

Per client request: Only DIGIT Team and OFA System Admin should have
access to upload and manage feedback reports. OFA Admin should no longer
have any report-related permissions.
"""

from django.db import migrations

from tdpservice.users.permissions import (
    add_permissions_q,
    create_perms,
    get_permission_ids_for_model,
    view_permissions_q,
)


def remove_ofa_admin_report_permissions(apps, schema_editor):
    """Remove all report permissions from OFA Admin group."""
    ofa_admin = apps.get_model("auth", "Group").objects.get(name="OFA Admin")

    # Get view and add permissions for ReportFile and ReportSource
    report_file_permissions = get_permission_ids_for_model(
        "reports", "reportfile", filters=[view_permissions_q, add_permissions_q]
    )
    report_source_permissions = get_permission_ids_for_model(
        "reports", "reportsource", filters=[view_permissions_q, add_permissions_q]
    )

    # Remove permissions from OFA Admin
    ofa_admin.permissions.remove(*report_file_permissions)
    ofa_admin.permissions.remove(*report_source_permissions)


def restore_ofa_admin_report_permissions(apps, schema_editor):
    """Restore report permissions to OFA Admin group (reverse operation)."""
    ofa_admin = apps.get_model("auth", "Group").objects.get(name="OFA Admin")

    # Get view and add permissions for ReportFile and ReportSource
    report_file_permissions = get_permission_ids_for_model(
        "reports", "reportfile", filters=[view_permissions_q, add_permissions_q]
    )
    report_source_permissions = get_permission_ids_for_model(
        "reports", "reportsource", filters=[view_permissions_q, add_permissions_q]
    )

    # Add permissions back to OFA Admin
    ofa_admin.permissions.add(*report_file_permissions)
    ofa_admin.permissions.add(*report_source_permissions)


def add_digit_team_report_permissions(apps, schema_editor):
    """Add report permissions to DIGIT Team group."""
    digit_team = apps.get_model("auth", "Group").objects.get(name="DIGIT Team")

    # Get view and add permissions for ReportFile and ReportSource
    report_file_permissions = get_permission_ids_for_model(
        "reports", "reportfile", filters=[view_permissions_q, add_permissions_q]
    )
    report_source_permissions = get_permission_ids_for_model(
        "reports", "reportsource", filters=[view_permissions_q, add_permissions_q]
    )

    # Add permissions to DIGIT Team
    digit_team.permissions.add(*report_file_permissions)
    digit_team.permissions.add(*report_source_permissions)


def remove_digit_team_report_permissions(apps, schema_editor):
    """Remove report permissions from DIGIT Team group (reverse operation)."""
    digit_team = apps.get_model("auth", "Group").objects.get(name="DIGIT Team")

    # Get view and add permissions for ReportFile and ReportSource
    report_file_permissions = get_permission_ids_for_model(
        "reports", "reportfile", filters=[view_permissions_q, add_permissions_q]
    )
    report_source_permissions = get_permission_ids_for_model(
        "reports", "reportsource", filters=[view_permissions_q, add_permissions_q]
    )

    # Remove permissions from DIGIT Team
    digit_team.permissions.remove(*report_file_permissions)
    digit_team.permissions.remove(*report_source_permissions)


def add_ofa_system_admin_report_permissions(apps, schema_editor):
    """Add report permissions to OFA System Admin group.

    Note: Migration 0020 was supposed to grant all permissions to OFA System Admin,
    but it only grants permissions that exist at the time it runs. Since 0020 ran
    in 2021 before the Reports app existed, we must explicitly add these permissions.
    """
    ofa_sys_admin = apps.get_model("auth", "Group").objects.get(name="OFA System Admin")

    # Get view and add permissions for ReportFile and ReportSource
    report_file_permissions = get_permission_ids_for_model(
        "reports", "reportfile", filters=[view_permissions_q, add_permissions_q]
    )
    report_source_permissions = get_permission_ids_for_model(
        "reports", "reportsource", filters=[view_permissions_q, add_permissions_q]
    )

    # Add permissions to OFA System Admin
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
        ('users', '0053_remove_deactivated_access_request'),
    ]

    operations = [
        # Ensure permissions are created for the Reports app models
        migrations.RunPython(
            create_perms,
            reverse_code=migrations.RunPython.noop
        ),
        # Remove report permissions from OFA Admin
        migrations.RunPython(
            remove_ofa_admin_report_permissions,
            reverse_code=restore_ofa_admin_report_permissions
        ),
        # Add report permissions to DIGIT Team
        migrations.RunPython(
            add_digit_team_report_permissions,
            reverse_code=remove_digit_team_report_permissions
        ),
        # Add report permissions to OFA System Admin
        # (migration 0020 didn't add these because Reports app didn't exist in 2021)
        migrations.RunPython(
            add_ofa_system_admin_report_permissions,
            reverse_code=remove_ofa_system_admin_report_permissions
        ),
    ]
