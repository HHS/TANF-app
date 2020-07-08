import pytest
from utilites.ftanf import FTANFProcess


test_section = FTANFProcess('./test_data_section_three.xlsx', 16)

def main_interestgrion_snapshot(self):
    test_section.build_file()
    captured = capsys.readouterr()
    assert captured.out == "HEADER00000000000000000\nT100000000000000000\nTRAILER0000001\n"


# def test_pad_field_data(self):
#     padded_string = test_section.pad_field_data([2,4,4], ['T6', 124, ''])
#     assert padded_string == 'T601240000'

# def test_header(self):
#     test_section.build_header()
#     captured = capsys.readouterr()
#     assert captured.out == "HEADER00000000000000000\n"

# def test_section(self):
#     test_section.build_body()
#     captured = capsys.readouterr()
#     assert captured.out == "T100000000000000000\n"

# def test_trailer(self):
#     test_section.build_trailer()
#     captured = capsys.readouterr()
#     assert captured.out == "TRAILER0000001\n"