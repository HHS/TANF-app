"""Decoder and utility classes."""

from abc import ABC, abstractmethod
from enum import IntEnum, auto
import chardet
import csv
from dataclasses import dataclass
import logging
from openpyxl import load_workbook
import os
import puremagic
from typing import List, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Generic class representing a position in a row of data."""

    start: int
    end: int | None = None
    is_range: bool = True

    def __init__(self, start: int, end: int = None):
        self.start = start
        self.end = end if end is not None else start + 1
        self.is_range = self.end - self.start > 1

@dataclass
class RawRow:
    """Generic wrapper for indexable row data."""

    raw_data: str | List | Tuple
    raw_len: int
    row_num: int
    record_type: str

    def value_at(self, position: Position):
        """Get value at position."""
        return self.raw_data[position.start:position.end]

    def value_at_is(self, position: Position, expected_value):
        """Check if the value at position matches the expected value."""
        return self.value_at(position) == expected_value

    def __len__(self):
        """Return the length of raw_data."""
        return self.raw_len


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
        char_result = chardet.detect(raw_file.read(4096))
        if char_result.get('encoding') == "ascii":
            confidence = char_result.get('confidence')
            if "csv" in os.path.splitext(raw_file.name)[-1]:
                logger.info(f"Returning CSV decoder with a confidence score of {confidence}")
                return Decoder.CSV
            logger.info(f"Returning UTF-8 decoder with a confidence score of {confidence}")
            return Decoder.UTF8
        else:
            try:
                predictions = puremagic.magic_string(raw_file.read(4096))
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
