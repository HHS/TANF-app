"""Grant OFA System Admin access to program participation reference data."""

from django.contrib.auth.management import create_permissions
from django.db import migrations


DEFAULT_ACTIONS = ("add", "change", "view")
ADMIN_MODELS = {
    "data_files": ("program", "section"),
    "stts": ("sttprogramparticipation",),
}


def create_model_permissions(apps, schema_editor):
    """Create permissions before assigning them in a fresh database."""
    for app_label in ADMIN_MODELS:
        app_config = apps.get_app_config(app_label)
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None


def add_ofa_system_admin_permissions(apps, schema_editor):
    """Grant the standard non-delete permissions for the new admin models."""
    permission_model = apps.get_model("auth", "Permission")
    permission_ids = []

    for app_label, model_names in ADMIN_MODELS.items():
        codenames = [
            f"{action}_{model_name}"
            for model_name in model_names
            for action in DEFAULT_ACTIONS
        ]
        permission_ids.extend(
            permission_model.objects.filter(
                content_type__app_label=app_label,
                content_type__model__in=model_names,
                codename__in=codenames,
            ).values_list("id", flat=True)
        )

    group, _ = apps.get_model("auth", "Group").objects.get_or_create(
        name="OFA System Admin"
    )
    group.permissions.add(*permission_ids)


class Migration(migrations.Migration):

    dependencies = [
        ("data_files", "0031_backfill_datafile_section_ref"),
        ("stts", "0014_populate_program_participations"),
        ("users", "0059_reconcile_role_permissions"),
    ]

    operations = [
        migrations.RunPython(
            create_model_permissions,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            add_ofa_system_admin_permissions,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
