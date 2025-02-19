"""Decoder and utility classes."""

from tdpservice.parsers.dataclasses import RawRow

from abc import ABC, abstractmethod
from enum import IntEnum, auto
import chardet
import csv
import logging
from openpyxl import load_workbook
import os
import puremagic

logger = logging.getLogger(__name__)


class Decoder(IntEnum):
    """Enum class for decoder types."""

    UTF8 = auto()
    CSV = auto()
    XLSX = auto()
    UNKNOWN = auto()


class BaseDecoder(ABC):
    """Abstract base class for all decoders."""

    def __init__(self, raw_file):
        super().__init__()
        self.raw_file = raw_file
        self.current_row_num = 1

    @abstractmethod
    def get_record_type(self, raw_data):
        """To be implemented in child class."""
        pass

    @abstractmethod
    def decode(self) -> RawRow:
        """To be implemented in child class."""
        pass


class Utf8Decoder(BaseDecoder):
    """Decoder for UTF-8 files."""

    def get_record_type(self, raw_data):
        """Get the record type based on the raw data."""
        if raw_data.startswith('HEADER'):
            return "HEADER"
        elif raw_data.startswith('TRAILER'):
            return "TRAILER"
        else:
            return raw_data[0:2]

    def decode(self):
        """Decode and yield each row."""
        for raw_data in self.raw_file:
            raw_len = len(raw_data)
            raw_data = raw_data.decode().strip('\r\n')
            record_type = self.get_record_type(raw_data)
            yield RawRow(raw_data=raw_data, raw_len=raw_len, row_num=self.current_row_num, record_type=record_type)
            self.current_row_num += 1


class CsvDecoder(BaseDecoder):
    """Decoder for csv files."""

    def __init__(self, raw_file):
        super().__init__(raw_file)
        self.csv_file = csv.reader(raw_file)

    def get_record_type(self, raw_data):
        """Get the record type based on the raw data."""
        # Until the need for more complicated logic arises, we assume this decoder is only being used for FRA files.
        return "FRA"

    def decode(self):
        """Decode and yield each row."""
        for raw_data in self.csv_file:
            raw_len = len(raw_data)
            record_type = self.get_record_type(raw_data)
            yield RawRow(raw_data=raw_data, raw_len=raw_len, row_num=self.current_row_num, record_type=record_type)
            self.current_row_num += 1


class XlsxDecoder(BaseDecoder):
    """Decoder for xlsx files."""

    def __init__(self, raw_file):
        super().__init__(raw_file)
        self.work_book = load_workbook(raw_file)

    def get_record_type(self, raw_data):
        """Get the record type based on the raw data."""
        # Until the need for more complicated logic arises, we assume this decoder is only being used for FRA files.
        return "FRA"

    def decode(self):
        """Decode and yield each row."""
        for raw_data in self.work_book.active.iter_rows(values_only=True):
            raw_len = len(raw_data)
            record_type = self.get_record_type(raw_data)
            yield RawRow(raw_data=raw_data, raw_len=raw_len, row_num=self.current_row_num, record_type=record_type)
            self.current_row_num += 1


class DecoderFactory:
    """Factory class to get/instantiate parsers."""

    @classmethod
    def get_suggested_decoder(cls, raw_file):
        """Try and determine what decoder to use based on file encoding and magic numbers."""
        # We need to guarentee that the file pointer is at the first byte
        raw_file.seek(0)

        data = raw_file.read(4096)
        char_result = chardet.detect(data)
        if char_result.get('encoding') == "ascii":
            confidence = char_result.get('confidence')
            if "csv" in os.path.splitext(raw_file.name)[-1]:
                logger.info(f"Returning CSV decoder with a confidence score of {confidence}")
                return Decoder.CSV
            logger.info(f"Returning UTF-8 decoder with a confidence score of {confidence}")
            return Decoder.UTF8
        else:
            try:
                predictions = puremagic.magic_string(data)
                most_confident = predictions[0]
                if most_confident.extension == "xlsx":
                    logger.info(f"Returning XLSX decoder with a confidence score of {most_confident.confidence}")
                    return Decoder.XLSX
            except puremagic.PureError:
                return Decoder.UNKNOWN
        return Decoder.UNKNOWN

    @classmethod
    def get_instance(cls, raw_file):
        """Return the correct parser class to be constructed manually."""
        decoder = cls.get_suggested_decoder(raw_file)
        match decoder:
            case Decoder.UTF8:
                return Utf8Decoder(raw_file)
            case Decoder.CSV:
                return CsvDecoder(raw_file)
            case Decoder.XLSX:
                return XlsxDecoder(raw_file)
            case Decoder.UNKNOWN:
                raise ValueError("Could not determine what decoder to use for file.")
