"""Utility file for DataFiles."""


def create_s3_log_file_path(datafile):
    """Create backwards compatible parsing log file path."""
    # Import inside function to avoid circular import during logging config.
    # log_handler.py is loaded before Django apps are ready, so top-level
    # model imports cause AppRegistryNotReady errors.
    from tdpservice.data_files.models import DataFile

    key = f"{datafile.year}/{datafile.quarter}/{datafile.stt}/"
    if datafile.program_type in [DataFile.ProgramType.FRA, DataFile.ProgramType.TANF]:
        key += f"{datafile.section}"
    elif datafile.program_type == DataFile.ProgramType.TRIBAL:
        key += f"{datafile.program_type.title()} {datafile.section}"
    else:
        key += f"{datafile.program_type} {datafile.section}"
    return key
