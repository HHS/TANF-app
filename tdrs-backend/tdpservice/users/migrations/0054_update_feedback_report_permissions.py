"""Migration to update Feedback Report permissions.

This migration:
- Removes all report permissions from "OFA Admin" group
- Adds report permissions to "DIGIT Team" group
- (OFA System Admin already has all permissions via migration 0020)

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
    ]
