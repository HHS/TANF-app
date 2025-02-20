"""Datafile field representations."""

import logging
from tdpservice.parsers.validators.util import value_is_empty
from tdpservice.parsers.dataclasses import FieldType, Position, RawRow

logger = logging.getLogger(__name__)


class Field:
    """Provides a mapping between a field name and its position."""

    def __init__(
        self,
        item,
        name,
        friendly_name,
        type: FieldType,
        position: Position = None,
        required=True,
        validators=[],
        ignore_errors=False,
        **kwargs,
    ):
        self.item = item
        self.name = name
        self.friendly_name = friendly_name
        self.type = type
        self.position = position
        self._init_position(**kwargs)
        self.required = required
        self.validators = validators
        self.ignore_errors = ignore_errors

    def _init_position(self, **kwargs):
        """Initialize position based on `startIndex` and `endIndex`."""
        # This is a Python hack to get constructor overloading which avoids changing hundreds of Field class
        # constructions with `startIndex` and `endIndex`.
        start = kwargs.get("startIndex", None)
        end = kwargs.get("endIndex", None)
        if self.position is not None:
            return
        elif start is not None and end is not None:
            self.position = Position(start, end)
            return

        raise ValueError("You must pass a position or a startIndex and endIndex.")

    def create(self, item, name, length, start, end, type):
        """Create a new field."""
        return Field(item, name, type, length, start, end)

    def __repr__(self):
        """Return a string representation of the field."""
        return f"{self.name}({self.position.start}-{self.position.end})"

    def parse_value(self, row: RawRow):
        """Parse the value for a field given a row, posiiton, and field type."""
        value = row.value_at(self.position)
        value_length = len(self.position)

        if len(value) < value_length or value_is_empty(value, value_length):
            logger.debug(f"Field: '{self.name}' at position: [{self.position.start}, {self.position.end}) is empty.")
            return None

        match self.type:
            case FieldType.NUMERIC:
                try:
                    value = int(value)
                    return value
                except ValueError:
                    logger.error(f"Error parsing field {self.name} value to integer.")
                    return None
            case FieldType.ALPHA_NUMERIC:
                return value
            case _:
                logger.warning(f"Unknown field type: {self.type}.")
                return None


class TransformField(Field):
    """Represents a field that requires some transformation before serializing."""

    def __init__(self, transform_func, item, name, friendly_name, type, startIndex, endIndex, required=True,
                 validators=[], ignore_errors=False, **kwargs):
        super().__init__(
            item=item,
            name=name,
            type=type,
            friendly_name=friendly_name,
            startIndex=startIndex,
            endIndex=endIndex,
            required=required,
            validators=validators,
            ignore_errors=ignore_errors,
            **kwargs)
        self.transform_func = transform_func
        self.kwargs = kwargs

    def parse_value(self, row: RawRow):
        """Parse and transform the value for a field given a row, position, and field type."""
        value = super().parse_value(row)
        try:
            return_value = self.transform_func(value, **self.kwargs)
            return return_value
        except Exception:
            raise ValueError(f"Error transforming field value for field: {self.name}.")
