"""Tests for the header parser module."""

from tdpservice.parsers import schema_defs
from tdpservice.parsers import util
import pytest

import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def test_datafile(stt_user, stt):
    """Fixture for small_correct_file."""
    return util.create_test_datafile("small_correct_file.txt", stt_user, stt)


@pytest.mark.django_db
def test_header_cleanup(test_datafile):
    """Test the header parser."""
    YEAR = "2020"
    QUARTER = "4"
    TYPE = "A"
    STATE_FIPS = "  "
    TRIBE_CODE = "   "
    PROGRAM_CODE = "TAN"
    EDIT_CODE = "1"
    ENCRYPTION_CODE = " "
    UPDATE_INDICATOR = "D"
    header_line = (
        f"HEADER{YEAR}{QUARTER}{TYPE}{STATE_FIPS}{TRIBE_CODE}"
        + f"{PROGRAM_CODE}{EDIT_CODE}{ENCRYPTION_CODE}{UPDATE_INDICATOR}"
    )
    header, header_is_valid, header_errors = schema_defs.header.parse_and_validate(
        header_line, util.make_generate_file_precheck_parser_error(test_datafile, 1)
    )

    assert header_is_valid
    assert header_errors == []

@pytest.mark.parametrize("header_line, is_valid, error", [
    # Title error
    ("      20204A06   TAN1ED", False, "Your file does not begin with a HEADER record."),
    # quarter error
    ("HEADER20205A06   TAN1ED", False, "HEADER Item 5 (quarter): 5 is not in [1, 2, 3, 4]."),
    # Type error
    ("HEADER20204E06   TAN1ED", False, "HEADER Item 6 (type): E is not in [A, C, G, S]."),
    # Fips error
    ("HEADER20204A07   TAN1ED", False, ("HEADER Item 1 (state fips): 07 is not in [00, 01, 02, 04, 05, 06, 08, 09, "
                                        "10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, "
                                        "30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45, 46, 47, 48, 49, "
                                        "50, 51, 53, 54, 55, 56, 66, 72, 78].")),
    # Tribe error
    ("HEADER20204A00 -1TAN1ED", False, "HEADER Item 3 (tribe code):  -1 is not in range [0, 999]."),
    # Program type error
    ("HEADER20204A06   BAD1ED", False, "HEADER Item 7 (program type): BAD is not in [TAN, SSP]."),
    # Edit error
    ("HEADER20204A06   TAN3ED", False, "HEADER Item 8 (edit): 3 is not in [1, 2]."),
    # Encryption error
    ("HEADER20204A06   TAN1AD", False, "HEADER Item 9 (encryption): A is not in [ , E]."),
    # Update error
    ("HEADER20204A06   TAN1EA", False, ("HEADER Update Indicator must be set to D instead of A. Please review "
                                        "Exporting Complete Data Using FTANF in the Knowledge Center.")),
])
@pytest.mark.django_db
def test_header_fields(test_datafile, header_line, is_valid, error):
    """Test validate all header fields."""
    generate_error = util.make_generate_parser_error(test_datafile, 1)
    header, header_is_valid, header_errors = schema_defs.header.parse_and_validate(header_line,
                                                                                   generate_error)

    assert is_valid == header_is_valid
    assert error == header_errors[0].error_message
