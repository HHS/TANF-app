from django.db import migrations


PRIMARY_PROGRAM_CODES = {
    "state": "TAN",
    "territory": "TAN",
    "tribe": "TRIBAL",
}
PROGRAM_PREFIXES = {
    "SSP": ("SSP ",),
    "TRIBAL": ("TRIBAL TANF ", "TRIBAL "),
}


def section_names_for_program(stt, program_code, canonical_names):
    section_names = set()
    prefixes = PROGRAM_PREFIXES.get(program_code, ())

    for section_name in (stt.filenames or {}):
        upper_name = section_name.upper()
        if program_code == "TAN":
            if any(
                upper_name.startswith(prefix)
                for prefixes in PROGRAM_PREFIXES.values()
                for prefix in prefixes
            ):
                continue
            normalized_name = section_name
        else:
            matching_prefix = next(
                (prefix for prefix in prefixes if upper_name.startswith(prefix)),
                None,
            )
            if matching_prefix is None:
                continue
            normalized_name = section_name[len(matching_prefix) :]

        if normalized_name in canonical_names:
            section_names.add(normalized_name)

    return section_names


def set_participation_sections(participation, program, stt):
    canonical_sections = {
        section.name: section for section in program.sections.all()
    }
    section_names = section_names_for_program(
        stt,
        program.code,
        canonical_sections,
    )
    if not section_names:
        raise RuntimeError(
            f"No {program.code} sections could be resolved for STT {stt.id}."
        )

    participation.sections.set(
        [canonical_sections[section_name] for section_name in section_names]
    )


def populate_program_participations(apps, schema_editor):
    Program = apps.get_model("data_files", "Program")
    STT = apps.get_model("stts", "STT")
    SttProgramParticipation = apps.get_model("stts", "SttProgramParticipation")

    programs = {
        program.code: program
        for program in Program.objects.filter(code__in=["TAN", "SSP", "TRIBAL"])
    }
    missing_programs = {"TAN", "SSP", "TRIBAL"} - programs.keys()
    if missing_programs:
        raise RuntimeError(
            f"Canonical programs are missing: {sorted(missing_programs)}"
        )

    for stt in STT.objects.all():
        primary_program_code = PRIMARY_PROGRAM_CODES.get(stt.type)
        if primary_program_code:
            primary_participation, _ = SttProgramParticipation.objects.update_or_create(
                stt=stt,
                program=programs[primary_program_code],
                defaults={"status": "ACTIVE"},
            )
            set_participation_sections(
                primary_participation,
                programs[primary_program_code],
                stt,
            )

        ssp_participation = SttProgramParticipation.objects.filter(
            stt=stt,
            program=programs["SSP"],
        ).first()
        if stt.ssp is True:
            ssp_participation, _ = SttProgramParticipation.objects.update_or_create(
                stt=stt,
                program=programs["SSP"],
                defaults={"status": "ACTIVE"},
            )

        if ssp_participation is not None:
            set_participation_sections(
                ssp_participation,
                programs["SSP"],
                stt,
            )


class Migration(migrations.Migration):

    dependencies = [
        ("data_files", "0031_backfill_datafile_section_ref"),
        ("stts", "0013_program_section_sttprogramparticipation"),
    ]

    operations = [
        migrations.RunPython(
            populate_program_participations,
            migrations.RunPython.noop,
        ),
    ]
