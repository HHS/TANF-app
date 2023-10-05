"""Datafile field representations."""

import logging

logger = logging.getLogger(__name__)

def value_is_empty(value, length):
    """Handle 'empty' values as field inputs."""
    empty_values = [
        ' '*length,  # '     '
        '#'*length,  # '#####'
        '_'*length,  # '_____'
    ]

    return value is None or value in empty_values


class Field:
    """Provides a mapping between a field name and its position."""

    def __init__(self, item, name, type, startIndex, endIndex, required=True, validators=[]):
        self.item = item
        self.name = name
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

        if value_is_empty(value, self.endIndex-self.startIndex):
            logger.debug(f"Field: '{self.name}' at position: [{self.startIndex}, {self.endIndex}) is empty.")
            return None

        match self.type:
            case 'number':
                try:
                    value = int(value)
                    return value
                except ValueError:
                    logger.error(f"Error parsing field value: {value} to integer.")
                    return None
            case 'string':
                return value
            case _:
                logger.warn(f"Unknown field type: {self.type}.")
                return None

class TransformField(Field):
    """Represents a field that requires some transformation before serializing."""

    def __init__(self, transform_func, item, name, type, startIndex, endIndex, required=True, validators=[], **kwargs):
        super().__init__(item, name, type, startIndex, endIndex, required, validators)
        self.transform_func = transform_func
        self.kwargs = kwargs

    def parse_value(self, line):
        """Parse and transform the value for a field given a line, startIndex, endIndex, and field type."""
        value = super().parse_value(line)
        return self.transform_func(value, **self.kwargs)
