from django.db import migrations, models


PROGRAM_CODES = {"TAN", "SSP", "TRIBAL", "FRA"}
SECTION_NAMES = {
    "Active Case Data",
    "Closed Case Data",
    "Aggregate Data",
    "Stratum Data",
    "Work Outcomes of TANF Exiters",
    "Secondary School Attainment",
    "Supplemental Work Outcomes",
}


def validate_program_and_section_values(apps, schema_editor):
    Program = apps.get_model("data_files", "Program")
    Section = apps.get_model("data_files", "Section")

    unknown_program_codes = sorted(
        Program.objects.exclude(code__in=PROGRAM_CODES).values_list(
            "code", flat=True
        )
    )
    unknown_section_names = sorted(
        Section.objects.exclude(name__in=SECTION_NAMES).values_list(
            "name", flat=True
        )
    )

    if unknown_program_codes or unknown_section_names:
        raise RuntimeError(
            "Cannot constrain Program and Section fields with unknown values: "
            f"programs={unknown_program_codes}, sections={unknown_section_names}"
        )


class Migration(migrations.Migration):

    dependencies = [
        ("data_files", "0035_replace_datafile_classification_fields"),
    ]

    operations = [
        migrations.RunPython(
            validate_program_and_section_values,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="program",
            name="code",
            field=models.CharField(
                choices=[
                    ("TAN", "TANF"),
                    ("SSP", "SSP"),
                    ("TRIBAL", "Tribal TANF"),
                    ("FRA", "FRA"),
                ],
                max_length=32,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="section",
            name="name",
            field=models.CharField(
                choices=[
                    ("Active Case Data", "Active Case Data"),
                    ("Closed Case Data", "Closed Case Data"),
                    ("Aggregate Data", "Aggregate Data"),
                    ("Stratum Data", "Stratum Data"),
                    (
                        "Work Outcomes of TANF Exiters",
                        "Work Outcomes of TANF Exiters",
                    ),
                    (
                        "Secondary School Attainment",
                        "Secondary School Attainment",
                    ),
                    (
                        "Supplemental Work Outcomes",
                        "Supplemental Work Outcomes",
                    ),
                ],
                max_length=100,
            ),
        ),
    ]
