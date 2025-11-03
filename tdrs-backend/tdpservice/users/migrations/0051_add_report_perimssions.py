from django.db import migrations

from tdpservice.users.permissions import (
    add_permissions_q,
    create_perms,
    get_permission_ids_for_model,
    view_permissions_q,
)


def set_ofa_admin_permissions(apps, schema_editor):
    """Set OFA admin permissions for the Reports app."""
    ofa_admin = apps.get_model("auth", "Group").objects.get(name="OFA Admin")

    # OFA Admin Should get view and add for ReportFiles and ReportIngestion
    report_file_permissions = get_permission_ids_for_model(
        "reports", "reportfile", filters=[view_permissions_q, add_permissions_q]
    )

    report_ingest_permissions = get_permission_ids_for_model(
        "reports", "reportingest", filters=[view_permissions_q, add_permissions_q]
    )

    ofa_admin.permissions.add(*report_file_permissions)
    ofa_admin.permissions.add(*report_ingest_permissions)


def unset_ofa_admin_permissions(apps, schema_editor):
    """Unset OFA admin permissions for the Reports app."""
    ofa_admin = apps.get_model("auth", "Group").objects.get(name="OFA Admin")

    # OFA Admin Should get view and add for ReportFiles and ReportIngestion
    report_file_permissions = get_permission_ids_for_model(
        "reports", "reportfile", filters=[view_permissions_q, add_permissions_q]
    )

    report_ingest_permissions = get_permission_ids_for_model(
        "reports", "reportingest", filters=[view_permissions_q, add_permissions_q]
    )

    ofa_admin.permissions.remove(report_file_permissions)
    ofa_admin.permissions.remove(report_ingest_permissions)


def set_data_analyst_permissions(apps, schema_editor):
    """Set Data Analyst permissions for the Reports app."""
    data_analyst = apps.get_model("auth", "Group").objects.get(name="Data Analyst")

    # Data Analyst should get view for ReportFiles
    report_file_permissions = get_permission_ids_for_model(
        "reports", "reportfile", filters=[view_permissions_q]
    )

    data_analyst.permissions.add(*report_file_permissions)


def unset_data_analyst_permissions(apps, schema_editor):
    """Unset Data Analyst permissions for the Reports app."""
    data_analyst = apps.get_model("auth", "Group").objects.get(name="Data Analyst")
    developer = apps.get_model("auth", "Group").objects.get(name="Developer")

    # Data Analyst should get view for ReportFiles
    report_file_permissions = get_permission_ids_for_model(
        "reports", "reportfile", filters=[view_permissions_q]
    )

    data_analyst.permissions.remove(*report_file_permissions)


def set_developer_permissions(apps, schema_editor):
    """Set Developer permissions for the Reports app."""
    developer = apps.get_model("auth", "Group").objects.get(name="Developer")

    # Developer should get all reports permissions
    report_file_permissions = get_permission_ids_for_model(
        "reports",
        "reportfile",
    )

    report_ingest_permissions = get_permission_ids_for_model(
        "reports",
        "reportingest",
    )

    developer.permissions.add(*report_file_permissions)
    developer.permissions.add(*report_ingest_permissions)


def unset_developer_permissions(apps, schema_editor):
    """Unset Developer permissions for the Reports app."""
    developer = apps.get_model("auth", "Group").objects.get(name="Developer")

    # Developer should get all reports permissions
    report_file_permissions = get_permission_ids_for_model(
        "reports",
        "reportfile",
    )

    report_ingest_permissions = get_permission_ids_for_model(
        "reports",
        "reportingest",
    )

    developer.permissions.remove(*report_file_permissions)
    developer.permissions.remove(*report_ingest_permissions)


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '__latest__'),
        ('users', '0050_feedback_addmetafields'),
    ]

    operations = [
        # Ensure permissions are created for the Reports app models
        migrations.RunPython(
            create_perms,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            set_ofa_admin_permissions,
            reverse_code=unset_ofa_admin_permissions
        ),
        migrations.RunPython(
            set_data_analyst_permissions,
            reverse_code=unset_data_analyst_permissions
        ),
        migrations.RunPython(
            set_developer_permissions,
            reverse_code=unset_developer_permissions
        ),
    ]
