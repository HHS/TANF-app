"""Load de-identified statistical weights CSV extracts into parsed tables."""

from __future__ import annotations

import csv
import gzip
import lzma
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import models
from django.utils.text import slugify

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import DataFile
from tdpservice.search_indexes.models.tanf import TANF_T1, TANF_T6, TANF_T7
from tdpservice.stts.models import STT
from tdpservice.users.models import User

IMPORT_PREFIX = "etl-test-statistical-weights"
IMPORT_USERNAME = "etl-test-data-importer@example.com"
DEFAULT_DATA_DIR = Path("tdpservice/etl/test/data")
DEFAULT_VERSION = 9001


@dataclass(frozen=True)
class CsvSpec:
    """A DataSurge CSV file that can be imported for weights testing."""

    key: str
    patterns: tuple[str, ...]
    record_type: str
    model: type[models.Model]
    section: str


CSV_SPECS = (
    CsvSpec(
        key="t1",
        patterns=("TANF_T1_*.csv.xz", "TANF_T1_*.csv.gz", "TANF_T1_*.csv"),
        record_type="T1",
        model=TANF_T1,
        section=DataFile.Section.ACTIVE_CASE_DATA,
    ),
    CsvSpec(
        key="t6",
        patterns=("TANF_T6_*.csv.xz", "TANF_T6_*.csv.gz", "TANF_T6_*.csv"),
        record_type="T6",
        model=TANF_T6,
        section=DataFile.Section.AGGREGATE_DATA,
    ),
    CsvSpec(
        key="t7",
        patterns=("TANF_T7_*.csv.xz", "TANF_T7_*.csv.gz", "TANF_T7_*.csv"),
        record_type="T7",
        model=TANF_T7,
        section=DataFile.Section.STRATUM_DATA,
    ),
)


class Command(BaseCommand):
    """Load de-identified TANF T1/T6/T7 CSVs for weights testing."""

    help = (
        "Load DataSurge TANF T1/T6/T7 CSV extracts into parsed record tables "
        "with synthetic parse-completed DataFiles."
    )

    def add_arguments(self, parser):
        """Register command-line arguments."""
        parser.add_argument(
            "--data-dir",
            default=str(DEFAULT_DATA_DIR),
            help=(
                "Directory containing TANF_T1, TANF_T6, and TANF_T7 CSV, "
                "CSV.GZ, or CSV.XZ files."
            ),
        )
        parser.add_argument(
            "--fiscal-year",
            type=int,
            default=2024,
            help="Federal fiscal year represented by the CSV files.",
        )
        parser.add_argument(
            "--datafile-version",
            dest="version",
            type=int,
            default=DEFAULT_VERSION,
            help=(
                "Synthetic DataFile version to create. Keep this higher than "
                "normal upload versions so the ETL uses the fixture data."
            ),
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=10000,
            help="Parsed-record bulk insert batch size.",
        )
        parser.add_argument(
            "--limit-per-file",
            type=int,
            default=None,
            help="Optional row limit per CSV for smoke testing the importer.",
        )
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Delete a previous synthetic import for this year/version first.",
        )
        parser.add_argument(
            "--populate-stts",
            action="store_true",
            help="Run populate_stts before importing if local STTs are missing.",
        )

    def handle(self, *args, **options):
        """Load the CSV files into parsed TANF tables."""
        self.fiscal_year = options["fiscal_year"]
        self.version = options["version"]
        self.batch_size = options["batch_size"]
        self.limit_per_file = options["limit_per_file"]
        self.datafile_ids: dict[tuple[str, str, str], int] = {}

        data_dir = Path(options["data_dir"]).expanduser()
        if not data_dir.exists():
            raise CommandError(f"Data directory does not exist: {data_dir}")

        if options["populate_stts"]:
            call_command("populate_stts")

        existing_import = self._imported_datafiles()
        if existing_import.exists():
            if not options["replace"]:
                raise CommandError(
                    "Synthetic statistical weights test data already exists for "
                    f"FY{self.fiscal_year} version {self.version}. Pass --replace "
                    "to remove and reload it."
                )
            deleted_count, _ = existing_import.delete()
            self.stdout.write(f"Deleted {deleted_count} previous import records.")

        self.stts_by_code = self._stts_by_code()
        importer = self._import_user()
        totals: dict[str, int] = {}

        for spec in CSV_SPECS:
            csv_path = self._single_csv_path(data_dir, spec)
            totals[spec.key] = self._load_csv(csv_path, spec, importer)

        self.stdout.write(
            self.style.SUCCESS(
                "Loaded statistical weights test data: "
                f"T1={totals['t1']}, T6={totals['t6']}, T7={totals['t7']}, "
                f"DataFiles={len(self.datafile_ids)}."
            )
        )

    def _imported_datafiles(self):
        """Return synthetic DataFiles created by this importer."""
        return DataFile.objects.filter(
            original_filename__startswith=IMPORT_PREFIX,
            program_type=DataFile.ProgramType.TANF,
            year=self.fiscal_year,
            version=self.version,
        )

    def _stts_by_code(self) -> dict[str, STT]:
        """Return STTs keyed by normalized two-digit STT code."""
        stts = {
            self._normalize_stt_code(stt.stt_code): stt
            for stt in STT.objects.exclude(stt_code__isnull=True)
            if stt.stt_code
        }
        if not stts:
            raise CommandError(
                "No STTs are available. Run populate_stts first, or pass "
                "--populate-stts to this command."
            )
        return stts

    def _import_user(self) -> User:
        """Return the service user used for synthetic DataFiles."""
        user = User.objects.filter(username=IMPORT_USERNAME).first()
        if user:
            return user

        user = User(
            username=IMPORT_USERNAME,
            email=IMPORT_USERNAME,
            first_name="ETL",
            last_name="Test Importer",
            is_active=False,
        )
        user.set_unusable_password()
        user.save()
        return user

    def _single_csv_path(self, data_dir: Path, spec: CsvSpec) -> Path:
        """Find the one CSV path for a configured import spec."""
        for pattern in spec.patterns:
            paths = sorted(data_dir.glob(pattern))
            if len(paths) == 1:
                return paths[0]
            if len(paths) > 1:
                raise CommandError(
                    f"Expected one {pattern} file in {data_dir}; found {len(paths)}."
                )

        patterns = ", ".join(spec.patterns)
        raise CommandError(f"No {patterns} file found in {data_dir}.")

    def _load_csv(self, csv_path: Path, spec: CsvSpec, importer: User) -> int:
        """Stream one CSV into its parsed-record table."""
        loaded_count = 0
        batch: list[models.Model] = []

        with self._open_csv(csv_path) as csv_file:
            reader = csv.DictReader(csv_file)
            model_fields = self._model_fields(spec.model)
            csv_fields = self._validated_csv_fields(csv_path, reader, model_fields)

            for line_number, row in enumerate(reader, start=2):
                if self.limit_per_file and loaded_count >= self.limit_per_file:
                    break

                datafile_id = self._datafile_id_for_row(spec, row, importer)
                values = self._record_values(row, csv_fields, model_fields)
                values.update(
                    {
                        "RecordType": spec.record_type,
                        "line_number": line_number,
                        "datafile_id": datafile_id,
                    }
                )
                batch.append(spec.model(**values))
                loaded_count += 1

                if len(batch) >= self.batch_size:
                    spec.model.objects.bulk_create(batch, batch_size=self.batch_size)
                    batch = []
                    self._write_progress(spec, loaded_count)

        if batch:
            spec.model.objects.bulk_create(batch, batch_size=self.batch_size)
            self._write_progress(spec, loaded_count)

        return loaded_count

    def _open_csv(self, csv_path: Path) -> TextIO:
        """Open plain or stdlib-compressed CSV input."""
        if csv_path.suffix == ".xz":
            return lzma.open(csv_path, mode="rt", newline="", encoding="utf-8-sig")
        if csv_path.suffix == ".gz":
            return gzip.open(csv_path, mode="rt", newline="", encoding="utf-8-sig")
        return csv_path.open(newline="", encoding="utf-8-sig")

    def _model_fields(self, model: type[models.Model]) -> dict[str, models.Field]:
        """Return concrete model fields keyed by name."""
        ignored_fields = {"id", "datafile", "line_number", "RecordType"}
        return {
            field.name: field
            for field in model._meta.fields
            if field.name not in ignored_fields
        }

    def _validated_csv_fields(
        self,
        csv_path: Path,
        reader: csv.DictReader,
        model_fields: dict[str, models.Field],
    ) -> list[str]:
        """Return CSV fields that can be loaded into the parsed model."""
        if not reader.fieldnames:
            raise CommandError(f"{csv_path} is missing a header row.")

        required_fields = {"FIPS_CODE", "RPT_MONTH_YEAR"}
        missing_fields = required_fields - set(reader.fieldnames)
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise CommandError(f"{csv_path} is missing required field(s): {missing}.")

        return [field for field in reader.fieldnames if field in model_fields]

    def _record_values(
        self,
        row: dict[str, Any],
        csv_fields: list[str],
        model_fields: dict[str, models.Field],
    ) -> dict[str, Any]:
        """Convert one CSV row into parsed-model values."""
        return {
            field_name: self._convert_value(model_fields[field_name], row[field_name])
            for field_name in csv_fields
        }

    def _convert_value(self, field: models.Field, value: Any) -> Any:
        """Convert CSV values into the destination model field type."""
        if value is None:
            return None

        value = str(value).strip()
        if not value:
            return None

        if isinstance(field, models.IntegerField):
            return int(float(value))

        return value

    def _datafile_id_for_row(
        self,
        spec: CsvSpec,
        row: dict[str, Any],
        importer: User,
    ) -> int:
        """Return the synthetic DataFile id for a CSV row."""
        reporting_month = self._reporting_month(row["RPT_MONTH_YEAR"])
        fiscal_year = self._fiscal_year_for_reporting_month(reporting_month)
        if fiscal_year != self.fiscal_year:
            raise CommandError(
                f"{spec.record_type} row for reporting month {reporting_month} "
                f"belongs to FY{fiscal_year}, not FY{self.fiscal_year}."
            )

        stt_code = self._normalize_stt_code(row["FIPS_CODE"])
        quarter = self._quarter_for_reporting_month(reporting_month)
        key = (spec.section, stt_code, quarter)
        if key in self.datafile_ids:
            return self.datafile_ids[key]

        stt = self.stts_by_code.get(stt_code)
        if not stt:
            raise CommandError(
                f"No STT with stt_code={stt_code} exists for {spec.record_type}."
            )

        datafile, created = DataFile.objects.get_or_create(
            program_type=DataFile.ProgramType.TANF,
            section=spec.section,
            version=self.version,
            quarter=quarter,
            year=self.fiscal_year,
            stt=stt,
            is_program_audit=False,
            defaults={
                "original_filename": self._synthetic_filename(spec, stt_code, quarter),
                "slug": self._synthetic_slug(spec, stt_code, quarter),
                "extension": "csv",
                "state": SubmissionState.PARSE_COMPLETED,
                "user": importer,
                "file": None,
                "s3_versioning_id": None,
            },
        )
        if not datafile.original_filename.startswith(IMPORT_PREFIX):
            raise CommandError(
                "A non-synthetic DataFile already exists for "
                f"{spec.record_type} FY{self.fiscal_year} {stt_code} {quarter} "
                f"version {self.version}. Choose a different --datafile-version."
            )
        if not created and datafile.state != SubmissionState.PARSE_COMPLETED:
            datafile.state = SubmissionState.PARSE_COMPLETED
            datafile.save(update_fields=["state"])

        self.datafile_ids[key] = datafile.id
        return datafile.id

    def _synthetic_filename(self, spec: CsvSpec, stt_code: str, quarter: str) -> str:
        """Return a synthetic filename marker for replacement safety."""
        return (
            f"{IMPORT_PREFIX}:{spec.record_type}:FY{self.fiscal_year}:"
            f"{stt_code}:{quarter}.csv"
        )

    def _synthetic_slug(self, spec: CsvSpec, stt_code: str, quarter: str) -> str:
        """Return a stable synthetic DataFile slug."""
        slug = (
            f"{IMPORT_PREFIX}-{spec.record_type}-fy{self.fiscal_year}-"
            f"{stt_code}-{quarter}"
        )
        return slugify(slug)

    def _reporting_month(self, value: Any) -> int:
        """Return a validated YYYYMM reporting month."""
        reporting_month = int(float(str(value).strip()))
        if len(str(reporting_month)) != 6:
            raise CommandError(f"Invalid RPT_MONTH_YEAR value: {value}")
        return reporting_month

    def _fiscal_year_for_reporting_month(self, reporting_month: int) -> int:
        """Return the federal fiscal year for a YYYYMM reporting month."""
        calendar_year = reporting_month // 100
        month = reporting_month % 100
        if month < 1 or month > 12:
            raise CommandError(f"Invalid RPT_MONTH_YEAR value: {reporting_month}")
        return calendar_year + 1 if month >= 10 else calendar_year

    def _quarter_for_reporting_month(self, reporting_month: int) -> str:
        """Return the federal fiscal quarter for a YYYYMM reporting month."""
        month = reporting_month % 100
        if month in (10, 11, 12):
            return DataFile.Quarter.Q1
        if month in (1, 2, 3):
            return DataFile.Quarter.Q2
        if month in (4, 5, 6):
            return DataFile.Quarter.Q3
        if month in (7, 8, 9):
            return DataFile.Quarter.Q4
        raise CommandError(f"Invalid RPT_MONTH_YEAR value: {reporting_month}")

    def _normalize_stt_code(self, value: Any) -> str:
        """Normalize STT codes for CSV-to-STT lookup."""
        return str(int(float(str(value).strip()))).zfill(2)

    def _write_progress(self, spec: CsvSpec, loaded_count: int):
        """Write periodic import progress."""
        self.stdout.write(f"Loaded {loaded_count} {spec.record_type} rows...")
