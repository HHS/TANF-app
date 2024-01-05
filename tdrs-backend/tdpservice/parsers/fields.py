"""Datafile field representations."""

import logging
from .validators import value_is_empty

logger = logging.getLogger(__name__)

class Field:
    """Provides a mapping between a field name and its position."""

    def __init__(
        self,
        item,
        name,
        friendly_name,
        type,
        startIndex,
        endIndex,
        required=True,
        validators=[],
    ):
        self.item = item
        self.name = name
        self.friendly_name = friendly_name
        self.type = type
        self.startIndex = startIndex
        self.endIndex = endIndex
        self.required = required
        self.validators = validators

    def create(self, item, name, length, start, end, type):
        """Create a new field."""
        return Field(item, name, type, length, start, end)

    def __repr__(self):
        """Return a string representation of the field."""
        return f"{self.name}({self.startIndex}-{self.endIndex})"

    def parse_value(self, line):
        """Parse the value for a field given a line, startIndex, endIndex, and field type."""
        value = line[self.startIndex:self.endIndex]
        value_length = self.endIndex-self.startIndex

        if len(value) < value_length or value_is_empty(value, value_length):
            logger.debug(f"Field: '{self.name}' at position: [{self.startIndex}, {self.endIndex}) is empty.")
            return None

        match self.type:
            case "number":
                try:
                    value = int(value)
                    return value
                except ValueError:
                    logger.error(f"Error parsing field value: {value} to integer.")
                    return None
            case "string":
                return value
            case _:
                logger.warn(f"Unknown field type: {self.type}.")
                return None


class TransformField(Field):
    """Represents a field that requires some transformation before serializing."""

    def __init__(self, transform_func, item, name, friendly_name, type, startIndex, endIndex, required=True,
                 validators=[], **kwargs):
        super().__init__(
            item=item,
            name=name,
            type=type,
            friendly_name=friendly_name,
            startIndex=startIndex,
            endIndex=endIndex,
            required=required,
            validators=validators)
        self.transform_func = transform_func
        self.kwargs = kwargs

    def parse_value(self, line):
        """Parse and transform the value for a field given a line, startIndex, endIndex, and field type."""
        value = super().parse_value(line)
        return self.transform_func(value, **self.kwargs)
