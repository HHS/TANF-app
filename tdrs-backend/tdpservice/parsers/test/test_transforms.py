"""Test for Transforms."""

import pytest
from .. import transforms

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
