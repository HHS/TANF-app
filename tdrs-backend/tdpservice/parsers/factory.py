"""Factory class for all parser classes."""

from tdpservice.parsers.fra_parser import FRAParser
from tdpservice.parsers.tdr_parser import TanfDataReportParser


class ParserFactory:
    """Factory class to get/instantiate parsers."""

    @classmethod
    def get_class(cls, program_type):
        """Return the correct parser class to be constructed manually."""
        match program_type:
            case "TANF" | "SSP":
                return TanfDataReportParser
            case "FRA":
                return FRAParser
            case _:
                raise ValueError(
                    f"No parser available for program type: {program_type}."
                )

    @classmethod
    def get_instance(cls, **kwargs):
        """Construct parser instance with the given kwargs."""
        program_type = kwargs.pop("program_type", None)
        match program_type:
            case "TAN" | "SSP":
                return TanfDataReportParser(**kwargs)
            case "FRA":
                return FRAParser(**kwargs)
            case _:
                raise ValueError(
                    f"No parser available for program type: {program_type}."
                )
