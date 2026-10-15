from django.db import migrations, models
import django.db.models.deletion


def validate_canonical_sections(apps, schema_editor):
    DataFile = apps.get_model("data_files", "DataFile")

    null_section_ids = list(
        DataFile.objects.filter(section_ref_id__isnull=True).values_list(
            "id", flat=True
        )
    )
    if null_section_ids:
        raise RuntimeError(
            "DataFile rows are missing canonical sections: "
            f"{null_section_ids}"
        )

    mismatched_ids = list(
        DataFile.objects.exclude(
            program_type=models.F("section_ref__program__code"),
            section=models.F("section_ref__name"),
        ).values_list("id", flat=True)
    )
    if mismatched_ids:
        raise RuntimeError(
            "DataFile rows have canonical sections that conflict with legacy "
            f"values: {mismatched_ids}"
        )


FORWARD_SQL = """
ALTER TABLE data_files_datafile DROP COLUMN program_type CASCADE;
ALTER TABLE data_files_datafile DROP COLUMN section CASCADE;
ALTER TABLE data_files_datafile ALTER COLUMN section_ref_id SET NOT NULL;
ALTER TABLE data_files_datafile RENAME COLUMN section_ref_id TO section_id;
"""

REVERSE_SQL = """
ALTER TABLE data_files_datafile RENAME COLUMN section_id TO section_ref_id;
ALTER TABLE data_files_datafile ALTER COLUMN section_ref_id DROP NOT NULL;
ALTER TABLE data_files_datafile ADD COLUMN section varchar(32);
ALTER TABLE data_files_datafile ADD COLUMN program_type varchar(32);
UPDATE data_files_datafile AS data_file
SET section = canonical_section.name,
    program_type = program.code
FROM data_files_section AS canonical_section
INNER JOIN data_files_program AS program
    ON program.id = canonical_section.program_id
WHERE canonical_section.id = data_file.section_ref_id;
ALTER TABLE data_files_datafile ALTER COLUMN section SET NOT NULL;
ALTER TABLE data_files_datafile ALTER COLUMN program_type SET NOT NULL;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("data_files", "0034_alter_shadowdatafile_classification_fields"),
    ]

    operations = [
        migrations.RunPython(
            validate_canonical_sections,
            migrations.RunPython.noop,
        ),
        migrations.RemoveConstraint(
            model_name="datafile",
            name="constraint_name",
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(FORWARD_SQL, REVERSE_SQL),
            ],
            state_operations=[
                migrations.RemoveField(
                    model_name="datafile",
                    name="program_type",
                ),
                migrations.RemoveField(
                    model_name="datafile",
                    name="section",
                ),
                migrations.AlterField(
                    model_name="datafile",
                    name="section_ref",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="data_files",
                        to="data_files.section",
                    ),
                ),
                migrations.RenameField(
                    model_name="datafile",
                    old_name="section_ref",
                    new_name="section",
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="datafile",
            constraint=models.UniqueConstraint(
                fields=(
                    "section",
                    "version",
                    "quarter",
                    "year",
                    "stt",
                    "is_program_audit",
                ),
                name="constraint_name",
            ),
        ),
    ]
