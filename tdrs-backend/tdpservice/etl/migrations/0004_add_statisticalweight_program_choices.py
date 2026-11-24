from django.db import migrations, models


PROGRAM_CODES = {"TAN", "SSP", "TRIBAL", "FRA"}


def validate_statistical_weight_programs(apps, schema_editor):
    StatisticalWeight = apps.get_model("etl", "StatisticalWeight")
    unknown_program_codes = sorted(
        StatisticalWeight.objects.exclude(program__in=PROGRAM_CODES)
        .values_list("program", flat=True)
        .distinct()
    )
    if unknown_program_codes:
        raise RuntimeError(
            "Cannot constrain StatisticalWeight.program with unknown values: "
            f"{unknown_program_codes}"
        )


class Migration(migrations.Migration):

    dependencies = [
        ("etl", "0003_alter_statisticalweight_program"),
    ]

    operations = [
        migrations.RunPython(
            validate_statistical_weight_programs,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="statisticalweight",
            name="program",
            field=models.CharField(
                choices=[
                    ("TAN", "TANF"),
                    ("SSP", "SSP"),
                    ("TRIBAL", "Tribal TANF"),
                    ("FRA", "FRA"),
                ],
                max_length=16,
            ),
        ),
    ]
