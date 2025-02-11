"""Decoder and utility classes."""

from abc import ABC, abstractmethod
import chardet
import csv
from dataclasses import dataclass
from openpyxl import load_workbook
import puremagic
from typing import List, Tuple



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
    row_num: int
    type: str

    def value_at(self, position: Position):
        """Get value at position."""
        return self.raw_data[position.start:position.end]

class BaseDecoder(ABC):
    """Abstract base class for all decoders."""

    def __init__(self, raw_file):
        super().__init__()
        self.raw_file = raw_file
        self.current_row = 0

    @abstractmethod
    def decode(self) -> RawRow:
        """To be implemented in child class."""
        pass


class Utf8Decoder(BaseDecoder):
    """Decoder for UTF-8 files."""

    def decode(self):
        """Decode and yield each row."""
        for row in self.raw_file:
            yield RawRow(raw_data=row.decode().strip('\r\n'), row_num=self.current_row)
            self.current_row += 1


class CsvDecoder(BaseDecoder):
    """Decoder for csv files."""

    def __init__(self, raw_file):
        super().__init__(raw_file)
        self.csv_file = csv.reader(raw_file)

    def decode(self):
        """Decode and yield each row."""
        for row in self.csv_file:
            yield RawRow(raw_data=row, row_num=self.current_row)
            self.current_row += 1


class XlsxDecoder(BaseDecoder):
    """Decoder for xlsx files."""

    def __init__(self, raw_file):
        super().__init__(raw_file)
        self.work_book = load_workbook(raw_file)

    def decode(self):
        """Decode and yield each row."""
        for row in self.work_book.active.iter_rows(values_only=True):
            yield RawRow(raw_data=row, row_num=self.current_row)
            self.current_row += 1


class DecoderFactory:
    """Factory class to get/instantiate parsers."""

    @classmethod
    def get_suggested_decoder(raw_file):
        # use puremagic and chardet to determine the correct decoder. This should probably return an enum
        return info

    @classmethod
    def get_instance(cls, raw_file):
        """Return the correct parser class to be constructed manually."""
        decoder = cls.get_suggested_decoder(raw_file)
        match decoder:
            case "UTF8":
                return Utf8Decoder(raw_file)
            case "CSV":
                return CsvDecoder(raw_file)
            case "XLSX":
                return XlsxDecoder(raw_file)
            case _:
                raise ValueError(f"No decoder available for the file.")

