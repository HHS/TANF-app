"""Fixtures for parsing integration tests."""
import pytest
from .factories import ParsingFileFactory

@pytest.fixture
def t3_cat2_invalid_citizenship_file():
    """Fixture for T3 file with an invalid CITIZENSHIP_STATUS."""
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q1',
        file__name='t3_invalid_citizenship_file.txt',
        file__section='Active Case Data',
        file__data=(b'HEADER20204A06   TAN1ED\n'
                    b'T320201011111111112420190127WTTTT90W022212222204398000000000\n'
                    b'T320201011111111112420190127WTTTT90W0222122222043981000000004201001013333333330000000'
                    b'1100000099998888\n'
                    b'TRAILER0000002         ')
    )
    return parsing_file

@pytest.fixture
def m2_cat2_invalid_37_38_39_file():
    """Fixture for M2 file with an invalid EDUCATION_LEVEL, CITIZENSHIP_STATUS, COOPERATION_CHILD_SUPPORT."""
    parsing_file = ParsingFileFactory(
        year=2024,
        quarter='Q1',
        file__name='m2_cat2_invalid_37_38_39_file.txt',
        section='SSP Active Case Data',
        file__data=(b'HEADER20234A24   SSP1ED\n'
                    b'M2202310111111111275219811103WTTT#PW@W22212222222250122000010119350000000000000000000000000000000'
                    b'00000000000000000000000000000225300000000000000000000\n'
                    b'TRAILER0000001         ')
    )
    return parsing_file

@pytest.fixture
def m3_cat2_invalid_68_69_file():
    """Fixture for M3 file with an invalid EDUCATION_LEVEL and CITIZENSHIP_STATUS."""
    parsing_file = ParsingFileFactory(
        year=2024,
        quarter='Q1',
        file__name='m3_cat2_invalid_68_69_file.txt',
        section='SSP Active Case Data',
        file__data=(b'HEADER20234A24   SSP1ED\n'
                    b'M320231011111111127420110615WTTTP99B#22212222204300000000000\n'
                    b'M320231011111111127120110615WTTTP99B#222122222043011000000004201001013333333330000000110000009999'
                    b'8888\n'
                    b'TRAILER0000002         ')
    )
    return parsing_file

@pytest.fixture
def m5_cat2_invalid_23_24_file():
    """Fixture for M5 file with an invalid EDUCATION_LEVEL and CITIZENSHIP_STATUS."""
    parsing_file = ParsingFileFactory(
        year=2024,
        quarter='Q1',
        file__name='m5_cat2_invalid_23_24_file.txt',
        section='SSP Closed Case Data',
        file__data=(b'HEADER20184C24   SSP1ED\n'
                    b'M520181011111111161519791106WTTTY0ZB922212222222210112000112970000\n'
                    b'TRAILER0000001         ')
    )
    return parsing_file
