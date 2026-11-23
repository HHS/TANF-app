"""Execute custom dashboard SQL against canonical models in isolated PostgreSQL."""

from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from django.apps import apps
from django.db import connection
from django.db.models import Model

import pytest

from plg.grafana_views import generate_views
from tdpservice.data_files.models import DataFile, Program, Section
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.search_indexes.models.fra import TANF_Exiter1
from tdpservice.stts.models import STT
from tdpservice.stts.test.factories import RegionFactory, STTFactory
from tdpservice.users.test.factories import UserFactory

pytestmark = pytest.mark.django_db

VIEWS_ROOT = Path(__file__).resolve().parents[1]
CUSTOM_VIEW_NAMES = (
    "latest_tanf_exiters_view_prod",
    "stt_section_to_type_mapping",
    "mr_record_counts_by_tableview",
)
PROGRAM_SOURCES = (
    (Program.Code.TANF, "tanf", "TANF_T", "t"),
    (Program.Code.SSP, "ssp", "SSP_M", "m"),
    (Program.Code.TRIBAL, "tribal_tanf", "Tribal_TANF_T", "t"),
)
RECORD_SECTIONS = (
    Section.Name.ACTIVE_CASE_DATA,
    Section.Name.ACTIVE_CASE_DATA,
    Section.Name.ACTIVE_CASE_DATA,
    Section.Name.CLOSED_CASE_DATA,
    Section.Name.CLOSED_CASE_DATA,
    Section.Name.AGGREGATE_DATA,
    Section.Name.STRATUM_DATA,
)


def apply_custom_view(name: str) -> None:
    """Execute the source definition, without a test-only SQL rewrite."""
    with connection.cursor() as cursor:
        cursor.execute((VIEWS_ROOT / "custom_views" / f"{name}.sql").read_text())


def query_rows(sql: str, params: tuple = ()) -> list[tuple]:
    """Fetch dashboard query results from the isolated test database."""
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()


@pytest.fixture
def make_file() -> Callable[..., DataFile]:
    """Create explicit modern file series without writing to object storage."""
    user = UserFactory.create()

    def create(**overrides: Any) -> DataFile:
        values = {
            "user": user,
            "file": None,
            "year": 2026,
            "quarter": "Q1",
            "version": 1,
            "program_type": Program.Code.FRA,
            "section": Section.Name.FRA_WORK_OUTCOMES,
        }
        values.update(overrides)
        return DataFileFactory.create(**values)

    return create


@pytest.fixture
def exiter_view() -> None:
    """Install only the real exiter definition for focused result tests."""
    apply_custom_view("latest_tanf_exiters_view_prod")


@pytest.fixture
def custom_views(tmp_path, monkeypatch) -> None:
    """Generate real prerequisites outside the checkout and install custom SQL."""
    for name in ("schema_fields.json", "helper_functions.sql"):
        (tmp_path / name).write_bytes((VIEWS_ROOT / name).read_bytes())
    monkeypatch.setattr(generate_views, "CWD", str(tmp_path))
    generate_views.main(False)
    with connection.cursor() as cursor:
        for path in sorted((tmp_path / "user_views").glob("*.sql")):
            cursor.execute(path.read_text())
    for name in CUSTOM_VIEW_NAMES:
        apply_custom_view(name)


def create_record(
    model_name: str, data_file: DataFile, number: int, **overrides: Any
) -> Model:
    """Create minimal parsed rows satisfying the generated record-view filters."""
    values = {"datafile": data_file, "RPT_MONTH_YEAR": 202601}
    if number <= 5:
        values["CASE_NUMBER"] = "CASE1"
    if number == 3:
        values.update(FAMILY_AFFILIATION=1, SEX=1)
    if number == 7:
        values.update(TDRS_SECTION_IND="4", STRATUM="01", FAMILIES_MONTH=1)
    values.update(overrides)
    return apps.get_model("search_indexes", model_name).objects.create(**values)


def test_exiters_select_latest_files_per_stt_and_period(
    exiter_view, make_file: Callable[..., DataFile]
) -> None:
    """Highest versions stay local to a file series and retain readable metadata."""
    stt = STTFactory.create(type=STT.EntityType.STATE, name="SQL state", stt_code="01")
    old = make_file(stt=stt)
    latest = make_file(stt=stt, version=2)
    other_quarter = make_file(stt=stt, quarter="Q2")
    cutoff = make_file(stt=stt, year=2025)
    other_stt = make_file(
        stt=STTFactory.create(type=STT.EntityType.TERRITORY, stt_code="02")
    )
    excluded = [
        old,
        make_file(stt=stt, year=2024),
        make_file(stt=stt, section=Section.Name.FRA_SECONDARY_SCHOOL_ATTAINMENT),
        make_file(stt=stt, program_type=Program.Code.TANF),
    ]
    for data_file in excluded + [latest, other_quarter, cutoff, other_stt]:
        TANF_Exiter1.objects.create(datafile=data_file, SSN="123456789", EXIT_DATE=202601)
    TANF_Exiter1.objects.create(datafile=latest, SSN="234567890", EXIT_DATE=None)
    TANF_Exiter1.objects.create(datafile=None, SSN="345678901", EXIT_DATE=202601)
    submitted = datetime(2026, 2, 1, 1, 30, tzinfo=timezone(timedelta(hours=2)))
    DataFile.objects.filter(pk=latest.pk).update(created_at=submitted)

    rows = query_rows(
        'SELECT datafile_id, "REGION", "STT", "STT_CODE", section, '
        '"FISCAL_YR", "FISCAL_QTR", submission_datetime '
        "FROM latest_tanf_exiters_view_prod"
    )

    assert Counter(row[0] for row in rows) == Counter(
        {latest.pk: 2, other_quarter.pk: 1, cutoff.pk: 1, other_stt.pk: 1}
    )
    assert next(row for row in rows if row[0] == latest.pk) == (
        latest.pk, stt.region_id, stt.name, "01", Section.Name.FRA_WORK_OUTCOMES,
        2026, "Q1", "2026-01-31 23:30:00",
    )
    make_file(stt=stt, version=3)
    assert not query_rows(
        'SELECT 1 FROM latest_tanf_exiters_view_prod WHERE "STT" = %s '
        'AND "FISCAL_YR" = 2026 AND "FISCAL_QTR" = \'Q1\'', (stt.name,)
    )


@pytest.mark.parametrize(
    "ssn,invalid",
    [(str(digit) * 9, 1) for digit in range(10)]
    + [("666123456", 1), ("912345678", 1), ("123456789", 0), (None, 0)],
)
def test_exiter_ssn_flags_preserve_invalid_and_null_rules(
    exiter_view, make_file: Callable[..., DataFile], ssn: str | None, invalid: int
) -> None:
    """Only valid non-null SSNs participate in same/cross-STT and adjacent flags."""
    data_file = make_file()
    other = make_file()
    for exit_date in (202601, 202602, 202605):
        TANF_Exiter1.objects.create(datafile=data_file, SSN=ssn, EXIT_DATE=exit_date)
    TANF_Exiter1.objects.create(datafile=other, SSN=ssn, EXIT_DATE=202601)
    rows = query_rows(
        'SELECT "EXIT_DATE", is_invalid_ssn, is_duplicate_ssn_xj, '
        "is_duplicate_ssn, is_duplicate_adjacent FROM latest_tanf_exiters_view_prod "
        'WHERE datafile_id = %s ORDER BY "EXIT_DATE"', (data_file.pk,)
    )
    duplicate = int(ssn is not None and not invalid)
    assert rows == [
        (202601, invalid, duplicate, duplicate, duplicate),
        (202602, invalid, duplicate, duplicate, duplicate),
        (202605, invalid, duplicate, duplicate, 0),
    ]
    assert query_rows(
        "SELECT is_invalid_ssn, is_duplicate_ssn_xj, is_duplicate_ssn, "
        "is_duplicate_adjacent FROM latest_tanf_exiters_view_prod WHERE datafile_id = %s",
        (other.pk,),
    ) == [(invalid, duplicate, 0, 0)]


@pytest.mark.parametrize("program,prefix,model_prefix,record_prefix", PROGRAM_SOURCES)
@pytest.mark.parametrize("number", range(1, 8))
def test_counts_cover_each_generated_source_and_latest_file(
    custom_views, make_file: Callable[..., DataFile], program: str, prefix: str,
    model_prefix: str, record_prefix: str, number: int,
) -> None:
    """Every source retains period/STT grouping, record counts and case semantics."""
    old = make_file(program_type=program, section=RECORD_SECTIONS[number - 1])
    latest = make_file(section=old.section, stt=old.stt, version=2)
    model_name = f"{model_prefix}{number}"
    for _ in range(5):
        create_record(model_name, old, number)
    for _ in range(2):
        create_record(model_name, latest, number)
    extra = {"CASE_NUMBER": "CASE2"} if number <= 5 else {}
    create_record(model_name, latest, number, **extra)
    create_record(model_name, latest, number, RPT_MONTH_YEAR=202602)
    other = make_file(program_type=program, section=old.section)
    create_record(model_name, other, number)

    source = f"{prefix}_{record_prefix}{number}"
    rows = query_rows(
        'SELECT program_type, section, record_type, "RPT_MONTH_YEAR", '
        '"STT", "STT_CODE", total_record_count, unique_case_count '
        "FROM mr_record_counts_by_tableview WHERE source_table = %s", (source,)
    )
    unique = 2 if number <= 5 else None
    single = 1 if number <= 5 else None
    assert set(rows) == {
        (program, old.section.name, f"{record_prefix}{number}", 202601,
         old.stt.name, old.stt.stt_code, 3, unique),
        (program, old.section.name, f"{record_prefix}{number}", 202602,
         old.stt.name, old.stt.stt_code, 1, single),
        (program, old.section.name, f"{record_prefix}{number}", 202601,
         other.stt.name, other.stt.stt_code, 1, single),
    }
    make_file(section=old.section, stt=old.stt, version=3)
    assert query_rows(
        'SELECT total_record_count FROM mr_record_counts_by_tableview '
        'WHERE source_table = %s AND "STT" = %s', (source, old.stt.name)
    ) == []


@pytest.mark.parametrize("program,prefix,model_prefix,record_prefix", PROGRAM_SOURCES)
@pytest.mark.parametrize(
    "number,excluded_fields",
    [
        (3, {"FAMILY_AFFILIATION": None}),
        (3, {"FAMILY_AFFILIATION": 0}),
        (3, {"SEX": None}),
        (3, {"SEX": 0}),
        (7, {"TDRS_SECTION_IND": None}),
        (7, {"TDRS_SECTION_IND": ""}),
        (7, {"FAMILIES_MONTH": None}),
        (7, {"FAMILIES_MONTH": 0}),
        (7, {"STRATUM": None}),
    ],
)
def test_counts_preserve_record_three_and_seven_filters(
    custom_views, make_file: Callable[..., DataFile], program: str, prefix: str,
    model_prefix: str, record_prefix: str, number: int, excluded_fields: dict,
) -> None:
    """Generated validity filters and the custom STRATUM null filter still apply."""
    data_file = make_file(program_type=program, section=RECORD_SECTIONS[number - 1])
    create_record(f"{model_prefix}{number}", data_file, number)
    create_record(f"{model_prefix}{number}", data_file, number, **excluded_fields)
    assert query_rows(
        "SELECT total_record_count FROM mr_record_counts_by_tableview "
        "WHERE source_table = %s", (f"{prefix}_{record_prefix}{number}",)
    ) == [(1,)]


def test_fra_counts_group_exit_dates_and_ignore_older_versions(
    custom_views, make_file: Callable[..., DataFile]
) -> None:
    """FRA uses EXIT_DATE as the reporting period and has no case count."""
    old = make_file()
    latest = make_file(stt=old.stt, version=2)
    TANF_Exiter1.objects.create(datafile=old, SSN="123456789", EXIT_DATE=202512)
    for exit_date in (202601, 202601, 202602):
        TANF_Exiter1.objects.create(datafile=latest, SSN="123456789", EXIT_DATE=exit_date)
    assert query_rows(
        'SELECT program_type, section, record_type, "RPT_MONTH_YEAR", '
        'total_record_count, unique_case_count FROM mr_record_counts_by_tableview '
        'ORDER BY "RPT_MONTH_YEAR"'
    ) == [
        ("FRA", Section.Name.FRA_WORK_OUTCOMES, "te1", 202601, 2, None),
        ("FRA", Section.Name.FRA_WORK_OUTCOMES, "te1", 202602, 1, None),
    ]
    make_file(stt=old.stt, version=3)
    assert query_rows("SELECT * FROM mr_record_counts_by_tableview") == []


def test_mapping_preserves_catalog_labels_and_per_stt_multiplicity() -> None:
    """The catalog is independent of submissions/participation and retains duplicates."""
    region = RegionFactory.create()
    entities = (STT.EntityType.STATE, STT.EntityType.STATE,
                STT.EntityType.TERRITORY, STT.EntityType.TRIBE)
    for index, entity in enumerate(entities):
        STTFactory.create(type=entity, region=region, stt_code=f"{index + 1:02}")
    STTFactory.create(type=None, region=region)
    apply_custom_view("stt_section_to_type_mapping")
    rows = query_rows(
        "SELECT * FROM stt_section_to_type_mapping WHERE region_id = %s", (region.pk,)
    )
    expected = []
    for entity in entities:
        for program, prefix, _, record_prefix in PROGRAM_SOURCES:
            allowed = (
                (program == "TAN" and entity in ("state", "territory"))
                or (program == "SSP" and entity == "state")
                or (program == "TRIBAL" and entity == "tribe")
            )
            if allowed:
                expected.extend(
                    (program, section, entity, region.pk, f"{record_prefix}{number}",
                     f"{prefix}_{record_prefix}{number}")
                    for number, section in enumerate(RECORD_SECTIONS, start=1)
                )
        if entity in ("state", "territory"):
            expected.append(("FRA", Section.Name.FRA_WORK_OUTCOMES, entity,
                             region.pk, "te1", "latest_tanf_exiters_view_prod"))
    assert Counter(rows) == Counter(expected)
    assert not DataFile.objects.exists()
    apply_custom_view("stt_section_to_type_mapping")
    assert Counter(query_rows(
        "SELECT * FROM stt_section_to_type_mapping WHERE region_id = %s", (region.pk,)
    )) == Counter(expected)


def test_custom_view_signatures_and_reapplication(custom_views, make_file) -> None:
    """Reapplying definitions retains public column names, types, and populated results."""
    data_file = make_file()
    TANF_Exiter1.objects.create(datafile=data_file, SSN="123456789", EXIT_DATE=202601)
    signatures = {
        "latest_tanf_exiters_view_prod": [
            ("REGION", "integer"), ("STT", "character varying(1000)"),
            ("STT_CODE", "character varying(3)"), ("section", "character varying(100)"),
            ("FISCAL_YR", "integer"), ("FISCAL_QTR", "character varying(16)"),
            ("datafile_id", "integer"), ("submission_datetime", "text"),
            ("EXIT_DATE", "integer"), ("SSN", "character varying(9)"),
            ("is_invalid_ssn", "integer"), ("is_duplicate_ssn_xj", "integer"),
            ("is_duplicate_ssn", "integer"), ("is_duplicate_adjacent", "integer"),
        ],
        "mr_record_counts_by_tableview": [
            ("program_type", "text"), ("section", "text"), ("record_type", "text"),
            ("source_table", "text"), ("RPT_MONTH_YEAR", "integer"),
            ("STT", "character varying(1000)"), ("STT_CODE", "character varying(3)"),
            ("total_record_count", "bigint"), ("unique_case_count", "bigint"),
        ],
        "stt_section_to_type_mapping": [
            ("program_type", "text"), ("section_id", "text"), ("stt_type", "text"),
            ("region_id", "integer"), ("record_type", "text"), ("table_view", "text"),
        ],
    }
    for name in CUSTOM_VIEW_NAMES:
        before = query_rows(f'SELECT * FROM public."{name}"')
        apply_custom_view(name)
        assert Counter(query_rows(f'SELECT * FROM public."{name}"')) == Counter(before)
        assert query_rows(
            "SELECT attname, format_type(atttypid, atttypmod) FROM pg_attribute "
            "WHERE attrelid = %s::regclass AND attnum > 0 AND NOT attisdropped "
            "ORDER BY attnum", (f"public.{name}",)
        ) == signatures[name]


def test_empty_custom_data_views(custom_views) -> None:
    """No submissions produce neither exiter rows nor synthetic zero counts."""
    assert query_rows("SELECT * FROM latest_tanf_exiters_view_prod") == []
    assert query_rows("SELECT * FROM mr_record_counts_by_tableview") == []
