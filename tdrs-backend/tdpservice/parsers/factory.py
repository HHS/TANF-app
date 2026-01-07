"""Factory class for all parser classes."""

from tdpservice.data_files.models import DataFile
from tdpservice.parsers.parser_classes.fra_parser import FRAParser
from tdpservice.parsers.parser_classes.program_audit_parser import ProgramAuditParser
from tdpservice.parsers.parser_classes.tdr_parser import TanfDataReportParser


class ParserFactory:
    """Factory class to get/instantiate parsers."""

    @classmethod
    def get_class(cls, program_type, is_program_audit=False):
        """Return the correct parser class to be constructed manually."""
        match program_type:
            case (
                DataFile.ProgramType.TANF
                | DataFile.ProgramType.SSP
                | DataFile.ProgramType.TRIBAL
            ):
                if is_program_audit:
                    return ProgramAuditParser
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
        is_program_audit = kwargs.pop("is_program_audit", False)
        return cls.get_class(program_type, is_program_audit=is_program_audit)(**kwargs)
