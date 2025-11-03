"""Shared celery task processing report ingestion files."""

import io
import logging
import re
import zipfile
from django.core.files.base import ContentFile
from django.utils import timezone

from celery import shared_task
from tdpservice.reports.models import ReportFile, ReportIngest
from tdpservice.stts.models import STT

# Matches: report_Arizona_Q1_2025.zip
FILENAME_RE = re.compile(r"^report_(.+)_(Q[1-4])_(\d{4})\.zip$", re.IGNORECASE)

logger = logging.getLogger(__name__)

@shared_task
def process_report_ingest(ingest_id: int):  # noqa: C901
    """Process a ReportIngest record zip file into individual ReportFile records."""
    logger.debug("Begin processing report ingest file")
    ingest: ReportIngest = ReportIngest.objects.get(id=ingest_id)

    # Mark as PROCESSING
    ingest.status = ReportIngest.Status.PROCESSING
    ingest.error_message = ""
    ingest.save(update_fields=["status", "error_message"])

    # Validate zip contents
    try:
        if ingest.file:
            ingest.file.open("rb")
            master_bytes = ingest.file.read()
            ingest.file.close()
    except Exception as e:
        ingest.status = ReportIngest.Status.FAILED
        ingest.error_message = f"Could  not download master zip: {e}"
        ingest.processed_at = timezone.now()
        ingest.save(update_fields=["status", "error_message", "processed_at"])
        return

    try:
        zip_file = zipfile.ZipFile(io.BytesIO(master_bytes))
    except zipfile.BadZipfile:
        ingest.status = ReportIngest.Status.FAILED
        ingest.error_message = "File is not a valid zip."
        ingest.processed_at = timezone.now()
        ingest.save(update_fields=["status", "error_message", "processed_at"])
        return

    # Validate child zip files
    parsed_children = []
    for info in zip_file.infolist():
        if info.is_dir():
            continue

        # validate child is .zip file
        filename = info.filename.split("/")[-1]
        match = FILENAME_RE.match(filename)
        if not match:
            ingest.status = ReportIngest.Status.FAILED
            ingest.error_message = (
                f"Invalid child filename format: {filename}. "
                "Expected: report_<STT>_<Q1|Q2|Q3|Q4>_<YYYY>.zip"
            )
            ingest.processed_at = timezone.now()
            ingest.save(update_fields=["status", "error_message", "processed_at"])
            return

        stt_name = match.group(1)
        quarter = match.group(2).upper()
        year = int(match.group(3))

        # validate STT exists
        try:
            stt = STT.objects.get(name=stt_name)
        except STT.DoesNotExist:
            ingest.status = ReportIngest.Status.FAILED
            ingest.error_message = (
                f"STT '{stt_name}' from file '{filename}' not found in system."
            )
            ingest.processed_at = timezone.now()
            ingest.save(update_fields=["status", "error_message", "processed_at"])
            return

        parsed_children.append(
            {
                "info": info,
                "filename": filename,
                "stt": stt,
                "quarter": quarter,
                "year": year,
            }
        )

    # Create a ReportFile record for each parsed_children entry
    num_created = 0
    for child in parsed_children:
        info = child["info"]
        filename = child["filename"]
        stt = child["stt"]
        quarter = child["quarter"]
        year = child["year"]

        child_bytes = zip_file.read(info)
        content = ContentFile(child_bytes, name=filename)

        ReportFile.create_new_version(
            {
                "year": year,
                "quarter": quarter,
                "stt": stt,
                "user": ingest.uploaded_by,  # uploader is the user on the ReportFile
                "ingest": ingest,
                "original_filename": filename,
                "slug": filename,
                "extension": "zip",
                "file": content,
            }
        )

        num_created += 1

    # mark ingest as succeeded
    ingest.status = ReportIngest.Status.SUCCEEDED
    ingest.num_reports_created = num_created
    ingest.processed_at = timezone.now()
    ingest.save(update_fields=["status", "num_reports_created", "processed_at"])
