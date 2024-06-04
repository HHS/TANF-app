"""Test for Transforms."""

import pytest
import tdpservice.parsers.transforms as transforms
from tdpservice.parsers.transforms import (
    tanf_ssn_decryption_func,
    ssp_ssn_decryption_func,
)


@pytest.mark.parametrize("value,digits,expected", [
    ("1", 3, "001"),
    ("10", 3, "010"),
    ("100", 3, "100"),
    ("1000", 3, "1000"),
    ("1 ", 3, "01 "),
    ("1  ", 3, "1  "),
    ("1", 0, "1"),
    ("1", -1, "1")
])
def test_zero_pad(value, digits, expected):
    """Test zero_pad returns valid value."""
    transform = transforms.zero_pad(digits)
    result = transform(value)

    assert result == expected


def test_tanf_ssn_decryption_func():
    """Test the TANF SSN decryption function."""
    assert tanf_ssn_decryption_func(None) is None
    assert tanf_ssn_decryption_func("TANFSSN", is_encrypted=True) == "0ANFSSN"
    assert tanf_ssn_decryption_func("TANFSSN", is_encrypted=False) == "TANFSSN"
    assert tanf_ssn_decryption_func("@90#Y0B", is_encrypted=True) == "1256758"


def test_ssp_ssn_decryption_func():
    """Test the SSP SSN decryption function."""
    assert ssp_ssn_decryption_func(None) is None
    assert ssp_ssn_decryption_func("SSPSSN", is_encrypted=False) == "SSPSSN"
    assert ssp_ssn_decryption_func("SSPSSN", is_encrypted=True) == "SS4SSN"
    assert ssp_ssn_decryption_func("@90#Y0B", is_encrypted=True) == "1256758"
