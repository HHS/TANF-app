import django.utils.timezone
from django.db import migrations, models
from django.db.models import F


SUBMISSION_STATES = [
    "uploaded",
    "virus_scan_started",
    "virus_scan_failed",
    "virus_scan_completed",
    "reparse_requested",
    "parse_started",
    "parse_failed",
    "parsed_with_errors",
    "parse_completed",
    "stuck",
    "completed",
    "canceled",
]


def backfill_state_changed_at(apps, schema_editor):
    """Use creation time as the best available legacy state timestamp."""
    DataFile = apps.get_model("data_files", "DataFile")
    ShadowDataFile = apps.get_model("data_files", "ShadowDataFile")
    DataFile.objects.update(state_changed_at=F("created_at"))
    ShadowDataFile.objects.update(state_changed_at=F("created_at"))


class Migration(migrations.Migration):
    dependencies = [
        ("data_files", "0031_backfill_datafile_section_ref"),
    ]

    operations = [
        migrations.AddField(
            model_name="datafile",
            name="state_changed_at",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="shadowdatafile",
            name="state_changed_at",
            field=models.DateTimeField(null=True),
        ),
        migrations.RunPython(backfill_state_changed_at, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="datafile",
            name="state_changed_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="shadowdatafile",
            name="state_changed_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name="datafile",
            name="current_parse_token",
            field=models.UUIDField(blank=True, editable=False, null=True),
        ),
        migrations.AddConstraint(
            model_name="datafile",
            constraint=models.CheckConstraint(
                condition=models.Q(("state__in", SUBMISSION_STATES)),
                name="datafile_valid_submission_state",
            ),
        ),
    ]
