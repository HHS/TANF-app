"""Factory class for all parser classes."""

from tdpservice.data_files.models import DataFile
from tdpservice.parsers.fra_parser import FRAParser
from tdpservice.parsers.tdr_parser import TanfDataReportParser


class ParserFactory:
    """Factory class to get/instantiate parsers."""

    @classmethod
    def get_class(cls, program_type):
        """Return the correct parser class to be constructed manually."""
        match program_type:
            case (
                DataFile.ProgramType.TANF
                | DataFile.ProgramType.SSP
                | DataFile.ProgramType.TRIBAL
            ):
                return TanfDataReportParser
            case DataFile.ProgramType.FRA:
                return FRAParser
            case _:
                raise ValueError(
                    f"No parser available for program type: {program_type}."
                )

    @classmethod
    def get_instance(cls, **kwargs):
        """Construct parser instance with the given kwargs."""
        program_type = kwargs.pop("program_type", None)
        return cls.get_class(program_type)(**kwargs)
