"""Test the implementation of the decoders with realistic datafiles."""

import pytest
from tdpservice.parsers.dataclasses import RawRow
from tdpservice.parsers.decoders import DecoderFactory, CsvDecoder, Utf8Decoder, XlsxDecoder


@pytest.mark.django_db
def test_utf8_decoder(small_correct_file):
    """Test UTF8 decoder is selected and decodes data."""
    decoder = DecoderFactory.get_instance(small_correct_file.file)
    assert type(decoder) == Utf8Decoder
    assert decoder.raw_file == small_correct_file.file
    header_row = next(decoder.decode())
    assert type(header_row) == RawRow
    assert type(header_row.data) == str
    assert header_row.data == "HEADER20204A06   TAN1 D"

@pytest.mark.django_db
def test_csv_decoder(fra_csv):
    """Test CSV decoder is selected and decodes data."""
    decoder = DecoderFactory.get_instance(fra_csv.file)
    assert type(decoder) == CsvDecoder
    assert decoder.raw_file == fra_csv.file
    first_row = next(decoder.decode())
    assert type(first_row) == RawRow
    assert type(first_row.data) == list
    assert first_row.data == ["yyyymm", "9999999999"]

@pytest.mark.django_db
def test_xlsx_decoder(fra_xlsx):
    """Test XLSX decoder is selected and decodes data."""
    decoder = DecoderFactory.get_instance(fra_xlsx.file)
    assert type(decoder) == XlsxDecoder
    assert decoder.raw_file == fra_xlsx.file
    first_row = next(decoder.decode())
    assert type(first_row) == RawRow
    assert type(first_row.data) == tuple
    assert first_row.data == ("yyyymm", 9999999999)

@pytest.mark.django_db
def test_empty_file_decoder(empty_file):
    """Test UTF8 decoder is selected on empty file with no extension."""
    with pytest.raises(StopIteration):
        decoder = DecoderFactory.get_instance(empty_file.file)
        assert type(decoder) == Utf8Decoder
        assert decoder.raw_file == empty_file.file

        # Shouldn't be able to decode anything since file is empty
        next(decoder.decode())

@pytest.mark.django_db
def test_unknown_decoder(unknown_png):
    """Test unknown decoder."""
    with pytest.raises(ValueError) as e:
        DecoderFactory.get_instance(unknown_png.file)
        assert repr(e) == "Could not determine what decoder to use for file."
