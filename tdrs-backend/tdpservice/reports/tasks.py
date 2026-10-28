"""Shared celery task processing report source files."""

import io
import logging
import re
import zipfile
from pathlib import PurePosixPath

from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from celery import shared_task

from tdpservice.email.helpers.feedback_report import (
    send_feedback_report_available_email,
)
from tdpservice.reports.models import ReportFile, ReportSource, ReportType
from tdpservice.stts.models import STT
from tdpservice.users.models import AccountApprovalStatusChoices, User

logger = logging.getLogger(__name__)

STT_FOLDER_INDEX = 3
STT_RELATIVE_PATH_START_INDEX = STT_FOLDER_INDEX + 1


def _is_report_file_path(parts: list[str]) -> bool:
    """Return whether a zip path follows root/FY####/RO#/F#/path/to/file."""
    if any(part == "__MACOSX" or part.startswith("._") for part in parts):
        return False

    if any(part in ("", ".", "..") for part in parts):
        return False

    if len(parts) < 5:
        return False

    _, fiscal_year_folder, region_folder, stt_folder, *file_path_parts = parts

    if not re.fullmatch(r"FY\d{4}", fiscal_year_folder):
        return False

    if not re.fullmatch(r"RO\d+", region_folder):
        return False

    if not re.fullmatch(r"F\d+", stt_folder):
        return False

    if any(part.startswith(".") for part in file_path_parts):
        return False

    return True


def find_stt_folders(zip_file: zipfile.ZipFile) -> dict:
    """
    Traverse the nested folder structure to find STT folders and their files.

    Expected structure: {ZipName}/FY{YYYY}/RO{X}/F{X}/files
    - {ZipName}: Root folder matching the zip filename (e.g., FY2025_07312025)
    - FY{YYYY}: Fiscal year folder with "FY" prefix (e.g., FY2025)
    - RO{X}: Regional Office folder with "RO" prefix (e.g., RO1, RO4)
    - F{X}: STT folder with "F" prefix (e.g., F1, F12)

    Returns: {stt_code: [file_info_objects]}
    """
    stt_files = {}

    for info in zip_file.infolist():
        # Skip directories
        if info.is_dir():
            continue

        # Parse the path: {ZipName}/FY{YYYY}/RO{X}/F{X}/filename
        parts = info.filename.split("/")

        # Must have at least 5 parts: {ZipName}/FY{YYYY}/RO{X}/F{X}/filename
        if len(parts) < 5:
            continue

        if not _is_report_file_path(parts):
            continue

        # Extract STT code from 4th level folder (index 3) (e.g., "F1" -> "1")
        stt_folder = parts[3]
        if stt_folder.startswith("F"):
            stt_code = stt_folder[1:]  # Strip the "F" prefix
        else:
            stt_code = stt_folder

        # Add file to this STT's list
        if stt_code not in stt_files:
            stt_files[stt_code] = []

        stt_files[stt_code].append(info)

    if not stt_files:
        raise ValueError(
            "No STT folders found. Expected structure: {ZipName}/FY{YYYY}/RO{X}/F{X}/files "
            "(e.g., FY2025_07312025/FY2025/RO1/F1/report.pdf). Please verify the zip file structure."
        )

    return stt_files


def bundle_stt_files(
    zip_file: zipfile.ZipFile, file_infos: list, stt_code: str
) -> ContentFile:
    """
    Bundle all files for an STT into a single zip file.

    Parameters
    ----------
        zip_file: The report source zip file
        file_infos: List of ZipInfo objects for files belonging to this STT
        stt_code: The STT code (for naming)

    Returns
    -------
        ContentFile containing the bundled zip
    """
    # Create in-memory zip
    zip_buffer = io.BytesIO()
    bundled_filenames = set()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as bundle_zip:
        for file_info in file_infos:
            # Read file from report source zip
            file_data = zip_file.read(file_info.filename)

            # Keep the folder hierarchy under the STT folder.
            path_parts = PurePosixPath(file_info.filename).parts
            relative_path_parts = path_parts[STT_RELATIVE_PATH_START_INDEX:]
            if not relative_path_parts or any(
                part in ("", ".", "..") for part in relative_path_parts
            ):
                raise ValueError(
                    f"Invalid file path in STT folder: {file_info.filename}"
                )
            filename = PurePosixPath(*relative_path_parts).as_posix()
            if filename in bundled_filenames:
                raise ValueError(
                    f"Duplicate file path in STT folder '{stt_code}': {filename}"
                )
            bundled_filenames.add(filename)

            bundle_zip.writestr(filename, file_data)

    # Rewind buffer
    zip_buffer.seek(0)

    # Create ContentFile
    bundle_filename = f"stt_{stt_code}_reports.zip"
    return ContentFile(zip_buffer.read(), name=bundle_filename)


def _mark_source_failed(source: ReportSource, error_message: str):
    """Mark a ReportSource as failed with the given error message."""
    source.status = ReportSource.Status.FAILED
    source.error_message = error_message
    source.processed_at = timezone.now()
    source.save(update_fields=["status", "error_message", "processed_at"])


def _stt_code_candidates(stt_code: str) -> tuple[str, ...]:
    """Return possible database STT codes for a source ZIP folder code."""
    candidates = []
    for pad_length in (2, 3):
        padded_code = stt_code.zfill(pad_length)
        if padded_code not in candidates:
            candidates.append(padded_code)

    return tuple(candidates)


def _is_tribal_stt(stt: STT) -> bool:
    """Return whether an STT is a tribe."""
    return (stt.type or "").lower() == STT.EntityType.TRIBE


def _valid_report_types_for_stt(stt: STT) -> tuple[str, ...]:
    """Return report types that are valid for an STT."""
    if _is_tribal_stt(stt):
        return (ReportType.TRIBAL_TANF,)

    # Should we just assume that all non-tribal stts can receive fra feedback reports?
    return (ReportType.TANF_SSP, ReportType.FRA)


def _expected_report_type_label(stt: STT) -> str:
    """Return the report type label expected for an STT."""
    labels = [
        ReportType(report_type).label
        for report_type in _valid_report_types_for_stt(stt)
    ]
    return " or ".join(labels)


def _resolve_stts(stt_files_map: dict[str, list]) -> dict[str, STT]:
    """Resolve source folder STT codes to STT records."""
    candidate_codes = {
        candidate_code
        for stt_code in stt_files_map
        for candidate_code in _stt_code_candidates(stt_code)
    }
    stts_by_db_code = {
        stt.stt_code: stt for stt in STT.objects.filter(stt_code__in=candidate_codes)
    }
    stts_by_code = {}

    for stt_code in stt_files_map:
        for candidate_code in _stt_code_candidates(stt_code):
            stt = stts_by_db_code.get(candidate_code)
            if stt is not None:
                stts_by_code[stt_code] = stt
                break
        else:
            raise ValueError(f"STT code '{stt_code}' not found in system.")

    return stts_by_code


def _validate_report_type_matches_stts(
    source: ReportSource, stts_by_code: dict[str, STT]
):
    """Validate all STTs in the upload match the selected report type."""
    mismatches = []

    for stt_code, stt in stts_by_code.items():
        if source.report_type in _valid_report_types_for_stt(stt):
            continue

        mismatches.append(
            f"{stt.name} ({stt.stt_code}; folder F{stt_code}) "
            f"is {_expected_report_type_label(stt)}"
        )

    if not mismatches:
        return

    mismatch_limit = 10
    mismatch_summary = "; ".join(mismatches[:mismatch_limit])
    remaining_count = len(mismatches) - mismatch_limit
    remaining_summary = f"; and {remaining_count} more" if remaining_count > 0 else ""
    raise ValueError(
        f"Selected report type {ReportType(source.report_type).label} does not "
        f"match STT folders in source upload. Mismatched STTs: "
        f"{mismatch_summary}{remaining_summary}."
    )


def _download_and_validate_zip(source: ReportSource):
    """
    Download zip file from S3 and validate it.

    Returns
    -------
        zipfile.ZipFile or None if validation fails
    """
    # Download zip from S3
    try:
        if source.file:
            source.file.open("rb")
            source_bytes = source.file.read()
            source.file.close()
    except Exception as e:
        _mark_source_failed(source, f"Could not download report source zip: {e}")
        return None

    # Validate zip file
    try:
        return zipfile.ZipFile(io.BytesIO(source_bytes))
    except zipfile.BadZipfile:
        _mark_source_failed(source, "File is not a valid zip.")
        return None


def _extract_and_validate_structure(source: ReportSource, zip_file: zipfile.ZipFile):
    """
    Extract STT folders from zip file.

    Uses source.year for the fiscal year (provided by admin during upload).

    Returns
    -------
        tuple of (fiscal_year, stt_files_map) or (None, None) if validation fails
    """
    # Find all STT folders and their files
    try:
        stt_files_map = find_stt_folders(zip_file)
    except ValueError as e:
        _mark_source_failed(source, str(e))
        return None, None

    return source.year, stt_files_map


def _send_report_file_notification(report_file: ReportFile):
    """
    Send email notification to Data Analysts and Regional Staff for the ReportFile's STT.

    Data Analysts are notified if their assigned STT matches the report's STT.
    Regional Staff are notified if their region includes the report's STT.

    Parameters
    ----------
        report_file: The ReportFile that was just created
    """
    # Data Analysts assigned to this STT
    data_analyst_q = Q(stt=report_file.stt, groups__name="Data Analyst")
    # Regional Staff whose region includes this STT
    regional_staff_q = Q(
        regions=report_file.stt.region, groups__name="OFA Regional Staff"
    )

    recipients = list(
        User.objects.filter(
            data_analyst_q | regional_staff_q,
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        .values_list("email", flat=True)
        .distinct()
    )

    if recipients:
        send_feedback_report_available_email(report_file, recipients)


def _build_report_file_payload(
    source: ReportSource,
    zip_file: zipfile.ZipFile,
    stt_code: str,
    file_infos: list,
    fiscal_year: int,
    stt: STT,
) -> dict:
    """Build ReportFile creation data for a single STT folder."""
    if not file_infos:
        raise ValueError(f"STT folder '{stt_code}' is empty.")

    # Bundle all files for this STT into a single zip
    try:
        bundled_zip = bundle_stt_files(zip_file, file_infos, stt_code)
    except Exception as e:
        raise ValueError(f"Failed to bundle files for STT '{stt_code}': {e}") from e

    return {
        "year": fiscal_year,
        "date_extracted_on": source.date_extracted_on,
        "stt": stt,
        "user": source.uploaded_by,
        "source": source,
        "report_type": source.report_type,
        "original_filename": bundled_zip.name,
        "slug": bundled_zip.name,
        "extension": "zip",
        "file": bundled_zip,
    }


def _build_report_file_payloads(
    source: ReportSource,
    zip_file: zipfile.ZipFile,
    stt_files_map: dict[str, list],
    fiscal_year: int,
) -> list[dict]:
    """Validate the full source upload and build ReportFile creation data."""
    stts_by_code = _resolve_stts(stt_files_map)
    _validate_report_type_matches_stts(source, stts_by_code)

    return [
        _build_report_file_payload(
            source,
            zip_file,
            stt_code,
            file_infos,
            fiscal_year,
            stts_by_code[stt_code],
        )
        for stt_code, file_infos in stt_files_map.items()
    ]


def _create_report_files(payloads: list[dict]) -> list[ReportFile]:
    """Create ReportFiles in a single database transaction."""
    with transaction.atomic():
        return [ReportFile.create_new_version(payload) for payload in payloads]


@shared_task
def process_report_source(source_id: int):
    """Process a ReportSource record zip file into individual ReportFile records."""
    logger.debug("Begin processing report source file")
    source: ReportSource = ReportSource.objects.get(id=source_id)

    # Mark as PROCESSING
    source.status = ReportSource.Status.PROCESSING
    source.error_message = ""
    source.save(update_fields=["status", "error_message"])

    # Download and validate zip file
    zip_file = _download_and_validate_zip(source)
    if zip_file is None:
        return

    # Extract fiscal year and STT folders
    fiscal_year, stt_files_map = _extract_and_validate_structure(source, zip_file)
    if fiscal_year is None:
        return

    # Validate every STT before creating rows or sending notifications.
    try:
        payloads = _build_report_file_payloads(
            source, zip_file, stt_files_map, fiscal_year
        )
    except ValueError as e:
        _mark_source_failed(source, str(e))
        return

    try:
        report_files = _create_report_files(payloads)
    except Exception as e:
        _mark_source_failed(source, f"Failed to create report files: {e}")
        return

    for report_file in report_files:
        _send_report_file_notification(report_file)

    # Mark source as succeeded
    source.status = ReportSource.Status.SUCCEEDED
    source.num_reports_created = len(report_files)
    source.processed_at = timezone.now()
    source.save(update_fields=["status", "num_reports_created", "processed_at"])
