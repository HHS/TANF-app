"""Shared celery task processing report source files."""

import io
import logging
import zipfile

from django.core.files.base import ContentFile
from django.utils import timezone

from celery import shared_task
from tdpservice.email.helpers.feedback_report import send_feedback_report_available_email
from tdpservice.reports.models import ReportFile, ReportSource
from tdpservice.stts.models import STT
from tdpservice.users.models import User, AccountApprovalStatusChoices


logger = logging.getLogger(__name__)


def find_stt_folders(zip_file: zipfile.ZipFile) -> dict:
    """
    Traverse the nested folder structure to find STT folders and their files.

    Expected structure: FY{YYYY}/R{XX}/F{X}/files
    - FY{YYYY}: Fiscal year folder with "FY" prefix (e.g., FY2025)
    - R{XX}: Region folder with "R" prefix (e.g., R01, R1)
    - F{X}: STT folder with "F" prefix (e.g., F1, F12)

    Returns: {stt_code: [file_info_objects]}
    """
    stt_files = {}

    for info in zip_file.infolist():
        # Skip directories
        if info.is_dir():
            continue

        # Parse the path: FY{YYYY}/R{XX}/F{X}/filename
        parts = info.filename.split('/')

        # Must have at least 4 parts: FY{YYYY}/R{XX}/F{X}/filename
        if len(parts) < 4:
            continue

        # Extract STT code from 3rd level folder (e.g., "F1" -> "1")
        stt_folder = parts[2]
        if stt_folder.startswith('F'):
            stt_code = stt_folder[1:]  # Strip the "F" prefix
        else:
            stt_code = stt_folder

        # Add file to this STT's list
        if stt_code not in stt_files:
            stt_files[stt_code] = []

        stt_files[stt_code].append(info)

    if not stt_files:
        raise ValueError(
            "No STT folders found. Expected structure: FY{YYYY}/R{XX}/F{X}/files "
            "(e.g., FY2025/R01/F1/report.pdf). Please verify the zip file structure."
        )

    return stt_files


def bundle_stt_files(zip_file: zipfile.ZipFile, file_infos: list, stt_code: str) -> ContentFile:
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

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as bundle_zip:
        for file_info in file_infos:
            # Read file from report source zip
            file_data = zip_file.read(file_info.filename)

            # Get just the filename (not the full path)
            filename = file_info.filename.split('/')[-1]

            # Add to bundle with just the filename (flatten structure)
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
    Send email notification to all Data Analysts for the ReportFile's STT.

    Parameters
    ----------
        report_file: The ReportFile that was just created
    """
    # Query all approved Data Analysts for this STT
    data_analysts = User.objects.filter(
        stt=report_file.stt,
        account_approval_status=AccountApprovalStatusChoices.APPROVED,
        groups__name="Data Analyst",
    ).values_list("email", flat=True).distinct()

    if data_analysts:
        send_feedback_report_available_email(report_file, list(data_analysts))


def _process_stt_folder(
    source: ReportSource,
    zip_file: zipfile.ZipFile,
    stt_code: str,
    file_infos: list,
    fiscal_year: int,
):
    """
    Process a single STT folder: validate, bundle files, and create ReportFile.

    Returns
    -------
        bool: True if successful, False if failed
    """
    # Validate STT exists
    try:
        stt = STT.objects.get(stt_code=stt_code)
    except STT.DoesNotExist:
        _mark_source_failed(source, f"STT code '{stt_code}' not found in system.")
        return False

    # Check if STT folder is empty
    if not file_infos:
        _mark_source_failed(source, f"STT folder '{stt_code}' is empty.")
        return False

    # Bundle all files for this STT into a single zip
    try:
        bundled_zip = bundle_stt_files(zip_file, file_infos, stt_code)
    except Exception as e:
        _mark_source_failed(source, f"Failed to bundle files for STT '{stt_code}': {e}")
        return False

    # Create ReportFile record
    report_file = ReportFile.create_new_version(
        {
            "year": fiscal_year,
            "date_extracted_on": source.date_extracted_on,
            "stt": stt,
            "user": source.uploaded_by,
            "source": source,
            "original_filename": bundled_zip.name,
            "slug": bundled_zip.name,
            "extension": "zip",
            "file": bundled_zip,
        }
    )

    # Send email notification to Data Analysts for this STT
    _send_report_file_notification(report_file)

    return True


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

    # Process each STT folder
    num_created = 0
    for stt_code, file_infos in stt_files_map.items():
        success = _process_stt_folder(
            source, zip_file, stt_code, file_infos, fiscal_year
        )
        if not success:
            return

        num_created += 1

    # Mark source as succeeded
    source.status = ReportSource.Status.SUCCEEDED
    source.num_reports_created = num_created
    source.processed_at = timezone.now()
    source.save(update_fields=["status", "num_reports_created", "processed_at"])
