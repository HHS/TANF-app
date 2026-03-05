"""Utility file for DataFiles."""


def create_s3_log_file_path(datafile):
    """Create a unique S3 log file path per parse using the DataFile ID."""
    return f"{datafile.year}/{datafile.quarter}/{datafile.stt}/{datafile.program_type}/{datafile.section}/{datafile.id}"
