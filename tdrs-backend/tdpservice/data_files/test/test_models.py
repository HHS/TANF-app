"""Module testing for data file model."""

import pytest
from django.core.exceptions import FieldDoesNotExist
from django.db import IntegrityError, transaction
from django.db.models.deletion import PROTECT, ProtectedError

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import (
    DataFile,
    Program,
    Section,
    ShadowDataFile,
    create_or_update_shadow_data_file,
)
from tdpservice.data_files.test.factories import DataFileFactory, canonical_section_for
from tdpservice.stts.models import STT


def _create_program(code="TEST", slug="test-program", name="Test Program"):
    """Create a test program without conflicting with canonical seed data."""
    return Program.objects.create(code=code, slug=slug, name=name)


@pytest.mark.django_db
def test_program_code_and_string_representation():
    """Programs expose their persisted code and display name."""
    program = _create_program()

    assert program.code == "TEST"
    assert str(program) == "Test Program"


def test_program_and_section_choices_define_the_static_catalog():
    """Program and section fields expose model-owned symbolic choices."""
    assert set(Program.Code.values) == {"TAN", "SSP", "TRIBAL", "FRA"}
    assert set(Section.Name.values) == {
        "Active Case Data",
        "Closed Case Data",
        "Aggregate Data",
        "Stratum Data",
        "Work Outcomes of TANF Exiters",
        "Secondary School Attainment",
        "Supplemental Work Outcomes",
    }
    assert DataFile._meta.get_field("section").remote_field.model is Section
    assert Program._meta.get_field("code").choices == Program.Code.choices
    assert Section._meta.get_field("name").choices == Section.Name.choices


@pytest.mark.django_db
def test_program_code_is_unique():
    """Program codes uniquely identify reporting programs."""
    _create_program()

    with pytest.raises(IntegrityError), transaction.atomic():
        _create_program(slug="another-program", name="Another Program")


@pytest.mark.django_db
def test_section_string_representation():
    """Sections display their program and section names."""
    program = _create_program()
    section = Section.objects.create(program=program, name="Active Case Data")

    assert str(section) == "Test Program - Active Case Data"


@pytest.mark.django_db
def test_section_name_is_unique_per_program():
    """Section names are unique within a program."""
    program = _create_program()
    Section.objects.create(program=program, name="Active Case Data")

    with pytest.raises(IntegrityError), transaction.atomic():
        Section.objects.create(program=program, name="Active Case Data")


@pytest.mark.django_db
def test_data_file_program_comes_from_section(data_file_instance):
    """Data files expose the program associated with their canonical section."""
    program = _create_program()
    section = Section.objects.create(program=program, name="Active Case Data")
    data_file_instance.section = section
    data_file_instance.save(update_fields=["section"])
    data_file_instance.refresh_from_db()

    assert data_file_instance.program == program


@pytest.mark.django_db
def test_data_file_section_is_required_and_protected(data_file_instance):
    """Every data file retains its canonical section."""
    field = DataFile._meta.get_field("section")

    assert field.null is False
    assert field.blank is False
    assert field.remote_field.on_delete is PROTECT
    with pytest.raises(ProtectedError):
        data_file_instance.section.delete()


def test_data_file_has_no_legacy_classification_fields():
    """Verify DataFile exposes only its canonical section and derived program."""
    assert not hasattr(DataFile, "ProgramType")
    assert not hasattr(DataFile, "Section")
    for field_name in ("program_type", "section_ref"):
        with pytest.raises(FieldDoesNotExist):
            DataFile._meta.get_field(field_name)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "program_type,section_name,is_program_audit",
    [
        (Program.Code.TANF, Section.Name.ACTIVE_CASE_DATA, False),
        (Program.Code.SSP, Section.Name.CLOSED_CASE_DATA, False),
        (Program.Code.TRIBAL, Section.Name.AGGREGATE_DATA, False),
        (Program.Code.FRA, Section.Name.FRA_WORK_OUTCOMES, False),
        (Program.Code.TANF, Section.Name.ACTIVE_CASE_DATA, True),
    ],
)
def test_data_file_factory_resolves_canonical_section(
    program_type, section_name, is_program_audit
):
    """The factory resolves convenient scalar inputs to canonical sections."""
    data_file = DataFileFactory.create(
        program_type=program_type,
        section=section_name,
        is_program_audit=is_program_audit,
    )

    assert data_file.program.code == program_type
    assert data_file.section.name == section_name
    assert data_file.is_program_audit is is_program_audit


@pytest.mark.django_db
def test_data_file_uniqueness_uses_canonical_section(data_file_instance):
    """A canonical section identifies the classification in the file key."""
    with pytest.raises(IntegrityError), transaction.atomic():
        DataFileFactory.create(
            section=data_file_instance.section,
            stt=data_file_instance.stt,
            year=data_file_instance.year,
            quarter=data_file_instance.quarter,
            version=data_file_instance.version,
            is_program_audit=data_file_instance.is_program_audit,
        )


@pytest.mark.django_db
def test_shadow_data_file_uses_canonical_section():
    """Shadow rows share production's required, protected classification."""
    data_file = DataFileFactory.create()

    shadow_data_file = create_or_update_shadow_data_file(data_file)

    assert shadow_data_file.section == data_file.section
    assert shadow_data_file.program == data_file.program
    field = ShadowDataFile._meta.get_field("section")
    assert field.null is False
    assert field.remote_field.on_delete is PROTECT
    with pytest.raises(FieldDoesNotExist):
        ShadowDataFile._meta.get_field("program_type")

    data_file.delete()
    with pytest.raises(ProtectedError):
        shadow_data_file.section.delete()


@pytest.mark.django_db
def test_create_new_data_file_version(data_file_instance):
    """Test version incrementing logic for data files."""
    new_version = DataFile.create_new_version(
        {
            "year": data_file_instance.year,
            "quarter": data_file_instance.quarter,
            "section": data_file_instance.section,
            "stt": data_file_instance.stt,
            "original_filename": data_file_instance.original_filename,
            "slug": data_file_instance.slug,
            "extension": data_file_instance.extension,
            "user": data_file_instance.user,
            "is_program_audit": data_file_instance.is_program_audit,
        }
    )
    assert new_version.version == data_file_instance.version + 1
    assert new_version.program == data_file_instance.program
    assert new_version.section == data_file_instance.section


@pytest.mark.django_db
def test_find_latest_version(data_file_instance):
    """Test method to find latest version."""
    new_data_file = DataFile.create_new_version(
        {
            "year": data_file_instance.year,
            "quarter": data_file_instance.quarter,
            "section": data_file_instance.section,
            "stt": data_file_instance.stt,
            "original_filename": data_file_instance.original_filename,
            "slug": data_file_instance.slug,
            "extension": data_file_instance.extension,
            "user": data_file_instance.user,
            "is_program_audit": data_file_instance.is_program_audit,
        }
    )

    latest_data_file = DataFile.find_latest_version(
        year=data_file_instance.year,
        quarter=data_file_instance.quarter,
        section=data_file_instance.section,
        stt=data_file_instance.stt.id,
        is_program_audit=data_file_instance.is_program_audit,
    )
    assert latest_data_file.version == new_data_file.version


@pytest.mark.django_db
def test_find_latest_version_number(data_file_instance):
    """Test method to find latest version number."""
    new_data_file = DataFile.create_new_version(
        {
            "year": data_file_instance.year,
            "quarter": data_file_instance.quarter,
            "section": data_file_instance.section,
            "stt": data_file_instance.stt,
            "original_filename": data_file_instance.original_filename,
            "slug": data_file_instance.slug,
            "extension": data_file_instance.extension,
            "user": data_file_instance.user,
            "is_program_audit": data_file_instance.is_program_audit,
        }
    )

    latest_version = DataFile.find_latest_version_number(
        year=data_file_instance.year,
        quarter=data_file_instance.quarter,
        section=data_file_instance.section,
        stt=data_file_instance.stt.id,
        is_program_audit=data_file_instance.is_program_audit,
    )
    assert latest_version == new_data_file.version


@pytest.mark.django_db
def test_data_files_filename_is_expected(user):
    """Test that the file name matches the file name expected based on the stt of each data file."""
    all_stts = STT.objects.all()

    if all_stts.count == 0:
        raise Exception("There are no stts, the test is invalid.")
    for stt in all_stts.iterator():
        for section in Section.objects.select_related("program"):
            expected_filename = stt.filenames.get(section.name)
            if expected_filename is None:
                program_name = (
                    section.program.code.title()
                    if section.program.code == "TRIBAL"
                    else section.program.code
                )
                expected_filename = stt.filenames.get(f"{program_name} {section.name}")
            if expected_filename is None:
                continue
            new_data_file = DataFile.create_new_version(
                {
                    "year": 2020,
                    "quarter": "Q1",
                    "section": section,
                    "user": user,
                    "stt": stt,
                    "is_program_audit": False,
                }
            )
            assert new_data_file.filename == expected_filename


@pytest.mark.django_db
@pytest.mark.parametrize(
    "program_type, filenames, expected_filename",
    [
        (
            Program.Code.SSP,
            {"Active Case Data": "section-based-ssp.txt"},
            "section-based-ssp.txt",
        ),
        (
            Program.Code.TRIBAL,
            {"Active Case Data": "section-based-tribal.txt"},
            "section-based-tribal.txt",
        ),
        (
            Program.Code.SSP,
            {"SSP Active Case Data": "legacy-ssp.txt"},
            "legacy-ssp.txt",
        ),
        (
            Program.Code.TRIBAL,
            {"Tribal Active Case Data": "legacy-tribal.txt"},
            "legacy-tribal.txt",
        ),
    ],
)
def test_data_files_filename_prefers_section_key_with_legacy_fallback(
    user, program_type, filenames, expected_filename
):
    """File name lookup supports section keys and legacy prefixed keys."""
    stt = STT.objects.create(
        name=f"Filename Lookup {program_type} {expected_filename}",
        filenames=filenames,
    )
    data_file = DataFile.create_new_version(
        {
            "year": 2020,
            "quarter": "Q1",
            "section": canonical_section_for(program_type, "Active Case Data"),
            "user": user,
            "stt": stt,
            "is_program_audit": False,
        }
    )

    assert data_file.filename == expected_filename


@pytest.mark.django_db
@pytest.mark.parametrize(
    "section, program_type",
    [
        ("Closed Case Data", "TRIBAL"),
        ("Active Case Data", "TRIBAL"),
        ("Aggregate Data", "SSP"),
        ("Closed Case Data", "SSP"),
        ("Active Case Data", "TAN"),
        ("Aggregate Data", "TAN"),
        ("Work Outcomes of TANF Exiters", "FRA"),
        ("Secondary School Attainment", "FRA"),
        ("Supplemental Work Outcomes", "FRA"),
    ],
)
def test_prog_type(base_data_file_data, data_analyst, stt, section, program_type):
    """Test proper prog_type."""
    df = DataFile.create_new_version(
        {
            "year": base_data_file_data["year"],
            "quarter": base_data_file_data["quarter"],
            "section": canonical_section_for(program_type, section),
            "stt": stt,
            "original_filename": base_data_file_data["original_filename"],
            "slug": base_data_file_data["slug"],
            "extension": base_data_file_data["extension"],
            "user": data_analyst,
            "is_program_audit": False,
        }
    )

    assert df.section.name == section
    assert df.program.code == program_type


@pytest.mark.django_db
def test_fiscal_year(data_file_instance):
    """Test property fiscal_year."""
    df = DataFile.create_new_version(
        {
            "year": data_file_instance.year,
            "quarter": data_file_instance.quarter,
            "section": data_file_instance.section,
            "stt": data_file_instance.stt,
            "original_filename": data_file_instance.original_filename,
            "slug": data_file_instance.slug,
            "extension": data_file_instance.extension,
            "user": data_file_instance.user,
            "is_program_audit": False,
        }
    )

    assert df.fiscal_year == "2020 - Q1 (Oct - Dec)"
    df.quarter = "Q2"
    assert df.fiscal_year == "2020 - Q2 (Jan - Mar)"
    df.quarter = "Q3"
    assert df.fiscal_year == "2020 - Q3 (Apr - Jun)"
    df.quarter = "Q4"
    assert df.fiscal_year == "2020 - Q4 (Jul - Sep)"


@pytest.mark.django_db
def test_data_file_defaults_to_uploaded_submission_state(data_file_instance):
    """Test new data files default to the uploaded submission state."""
    df = DataFile.create_new_version(
        {
            "year": data_file_instance.year,
            "quarter": data_file_instance.quarter,
            "section": data_file_instance.section,
            "stt": data_file_instance.stt,
            "original_filename": data_file_instance.original_filename,
            "slug": data_file_instance.slug,
            "extension": data_file_instance.extension,
            "user": data_file_instance.user,
            "is_program_audit": data_file_instance.is_program_audit,
        }
    )

    assert df.state == SubmissionState.UPLOADED


def test_submission_state_enum_matches_parsing_refactor_writeup():
    """Test the durable submission lifecycle states are defined on the enum."""
    assert list(SubmissionState.values) == [
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
