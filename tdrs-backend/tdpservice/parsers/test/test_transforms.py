"""Test for Transforms."""

import pytest

import tdpservice.parsers.transforms as transforms
from tdpservice.parsers.transforms import (
    ssp_ssn_decryption_func,
    tanf_ssn_decryption_func,
)


class TestParserTransforms:
    """Tests for parser transforms."""

    @pytest.mark.parametrize(
        "value,digits,expected",
        [
            ("1", 3, "001"),
            ("10", 3, "010"),
            ("100", 3, "100"),
            ("1000", 3, "1000"),
            ("1 ", 3, "01 "),
            ("1  ", 3, "1  "),
            ("1", 0, "1"),
            ("1", -1, "1"),
        ],
    )
    def test_zero_pad(self, value, digits, expected):
        """Test zero_pad returns valid value."""
        transform = transforms.zero_pad(digits)
        result = transform(value)

        assert result == expected

    @pytest.mark.parametrize(
        "decrypt_func,value,is_encrypted,expected",
        [
            (tanf_ssn_decryption_func, None, None, None),
            (tanf_ssn_decryption_func, "TANFSSN", True, "0ANFSSN"),
            (tanf_ssn_decryption_func, "TANFSSN", False, "TANFSSN"),
            (tanf_ssn_decryption_func, "@90#Y0B", True, "1256758"),
            (ssp_ssn_decryption_func, None, None, None),
            (ssp_ssn_decryption_func, "SSPSSN", False, "SSPSSN"),
            (ssp_ssn_decryption_func, "SSPSSN", True, "SS4SSN"),
            (ssp_ssn_decryption_func, "@90#Y0B", True, "1256758"),
        ],
    )
    def test_ssn_decryption_func(self, decrypt_func, value, is_encrypted, expected):
        """Test SSN decryption functions for base, positive, and negative cases."""
        if is_encrypted is None:
            result = decrypt_func(value)
        else:
            result = decrypt_func(value, is_encrypted=is_encrypted)

        assert result == expected
