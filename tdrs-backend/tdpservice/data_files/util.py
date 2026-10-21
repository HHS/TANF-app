"""Utility file for DataFiles."""


def create_s3_log_file_path(datafile):
    """Create a unique S3 log file path per parse using the DataFile ID."""
    return f"{datafile.year}/{datafile.quarter}/{datafile.stt}/{datafile.program.code}/{datafile.section.name}/{datafile.id}"


def create_legacy_s3_log_file_path(datafile):
    """Create the old-format S3 log path for backwards compatibility with pre-existing logs."""
    from tdpservice.data_files.models import Program

    key = f"{datafile.year}/{datafile.quarter}/{datafile.stt}/"
    if datafile.program.code in [Program.Code.FRA, Program.Code.TANF]:
        key += datafile.section.name
    elif datafile.program.code == Program.Code.TRIBAL:
        key += f"{datafile.program.code.title()} {datafile.section.name}"
    else:
        key += f"{datafile.program.code} {datafile.section.name}"
    return key
