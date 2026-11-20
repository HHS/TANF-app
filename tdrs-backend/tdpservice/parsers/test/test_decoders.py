"""Test the implementation of the decoders with realistic datafiles."""

import os
from unittest.mock import MagicMock, patch

import pytest
import puremagic
from django.core.files.uploadedfile import SimpleUploadedFile

from tdpservice.parsers.dataclasses import RawRow, TupleRow
from tdpservice.parsers.decoders import (
    CsvDecoder,
    Decoder,
    DecoderFactory,
    Utf8Decoder,
    XlsxDecoder,
    _strip_trailing_substitute_characters,
)


class TestDecoderFactory:
    """Tests for decoder selection and decoding."""

    def test_strip_trailing_substitute_characters_empty(self):
        """Test stripping substitute characters from empty list."""
        assert _strip_trailing_substitute_characters([]) == []

    @pytest.mark.django_db
    def test_utf8_decoder(self, small_correct_file):
        """Test UTF8 decoder is selected and decodes data."""
        decoder = DecoderFactory.get_instance(small_correct_file.file)
        assert isinstance(decoder, Utf8Decoder)
        assert decoder.raw_file == small_correct_file.file
        header_row = next(decoder.decode())
        assert isinstance(header_row, RawRow)
        assert isinstance(header_row.data, str)
        assert header_row.data == "HEADER20204A06   TAN1 D"

    @pytest.mark.django_db
    def test_utf8_decoder_record_types(self, small_correct_file):
        """Test UTF8 decoder record type detection."""
        decoder = DecoderFactory.get_instance(small_correct_file.file)
        assert decoder.get_record_type("HEADER20204A06") == "HEADER"
        assert decoder.get_record_type("TRAILER0000001") == "TRAILER"
        assert decoder.get_record_type("T1202010111111") == "T1"

    @pytest.mark.django_db
    def test_utf8_decoder_get_header(self, small_correct_file):
        """Test UTF8 decoder get_header."""
        decoder = DecoderFactory.get_instance(small_correct_file.file)
        header = decoder.get_header()
        assert isinstance(header, RawRow)
        assert header.record_type == "HEADER"
        assert header.data == "HEADER20204A06   TAN1 D"

    @pytest.mark.django_db
    def test_csv_decoder(self, fra_csv):
        """Test CSV decoder is selected and decodes data."""
        decoder = DecoderFactory.get_instance(fra_csv.file)
        assert isinstance(decoder, CsvDecoder)
        assert decoder.raw_file == fra_csv.file
        first_row = next(decoder.decode())
        assert isinstance(first_row, TupleRow)
        assert isinstance(first_row.data, tuple)
        assert first_row.data == ("202401", "946412419")
        decoder.close()

    @pytest.mark.django_db
    def test_csv_decoder_get_header(self, fra_csv):
        """Test CSV decoder get_header."""
        decoder = DecoderFactory.get_instance(fra_csv.file)
        header = decoder.get_header()
        assert isinstance(header, TupleRow)
        assert header.record_type == "HEADER"
        assert header.data == ("202401", "946412419")
        decoder.close()

    def test_csv_decoder_decode_filters_empty_and_comment_rows(self):
        """Test CSV decoder ignores comment lines and empty rows."""
        csv_content = b"col1,col2\n#comment line\n,\n\n202401,123456789\n"
        uploaded = SimpleUploadedFile("test_filter.csv", csv_content)
        with CsvDecoder(uploaded) as decoder:
            rows = list(decoder.decode())
            assert len(rows) == 2
            assert rows[0].data == ("col1", "col2")
            assert rows[1].data == ("202401", "123456789")

    @pytest.mark.django_db
    def test_csv_decoder_strips_trailing_sub_character(
        self, fra_csv_with_sub_character
    ):
        """Test CSV decoder ignores a legacy DOS EOF marker."""
        decoder = DecoderFactory.get_instance(fra_csv_with_sub_character.file)

        rows = list(decoder.decode())

        assert len(rows) == 28
        assert rows[-1].data == ("202504", "912345678")
        assert all("\x1a" not in value for row in rows for value in row.data)
        decoder.close()

    @pytest.mark.django_db
    def test_csv_decoder_close_exception_handled(self, fra_csv):
        """Test CSV decoder close handles and logs exceptions gracefully."""
        decoder = DecoderFactory.get_instance(fra_csv.file)
        with patch("os.remove", side_effect=OSError("Disk error")):
            decoder.close()
        assert decoder.local_file is None
        assert decoder.csv_file is None

    @pytest.mark.django_db
    def test_xlsx_decoder(self, fra_xlsx):
        """Test XLSX decoder is selected and decodes data."""
        decoder = DecoderFactory.get_instance(fra_xlsx.file)
        assert isinstance(decoder, XlsxDecoder)
        assert decoder.raw_file == fra_xlsx.file
        first_row = next(decoder.decode())
        assert isinstance(first_row, TupleRow)
        assert isinstance(first_row.data, tuple)
        assert first_row.data == (202401, 946412419)
        decoder.close()

    @pytest.mark.django_db
    def test_xlsx_decoder_get_header(self, fra_xlsx):
        """Test XLSX decoder get_header."""
        decoder = DecoderFactory.get_instance(fra_xlsx.file)
        header = decoder.get_header()
        assert isinstance(header, TupleRow)
        assert header.record_type == "HEADER"
        assert header.data == (202401, 946412419)
        decoder.close()

    @pytest.mark.django_db
    def test_xlsx_decoder_decode_filters_empty_rows(self, fra_empty_first_row_xlsx):
        """Test XLSX decoder correctly skips empty rows."""
        decoder = DecoderFactory.get_instance(fra_empty_first_row_xlsx.file)
        rows = list(decoder.decode())
        assert len(rows) > 0
        decoder.close()

    @pytest.mark.django_db
    def test_xlsx_decoder_close_exception_handled(self, fra_xlsx):
        """Test XLSX decoder close handles and logs exceptions gracefully."""
        decoder = DecoderFactory.get_instance(fra_xlsx.file)
        with patch.object(decoder.work_book, "close", side_effect=Exception("Workbook error")):
            decoder.close()
        assert decoder.work_book is None

    @pytest.mark.django_db
    def test_xlsx_decoder_multisheet(self, fra_multi_sheet_xlsx):
        """Test XLSX decoder is selected and decodes data."""
        decoder = DecoderFactory.get_instance(fra_multi_sheet_xlsx.file)
        assert isinstance(decoder, XlsxDecoder)
        assert decoder.raw_file == fra_multi_sheet_xlsx.file
        first_row = next(decoder.decode())
        assert isinstance(first_row, TupleRow)
        assert isinstance(first_row.data, tuple)
        assert first_row.data == (202401, 946412419)
        decoder.close()

    @pytest.mark.django_db
    def test_empty_file_decoder(self, empty_file):
        """Test UTF8 decoder is selected on empty file with no extension."""
        with pytest.raises(StopIteration):
            decoder = DecoderFactory.get_instance(empty_file.file)
            assert isinstance(decoder, Utf8Decoder)
            assert decoder.raw_file == empty_file.file

            # Shouldn't be able to decode anything since file is empty
            next(decoder.decode())

    def test_empty_csv_file_decoder(self):
        """Test CSV decoder is selected for empty file with .csv extension."""
        uploaded = SimpleUploadedFile("empty_file.csv", b"")
        assert DecoderFactory.get_suggested_decoder(uploaded) == Decoder.CSV

    def test_empty_xlsx_file_decoder(self):
        """Test XLSX decoder is selected for empty file with .xlsx extension."""
        uploaded = SimpleUploadedFile("empty_file.xlsx", b"")
        assert DecoderFactory.get_suggested_decoder(uploaded) == Decoder.XLSX

    @pytest.mark.django_db
    def test_unknown_decoder(self, unknown_png):
        """Test unknown decoder."""
        with pytest.raises(ValueError) as e:
            DecoderFactory.get_instance(unknown_png.file)
            assert repr(e) == "Could not determine what decoder to use for file."
        assert unknown_png.file.closed is True

    def test_unknown_decoder_closes_file(self):
        """Test DecoderFactory closes raw_file when decoder is UNKNOWN."""
        uploaded = SimpleUploadedFile("unknown.bin", b"\x00\x01\x02\x03")
        with patch.object(
            DecoderFactory, "get_suggested_decoder", return_value=Decoder.UNKNOWN
        ):
            with pytest.raises(
                ValueError, match="Could not determine what decoder to use for file."
            ):
                DecoderFactory.get_instance(uploaded)
        assert uploaded.closed is True

    def test_decoder_factory_closes_file_on_exception(self):
        """Test DecoderFactory closes raw_file and propagates original exception when get_suggested_decoder fails."""
        uploaded = SimpleUploadedFile("test.bin", b"\x80\x81\x82\x83")
        with patch.object(
            DecoderFactory,
            "get_suggested_decoder",
            side_effect=RuntimeError("Detection error"),
        ):
            with pytest.raises(RuntimeError):
                DecoderFactory.get_instance(uploaded)
        assert uploaded.closed is True

    def test_csv_decoder_closes_file_on_init_failure(self):
        """Test CsvDecoder closes raw_file if _open_as_csv fails."""
        uploaded = SimpleUploadedFile("test.csv", b"col1,col2\nval1,val2\n")
        with patch.object(CsvDecoder, "_open_as_csv", side_effect=OSError("Disk full")):
            with pytest.raises(OSError):
                CsvDecoder(uploaded)
        assert uploaded.closed is True

    def test_xlsx_decoder_closes_file_on_init_failure(self):
        """Test XlsxDecoder closes raw_file if load_workbook fails."""
        uploaded = SimpleUploadedFile("test.xlsx", b"invalid_xlsx_content")
        with pytest.raises(Exception):
            XlsxDecoder(uploaded)
        assert uploaded.closed is True

    def test_puremagic_pure_error_returns_unknown(self):
        """Test puremagic PureError returns UNKNOWN decoder."""
        uploaded = SimpleUploadedFile("test.bin", b"\x80\x81\x82\x83")
        with patch("puremagic.magic_string", side_effect=puremagic.PureError("Magic error")):
            assert DecoderFactory.get_suggested_decoder(uploaded) == Decoder.UNKNOWN

    def test_puremagic_non_xlsx_returns_unknown(self):
        """Test puremagic prediction with non-xlsx extension returns UNKNOWN decoder."""
        mock_prediction = MagicMock()
        mock_prediction.extension = "pdf"
        uploaded = SimpleUploadedFile("test.bin", b"\x80\x81\x82\x83")
        with patch("puremagic.magic_string", return_value=[mock_prediction]):
            assert DecoderFactory.get_suggested_decoder(uploaded) == Decoder.UNKNOWN

    @pytest.mark.django_db
    def test_file_offset(self, small_correct_file):
        """Test raw length matches file length."""
        decoder = DecoderFactory.get_instance(small_correct_file.file)
        assert isinstance(decoder, Utf8Decoder)
        assert decoder.raw_file == small_correct_file.file
        raw_length = 0
        decoded_length = 0
        for row in decoder.decode():
            assert "\n" not in row.data
            assert "\r" not in row.data
            raw_length += row.raw_length()
            decoded_length += len(row)
        assert raw_length == len(small_correct_file.file)
        assert decoded_length != raw_length
        decoder.close()

    def test_base_decoder_close_idempotent(self):
        """Test that calling close multiple times or with closed file is safe."""
        uploaded = SimpleUploadedFile("test.txt", b"HEADER20204A06\n")
        decoder = Utf8Decoder(uploaded)
        decoder.close()
        assert uploaded.closed is True
        # Calling close again should not raise
        decoder.close()

    def test_base_decoder_close_exception_handled(self):
        """Test that BaseDecoder close handles and logs exceptions gracefully."""
        uploaded = SimpleUploadedFile("test.txt", b"HEADER20204A06\n")
        decoder = Utf8Decoder(uploaded)
        with patch.object(uploaded, "close", side_effect=OSError("Close error")):
            # Calling close should handle exception and not raise
            decoder.close()

    def test_base_decoder_exit_suppresses_close_exception(self):
        """Test that BaseDecoder __exit__ handles close exceptions without escaping."""
        uploaded = SimpleUploadedFile("test.txt", b"HEADER20204A06\n")
        with patch.object(uploaded, "close", side_effect=OSError("Close error")):
            with Utf8Decoder(uploaded) as decoder:
                next(decoder.decode())
            # Exiting context manager should not raise close error

    @pytest.mark.django_db
    def test_utf8_decoder_close(self, small_correct_file):
        """Test that Utf8Decoder close and context manager close underlying file."""
        decoder = DecoderFactory.get_instance(small_correct_file.file)
        assert isinstance(decoder, Utf8Decoder)
        decoder.close()
        assert small_correct_file.file.closed is True

        with DecoderFactory.get_instance(small_correct_file.file) as dec:
            next(dec.decode())
        assert small_correct_file.file.closed is True

    @pytest.mark.django_db
    def test_csv_decoder_close(self, fra_csv):
        """Test that CsvDecoder close and context manager close and cleanup files."""
        decoder = DecoderFactory.get_instance(fra_csv.file)
        assert isinstance(decoder, CsvDecoder)
        local_file = decoder.local_file
        decoder.close()
        assert fra_csv.file.closed is True
        assert local_file.closed is True
        assert not os.path.exists(local_file.name)
        assert decoder.local_file is None
        assert decoder.csv_file is None

        with DecoderFactory.get_instance(fra_csv.file) as dec:
            local_file = dec.local_file
            next(dec.decode())
        assert fra_csv.file.closed is True
        assert local_file.closed is True
        assert not os.path.exists(local_file.name)
        assert dec.local_file is None
        assert dec.csv_file is None

    @pytest.mark.django_db
    def test_xlsx_decoder_close(self, fra_xlsx):
        """Test that XlsxDecoder close and context manager close workbook and raw file."""
        decoder = DecoderFactory.get_instance(fra_xlsx.file)
        assert isinstance(decoder, XlsxDecoder)
        decoder.close()
        assert fra_xlsx.file.closed is True
        assert decoder.work_book is None

        with DecoderFactory.get_instance(fra_xlsx.file) as dec:
            next(dec.decode())
        assert fra_xlsx.file.closed is True
        assert dec.work_book is None
