"""Tests for dataclasses module."""

from tdpservice.parsers.dataclasses import Position, RawRow, TupleRow


def test_position():
    """Test the Position class."""
    pos1 = Position(1, 3)
    pos2 = Position(1)

    assert pos1.is_range is True
    assert len(pos1) == 2

    assert pos2.end == 2
    assert pos2.is_range is False
    assert len(pos2) == 1


def test_raw_row():
    """Test the RawRow class."""
    row = RawRow("test", 4, 4, 1, "test")

    assert row.value_at(Position(0, 2)) == "te"
    assert row.value_at_is(Position(0, 2), "te") is True
    assert row.raw_length() == 4
    assert len(row) == 4
    assert row[1] == "e"
    assert str(row) == "test"
    assert hash(row) == hash("test")
    assert row == RawRow("test", 4, 4, 1, "test")
    assert row != RawRow("test2", 4, 4, 1, "test2")


def test_tuple_row():
    """Test the TupleRow class."""
    row = TupleRow(("test", "test2"), 2, 2, 1, "test")
    raw_row = RawRow(("test", "test2"), 2, 2, 1, "test")

    assert row.value_at(Position(0)) == "test"
    assert row.value_at_is(Position(0), "test") is True
    assert row.value_at(Position(0, 2)) == ("test", "test2")
    assert row.raw_length() == 2
    assert len(row) == 2
    assert row[1] == "test2"
    assert str(row) == "('test', 'test2')"
    assert hash(row) == hash(("test", "test2"))
    assert row == raw_row
    assert row == TupleRow(("test", "test2"), 2, 2, 1, "test")
    assert row != RawRow("test", 4, 4, 1, "test")
