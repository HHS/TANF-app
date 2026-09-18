from django.db import migrations


PROGRAMS = {
    "TAN": {
        "slug": "tanf",
        "name": "TANF",
        "sections": [
            "Active Case Data",
            "Closed Case Data",
            "Aggregate Data",
            "Stratum Data",
        ],
    },
    "SSP": {
        "slug": "ssp",
        "name": "SSP",
        "sections": [
            "Active Case Data",
            "Closed Case Data",
            "Aggregate Data",
            "Stratum Data",
        ],
    },
    "TRIBAL": {
        "slug": "tribal",
        "name": "Tribal TANF",
        "sections": [
            "Active Case Data",
            "Closed Case Data",
            "Aggregate Data",
            "Stratum Data",
        ],
    },
    "FRA": {
        "slug": "fra",
        "name": "FRA",
        "sections": [
            "Work Outcomes of TANF Exiters",
            "Secondary School Attainment",
            "Supplemental Work Outcomes",
        ],
    },
}


def ensure_canonical_sections(apps):
    Program = apps.get_model("data_files", "Program")
    Section = apps.get_model("data_files", "Section")

    canonical_sections = {}
    for code, program_data in PROGRAMS.items():
        program, _ = Program.objects.update_or_create(
            code=code,
            defaults={
                "slug": program_data["slug"],
                "name": program_data["name"],
            },
        )
        for section_name in program_data["sections"]:
            section, _ = Section.objects.get_or_create(
                program=program,
                name=section_name,
            )
            canonical_sections[(code, section_name)] = section.id

    return canonical_sections


def backfill_datafile_section_ref(apps, schema_editor):
    DataFile = apps.get_model("data_files", "DataFile")
    canonical_sections = ensure_canonical_sections(apps)

    legacy_values = set(
        DataFile.objects.values_list("program_type", "section").distinct()
    )
    unmapped_values = sorted(legacy_values - canonical_sections.keys())
    if unmapped_values:
        raise RuntimeError(
            "Cannot map legacy DataFile program/section values to canonical "
            f"sections: {unmapped_values}"
        )

    for (program_code, section_name), section_id in canonical_sections.items():
        data_files = DataFile.objects.filter(
            program_type=program_code,
            section=section_name,
        )
        inconsistent_ids = list(
            data_files.exclude(section_ref_id__isnull=True)
            .exclude(section_ref_id=section_id)
            .values_list("id", flat=True)
        )
        if inconsistent_ids:
            raise RuntimeError(
                "DataFile rows already reference a section that conflicts with "
                f"their legacy values: {inconsistent_ids}"
            )

        data_files.filter(section_ref_id__isnull=True).update(
            section_ref_id=section_id
        )


class Migration(migrations.Migration):

    dependencies = [
        ("data_files", "0030_datafile_section_ref"),
    ]

    operations = [
        migrations.RunPython(
            backfill_datafile_section_ref,
            migrations.RunPython.noop,
        ),
    ]
