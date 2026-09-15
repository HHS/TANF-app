"""Module testing for data file model."""

import pytest
from django.db import IntegrityError, transaction

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import DataFile, Program, Section
from tdpservice.data_files.test.factories import DataFileFactory
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
def test_data_file_program_comes_from_section_ref(data_file_instance):
    """Data files expose the program associated with their canonical section."""
    program = _create_program()
    section = Section.objects.create(program=program, name="Active Case Data")
    data_file_instance.section_ref = section
    data_file_instance.save(update_fields=["section_ref"])
    data_file_instance.refresh_from_db()

    assert data_file_instance.program == program


@pytest.mark.django_db
def test_data_file_program_is_none_without_section_ref(data_file_instance):
    """Data files without a canonical section do not expose a program."""
    data_file_instance.section_ref = None

    assert data_file_instance.section_ref is None
    assert data_file_instance.program is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    "program_type,section_name,is_program_audit",
    [
        (DataFile.ProgramType.TANF, DataFile.Section.ACTIVE_CASE_DATA, False),
        (DataFile.ProgramType.SSP, DataFile.Section.CLOSED_CASE_DATA, False),
        (DataFile.ProgramType.TRIBAL, DataFile.Section.AGGREGATE_DATA, False),
        (
            DataFile.ProgramType.FRA,
            DataFile.Section.FRA_WORK_OUTCOME_TANF_EXITERS,
            False,
        ),
        (DataFile.ProgramType.TANF, DataFile.Section.ACTIVE_CASE_DATA, True),
    ],
)
def test_new_data_file_resolves_section_ref(
    program_type, section_name, is_program_audit
):
    """Normal ORM writes resolve canonical sections without changing legacy data."""
    data_file = DataFileFactory.create(
        program_type=program_type,
        section=section_name,
        is_program_audit=is_program_audit,
    )

    assert data_file.section_ref.program.code == program_type
    assert data_file.section_ref.name == section_name
    assert data_file.program_type == program_type
    assert data_file.section == section_name
    assert data_file.is_program_audit is is_program_audit


@pytest.mark.django_db
def test_create_new_data_file_version(data_file_instance):
    """Test version incrementing logic for data files."""
    new_version = DataFile.create_new_version(
        {
            "year": data_file_instance.year,
            "quarter": data_file_instance.quarter,
            "section": data_file_instance.section,
            "program_type": data_file_instance.program_type,
            "stt": data_file_instance.stt,
            "original_filename": data_file_instance.original_filename,
            "slug": data_file_instance.slug,
            "extension": data_file_instance.extension,
            "user": data_file_instance.user,
            "is_program_audit": data_file_instance.is_program_audit,
        }
    )
    assert new_version.version == data_file_instance.version + 1
    assert new_version.section_ref.program.code == data_file_instance.program_type
    assert new_version.section_ref.name == data_file_instance.section


@pytest.mark.django_db
def test_find_latest_version(data_file_instance):
    """Test method to find latest version."""
    new_data_file = DataFile.create_new_version(
        {
            "year": data_file_instance.year,
            "quarter": data_file_instance.quarter,
            "section": data_file_instance.section,
            "program_type": data_file_instance.program_type,
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
        program_type=data_file_instance.program_type,
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
            "program_type": data_file_instance.program_type,
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
        program_type=data_file_instance.program_type,
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
        for section in stt.filenames:
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
            assert new_data_file.filename == stt.filenames[section]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "program_type, filenames, expected_filename",
    [
        (
            DataFile.ProgramType.SSP,
            {"Active Case Data": "section-based-ssp.txt"},
            "section-based-ssp.txt",
        ),
        (
            DataFile.ProgramType.TRIBAL,
            {"Active Case Data": "section-based-tribal.txt"},
            "section-based-tribal.txt",
        ),
        (
            DataFile.ProgramType.SSP,
            {"SSP Active Case Data": "legacy-ssp.txt"},
            "legacy-ssp.txt",
        ),
        (
            DataFile.ProgramType.TRIBAL,
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
            "section": "Active Case Data",
            "program_type": program_type,
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
            "section": section,
            "program_type": program_type,
            "stt": stt,
            "original_filename": base_data_file_data["original_filename"],
            "slug": base_data_file_data["slug"],
            "extension": base_data_file_data["extension"],
            "user": data_analyst,
            "is_program_audit": False,
        }
    )

    assert df.section == section
    assert df.program_type == program_type


@pytest.mark.django_db
def test_fiscal_year(data_file_instance):
    """Test property fiscal_year."""
    df = DataFile.create_new_version(
        {
            "year": data_file_instance.year,
            "quarter": data_file_instance.quarter,
            "section": data_file_instance.section,
            "program_type": data_file_instance.program_type,
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
            "program_type": data_file_instance.program_type,
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
