"""Utility data classes for the parsing engine."""

from dataclasses import dataclass, field
from enum import IntFlag, auto
from typing import Any, DefaultDict, List, Tuple

from django.db.models import Model


class FieldType(IntFlag):
    """Enum class for field types."""

    NUMERIC = auto()
    ALPHA_NUMERIC = auto()


@dataclass
class HeaderResult:
    """Header validation result class."""

    is_valid: bool
    header: dict | None = None
    program_type: str | None = None
    is_encrypted: bool = False


@dataclass
class ManagerPVResult:
    """SchemaManager parse and validate result class."""

    records: List["SchemaResult"]
    schemas: List[object]  # RowSchema causes circular import


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

    def __len__(self):
        """Return the size of the field the position represents."""
        return self.end - self.start


@dataclass(eq=False)
class RawRow:
    """Generic wrapper for indexable row data."""

    data: str | Tuple
    raw_len: int
    decoded_len: int
    row_num: int
    record_type: str

    def value_at(self, position: Position):
        """Get value at position."""
        return self.data[position.start : position.end]

    def value_at_is(self, position: Position, expected_value):
        """Check if the value at position matches the expected value."""
        return self.value_at(position) == expected_value

    def raw_length(self):
        """Return the byte length of data."""
        return self.raw_len

    def __len__(self):
        """Return the length of data."""
        return self.decoded_len

    def __getitem__(self, key):
        """Return slice from data."""
        return self.data[key]

    def __str__(self):
        """Return string representation of data."""
        return str(self.data)

    def __hash__(self):
        """Return hash of data."""
        return hash(self.data)

    def __eq__(self, value):
        """Check if value equals self."""
        if isinstance(value, RawRow):
            return self.data == value.data
        return False

    def __ne__(self, value):
        """Check if value does not equal self."""
        return not self.__eq__(value)


@dataclass(eq=False)
class TupleRow(RawRow):
    """Row class for Tuple based raw data."""

    def value_at(self, position: Position):
        """Get value at position."""
        value = self.data[position.start : position.end]
        if value is None or len(value) == 0:
            return None
        if position.is_range:
            return value
        return value[0]


@dataclass
class Result:
    """Dataclass representing a validator's evaluated result."""

    valid: bool = True
    error: str | None = None
    field_names: list = field(default_factory=list)
    deprecated: bool = False


@dataclass
class SchemaResult:
    """Datclass to encapsulating a RowSchema's parse_and_validate result."""

    record: DefaultDict | Model
    is_valid: bool
    errors: List[Model]

    def __iter__(self):
        """Allow unpacking."""
        return iter((self.record, self.is_valid, self.errors))


@dataclass
class ValidationErrorArgs:
    """Dataclass for args to `make_validator` `error_func`s."""

    value: Any
    row_schema: object  # RowSchema causes circular import
    friendly_name: str
    item_num: str
