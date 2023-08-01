"""Datafile field representations."""

def value_is_empty(value, length):
    """Handle 'empty' values as field inputs."""
    empty_values = [
        ' '*length,  # '     '
        '#'*length,  # '#####'
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
            return None

        match self.type:
            case 'number':
                try:
                    value = int(value)
                    return value
                except ValueError:
                    return None
            case 'string':
                return value

def tanf_ssn_decryption_func(value, is_encrypted):
    """Decrypt TANF SSN value."""
    if is_encrypted:
        decryption_dict = {"@": "1", "9": "2", "Z": "3", "P": "4", "0": "5",
                           "#": "6", "Y": "7", "B": "8", "W": "9", "T": "0"}
        decryption_table = str.maketrans(decryption_dict)
        return value.translate(decryption_table)
    return value

def ssp_ssn_decryption_func(value, is_encrypted):
    """Decrypt SSP SSN value."""
    if is_encrypted:
        decryption_dict = {"@": "1", "9": "2", "Z": "3", "P": "4", "0": "5",
                           "#": "6", "Y": "7", "B": "8", "W": "9", "T": "0"}
        decryption_table = str.maketrans(decryption_dict)
        return value.translate(decryption_table)
    return value

class EncryptedField(Field):
    """Represents an encrypted field and its position."""

    def __init__(self, decryption_func, item, name, type, startIndex, endIndex, required=True, validators=[]):
        super().__init__(item, name, type, startIndex, endIndex, required, validators)
        self.decryption_func = decryption_func
        self.is_encrypted = False

    def parse_value(self, line):
        """Parse and decrypt the value for a field given a line, startIndex, endIndex, and field type."""
        value = line[self.startIndex:self.endIndex]

        if value_is_empty(value, self.endIndex-self.startIndex):
            return None

        match self.type:
            case 'string':
                return self.decryption_func(value, self.is_encrypted)
            case _:
                return None
