"""Constants for parser classes."""

from tdpservice.parsers.dataclasses import Position

HEADER_POSITION = Position(0, 6)
TRAILER_POSITION = Position(0, 7)

SSN_AREA_NUMBER_POSITION = slice(0, 3)
SSN_GROUP_NUMBER_POSITION = slice(3, 5)
SSN_SERIAL_NUMBER_POSITION = slice(5, 9)
INVALID_SSN_AREA_NUMBERS = ["000", "666"]
INVALID_SSN_GROUP_NUMBERS = ["00"]
INVALID_SSN_SERIAL_NUMBERS = ["0000"]
