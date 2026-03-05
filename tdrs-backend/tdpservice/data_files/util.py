"""Utility file for DataFiles."""


def create_s3_log_file_path(datafile):
    """Create a unique S3 log file path per parse using the DataFile ID."""
    return f"{datafile.year}/{datafile.quarter}/{datafile.stt}/{datafile.program_type}/{datafile.section}/{datafile.id}"


def create_legacy_s3_log_file_path(datafile):
    """Create the old-format S3 log path for backwards compatibility with pre-existing logs."""
    from tdpservice.data_files.models import DataFile

    key = f"{datafile.year}/{datafile.quarter}/{datafile.stt}/"
    if datafile.program_type in [DataFile.ProgramType.FRA, DataFile.ProgramType.TANF]:
        key += f"{datafile.section}"
    elif datafile.program_type == DataFile.ProgramType.TRIBAL:
        key += f"{datafile.program_type.title()} {datafile.section}"
    else:
        key += f"{datafile.program_type} {datafile.section}"
    return key
