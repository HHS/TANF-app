import pytest
from utilities.ftanf import FTANFProcess


def test_interestgrion_snapshot(capsys):
    test_section = FTANFProcess('./utilities/test_data_section_three.xlsx', 16)
    test_section.build_file()
    captured = capsys.readouterr()
    assert captured.out == "Opening Sheet: Section 3 Aggregate\nHEADER00000000000000000\nT600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000\nTRAILER0000001         \n"


def test_pad_field_data():
    test_section = FTANFProcess('./utilities/test_data_section_three.xlsx', 16)
    padded_string = test_section.pad_field_data([2,4,4], ['T6', 124, ''])
    assert padded_string == 'T601240000'

def test_header(capsys):
    test_section = FTANFProcess('./utilities/test_data_section_three.xlsx', 16)
    test_section.build_header()
    captured = capsys.readouterr()
    assert captured.out == "Opening Sheet: Section 3 Aggregate\nHEADER00000000000000000\n"

def test_section(capsys):
    test_section = FTANFProcess('./utilities/test_data_section_three.xlsx', 16)
    test_section.build_body()
    captured = capsys.readouterr()
    assert captured.out == "Opening Sheet: Section 3 Aggregate\nT600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000\n"

def test_trailer(capsys):
    test_section = FTANFProcess('./utilities/test_data_section_three.xlsx', 16)
    test_section.build_trailer()
    captured = capsys.readouterr()
    assert captured.out == "Opening Sheet: Section 3 Aggregate\nTRAILER0000000         \n"