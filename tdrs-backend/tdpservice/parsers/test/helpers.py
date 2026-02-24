"""Shared helpers for parser tests."""

from tdpservice.parsers.factory import ParserFactory


def parse_datafile(dfs, datafile, **factory_kwargs):
    """Parse a datafile using the parser factory with consistent defaults."""
    dfs.datafile = datafile
    parser = ParserFactory.get_instance(
        datafile=datafile,
        dfs=dfs,
        section=factory_kwargs.pop("section", datafile.section),
        program_type=factory_kwargs.pop("program_type", datafile.program_type),
        **factory_kwargs,
    )
    parser.parse_and_validate()
    return parser
