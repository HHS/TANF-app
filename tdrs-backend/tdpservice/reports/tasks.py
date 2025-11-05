"""Shared celery task processing report ingestion files."""

import io
import logging
import zipfile
from datetime import datetime
from django.core.files.base import ContentFile
from django.utils import timezone

from celery import shared_task
from tdpservice.reports.models import ReportFile, ReportIngest
from tdpservice.stts.models import STT


logger = logging.getLogger(__name__)


def calculate_quarter_from_date(created_at: datetime) -> str:
    """
    Calculate the quarter based on the upload date.

    Q1: 01/01 - 02/14 → Q1 (for previous year Oct-Dec)
    Q2: 04/01 - 05/15 → Q2 (for current year Jan-Mar)
    Q3: 07/01 - 08/14 → Q3 (for current year Apr-Jun)
    Q4: 10/01 - 10/14 → Q4 (for current year Jul-Sep)
    """
    month = created_at.month
    day = created_at.day

    # Q1: January 1 - February 14
    if (month == 1) or (month == 2 and day <= 14):
        return "Q1"

    # Q2: April 1 - May 15
    if (month == 4) or (month == 5 and day <= 15):
        return "Q2"

    # Q3: July 1 - August 14
    if (month == 7) or (month == 8 and day <= 14):
        return "Q3"

    # Q4: October 1 - October 14
    if (month == 10 and day <= 14):
        return "Q4"

    # If we reach here, the date is outside valid submission windows
    raise ValueError(
        f"Upload date {created_at.strftime('%Y-%m-%d')} is outside valid submission windows. "
        "Valid windows: Q1 (01/01-02/14), Q2 (04/01-05/15), Q3 (07/01-08/14), Q4 (10/01-10/14)."
    )


def extract_fiscal_year(zip_file: zipfile.ZipFile) -> int:
    """
    Extract the fiscal year from the top-level folder in the zip file.

    Expected structure: {YYYY}/Region/STT/files
    """
    # Get all paths in the zip
    all_paths = [info.filename for info in zip_file.infolist()]

    # Find top-level folders (no parent directory)
    top_level_folders = set()
    for path in all_paths:
        parts = path.split('/')
        if len(parts) > 1:  # Has at least one folder
            top_level_folders.add(parts[0])

    if not top_level_folders:
        raise ValueError("No top-level folder found in zip file. Expected structure: {YYYY}/Region/STT/files")

    if len(top_level_folders) > 1:
        raise ValueError(
            f"Multiple top-level folders found: {sorted(top_level_folders)}. "
            "Expected single fiscal year folder (e.g., '2025')."
        )

    fiscal_year_folder = list(top_level_folders)[0]

    # Validate it's a 4-digit year
    if not fiscal_year_folder.isdigit() or len(fiscal_year_folder) != 4:
        raise ValueError(
            f"Fiscal year folder '{fiscal_year_folder}' is invalid. "
            "Expected 4-digit year (e.g., '2025')."
        )

    return int(fiscal_year_folder)


def find_stt_folders(zip_file: zipfile.ZipFile, fiscal_year_folder: str) -> dict:
    """
    Traverse the nested folder structure to find STT folders and their files.

    Expected structure: {YYYY}/Region/STT/files
    Returns: {stt_code: [file_info_objects]}
    """
    stt_files = {}

    for info in zip_file.infolist():
        # Skip directories
        if info.is_dir():
            continue

        # Parse the path: YYYY/Region/STT/filename
        parts = info.filename.split('/')

        # Must have at least 4 parts: YYYY/Region/STT/filename
        if len(parts) < 4:
            continue

        # Verify first part matches fiscal year
        if parts[0] != fiscal_year_folder:
            continue

        # Extract STT code (3rd level folder)
        stt_code = parts[2]

        # Add file to this STT's list
        if stt_code not in stt_files:
            stt_files[stt_code] = []

        stt_files[stt_code].append(info)

    if not stt_files:
        raise ValueError(
            f"No STT folders found in structure {fiscal_year_folder}/Region/STT/. "
            "Please verify the zip file structure."
        )

    return stt_files


def bundle_stt_files(zip_file: zipfile.ZipFile, file_infos: list, stt_code: str) -> ContentFile:
    """
    Bundle all files for an STT into a single zip file.

    Args:
        zip_file: The master zip file
        file_infos: List of ZipInfo objects for files belonging to this STT
        stt_code: The STT code (for naming)

    Returns:
        ContentFile containing the bundled zip
    """
    # Create in-memory zip
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as bundle_zip:
        for file_info in file_infos:
            # Read file from master zip
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


@shared_task
def process_report_ingest(ingest_id: int):  # noqa: C901
    """Process a ReportIngest record zip file into individual ReportFile records."""
    logger.debug("Begin processing report ingest file")
    ingest: ReportIngest = ReportIngest.objects.get(id=ingest_id)

    # Mark as PROCESSING
    ingest.status = ReportIngest.Status.PROCESSING
    ingest.error_message = ""
    ingest.save(update_fields=["status", "error_message"])

    # Download zip from S3
    try:
        if ingest.file:
            ingest.file.open("rb")
            master_bytes = ingest.file.read()
            ingest.file.close()
    except Exception as e:
        ingest.status = ReportIngest.Status.FAILED
        ingest.error_message = f"Could not download master zip: {e}"
        ingest.processed_at = timezone.now()
        ingest.save(update_fields=["status", "error_message", "processed_at"])
        return

    # Validate zip file
    try:
        zip_file = zipfile.ZipFile(io.BytesIO(master_bytes))
    except zipfile.BadZipfile:
        ingest.status = ReportIngest.Status.FAILED
        ingest.error_message = "File is not a valid zip."
        ingest.processed_at = timezone.now()
        ingest.save(update_fields=["status", "error_message", "processed_at"])
        return

    # Calculate quarter from upload date
    try:
        quarter = calculate_quarter_from_date(ingest.created_at)
    except ValueError as e:
        ingest.status = ReportIngest.Status.FAILED
        ingest.error_message = str(e)
        ingest.processed_at = timezone.now()
        ingest.save(update_fields=["status", "error_message", "processed_at"])
        return

    # Extract fiscal year from top-level folder
    try:
        fiscal_year = extract_fiscal_year(zip_file)
    except ValueError as e:
        ingest.status = ReportIngest.Status.FAILED
        ingest.error_message = str(e)
        ingest.processed_at = timezone.now()
        ingest.save(update_fields=["status", "error_message", "processed_at"])
        return

    # Find all STT folders and their files
    try:
        stt_files_map = find_stt_folders(zip_file, str(fiscal_year))
    except ValueError as e:
        ingest.status = ReportIngest.Status.FAILED
        ingest.error_message = str(e)
        ingest.processed_at = timezone.now()
        ingest.save(update_fields=["status", "error_message", "processed_at"])
        return

    # Process each STT folder
    num_created = 0
    for stt_code, file_infos in stt_files_map.items():
        # Validate STT exists
        try:
            stt = STT.objects.get(stt_code=stt_code)
        except STT.DoesNotExist:
            ingest.status = ReportIngest.Status.FAILED
            ingest.error_message = f"STT code '{stt_code}' not found in system."
            ingest.processed_at = timezone.now()
            ingest.save(update_fields=["status", "error_message", "processed_at"])
            return

        # Check if STT folder is empty
        if not file_infos:
            ingest.status = ReportIngest.Status.FAILED
            ingest.error_message = f"STT folder '{stt_code}' is empty."
            ingest.processed_at = timezone.now()
            ingest.save(update_fields=["status", "error_message", "processed_at"])
            return

        # Bundle all files for this STT into a single zip
        try:
            bundled_zip = bundle_stt_files(zip_file, file_infos, stt_code)
        except Exception as e:
            ingest.status = ReportIngest.Status.FAILED
            ingest.error_message = f"Failed to bundle files for STT '{stt_code}': {e}"
            ingest.processed_at = timezone.now()
            ingest.save(update_fields=["status", "error_message", "processed_at"])
            return

        # Create ReportFile record
        ReportFile.create_new_version(
            {
                "year": fiscal_year,
                "quarter": quarter,
                "stt": stt,
                "user": ingest.uploaded_by,
                "ingest": ingest,
                "original_filename": bundled_zip.name,
                "slug": bundled_zip.name,
                "extension": "zip",
                "file": bundled_zip,
            }
        )

        num_created += 1

    # Mark ingest as succeeded
    ingest.status = ReportIngest.Status.SUCCEEDED
    ingest.num_reports_created = num_created
    ingest.processed_at = timezone.now()
    ingest.save(update_fields=["status", "num_reports_created", "processed_at"])
