"""Tests for the transforms module."""

from tdpservice.parsers.transforms import (
    tanf_ssn_decryption_func,
    ssp_ssn_decryption_func,
)


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
