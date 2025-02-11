# FRA Schema Definition & Field Enhancements

**Audience**: TDP Software Engineers <br>
**Subject**:  FRA Schema Support <br>
**Date**:     February 11, 2025 <br>

## Summary
This technical memorandum provides a set of suggestions to further abstract the `RowSchema` and `Field` classes to better support the introduction of the FRA datafile type and the parser refactor. This memo highlights key areas in the `Field` and `RowSchema` classes that are not generic and should be moved down an inheritance hierarchy thus introducing the need for better interfaces for both classes.

## Out of Scope
Call out what is out of scope for this technical memorandum and should be considered in a different technical memorandum.

## Method/Design

### Abstracting the Line
The introduction of the FRA datafile brings with it the need to handle rows of data with different structure. The FRA datafile can either be a .csv or a .xlsx. It is the parser's job to parse the raw file, regardless of it's encoding, and provide that row of data to the `RowSchema` for it to parse into a record. Because a raw row of data from a .csv, .xlsx, and existing datafiles are all structurally different, a unified object is needed to wrap the raw row of data to make access to it consistent regardless of the underlying data. This object will leverage the fact that all the data the parsing engine expects to parse is tabular in nature. I.e. the particular data items in a file can be identified positionally by a row and column regardless of how the data is delimited. Refer to the `parser-refactor.md` for a more in depth explanation of the tabular nature of all datafile submissions. The following templates provide a starting point to achieve consistent parser input to the `RowSchema` and `Field` classes.

```python
from dataclasses import dataclass
from typing import List, Tuple, AnyStr

@dataclass
class Position:
    start: int
    end: int | None = None

    def __init__(self, start: int, end: int = None):
        self.start = start
        self.end = end if end is not None else start + 1

    def __len__(self):
        return self.end - self.start

@dataclass
class RawRow:
    raw_data: AnyStr | List | Tuple
    row_num: int

    def value_at(self, position: Position):
        return self.raw_data[position.start:position.end]

```

These classes are simple for the moment, but they provide a consistent and well defined interface to access the tabular data from the perspective of a `RowSchema` and `Field`. These classes are also open for extension but closed for modification to handle more complex scenarios should the situation arise.

### RowSchema
The `RowSchema` class as it stands is very coupled to the current datafile structure. Many of the features of the `RowSchema` class are not applicable to what an FRA `RowSchema` would leverage. To support using the `RowSchema` in a more general way, it needs to be updated to keep the most generic logic in a base class and let subclasses add extra functionality to suite their needs. The templates below outline a suggested path forward to accommodate a more generic `RowSchema`.

```python
# Other imports ommitted for brevity
from abc import ABC, abstractmethod
from dataclasses import dataclass
from django.db.models import Model
from typing import DefaultDict, List

@dataclass
class SchemaResult:
    record: DefaultDict | Model
    is_valid: bool
    errors: List[Model]


class RowSchema(ABC):

    def __init__(self, record_type, document, fields=None):
        super().__init__()
        self.record_type = record_type
        # This will change to "model" once elastic/kibana are officially gone
        self.document = document
        self.fields = list() if not fields else fields
        self.datafile = None

    @abstractmethod
    def parse_and_validate(self, row: RawRow, generate_error) -> SchemaResult:
        pass

    def parse_row(self, row: RawRow):
        """Create a model for the raw row based on the schema."""
        # Same, update to use RawRow
        return record

    def run_field_validators(self, instance, generate_error):
        """Run all validators for each field in the parsed model."""
        # Same
        return is_valid, errors

    def set_datafile(self, datafile):
        """Datafile setter."""
        # I personally prefer this over accessing the member explicitly even though Python allows that
        self.datafile = datafile

    def _add_field(self, item, name, length, start, end, type):
        """Add a field to the schema."""
        # Same
        pass

    def add_fields(self, fields: list):
        """Add multiple fields to the schema."""
        # Same
        pass

    def get_all_fields(self):
        """Get all fields from the schema."""
        # Same
        pass

    def get_field_values_by_names(self, row: RawRow, names={}):
        """Return dictionary of field values keyed on their name."""
        # Same, update to use RawRow
        pass

    def get_field_by_name(self, name):
        """Get field by it's name."""
        # Same
        pass


# Alex/Kathryn/Lauren provided guidance on the naming here. If the implementer chooses to lump TANF/SSP/Tribal into a
# single subclass, then the class name below could be changed to `TDRSchema`. Kathryn indicated that internally OFA
# sometimes refers TANF/SSP/Tribal datafiles as TDR (TANF Data Report) files.
class TanfSspTribalSchema(RowSchema):
    """Maps the schema for TANF/SSP/Tribal data rows."""

    def __init__(
            self,
            record_type="T1",
            document=None,
            fields=None,
            # The default hash function covers all program types with record types ending in a 6 or 7.
            generate_hashes_func=lambda line, record: (hash(line),
                                                       hash(record.RecordType)),
            should_skip_partial_dup_func=lambda record: False,
            get_partial_hash_members_func=lambda: ["RecordType"],
            preparsing_validators=[],
            postparsing_validators=[],
            quiet_preparser_errors=False,
            ):
        super().__init__(record_type, document, fields)

        self.generate_hashes_func = generate_hashes_func
        self.should_skip_partial_dup_func = should_skip_partial_dup_func
        self.get_partial_hash_members_func = get_partial_hash_members_func
        self.preparsing_validators = preparsing_validators
        self.postparsing_validators = postparsing_validators
        self.quiet_preparser_errors = quiet_preparser_errors

    def parse_and_validate(self, row: RawRow, generate_error):
        """Run all validation steps in order, and parse the given line into a record."""
        # Virtually same functionality as original RowSchema, just needs to leverage RawRow now
        return SchemaResult(record, is_valid, errors)

    def run_preparsing_validators(self, row: RawRow, generate_error):
        """Run each of the `preparsing_validator` functions in the schema against the un-parsed line."""
        # Virtually same functionality as original RowSchema, just needs to leverage RawRow now
        return is_valid, errors

    def run_postparsing_validators(self, instance, generate_error):
        """Run each of the `postparsing_validator` functions against the parsed model."""
        # Same
        return is_valid, errors


class FRASchema(RowSchema):
    """Maps the schema for FRA data rows."""

    def __init__(
            self,
            record_type="FRA_RECORD",
            document=None,
            fields=None,
            ):
        super().__init__(record_type, document, fields)

    def parse_and_validate(self, row: RawRow, generate_error):
        """Run all validation steps in order, and parse the given line into a record."""
        # Parse FRA row and run field validators, waiting for guidance on other categories of validators
        # The implementor should reference `UpdatedErrorReport.xlsx` to gain insight into appropriate validators for fields.
        errors = []

        # parse row to model
        record = self.parse_row(row)

        # run field validators
        fields_are_valid, field_errors = self.run_field_validators(record, generate_error)

        is_valid = fields_are_valid
        errors = field_errors

        return SchemaResult(record, is_valid, errors)


```

There are a few things to note from the above templates. Methods that have `# Same` in their body indicate that they would be implemented in exactly the same way as the are in the current `RowSchema` class. Only new imports have been included with the template and a distinct comment is called out since TDP is moving away from ElasticSearch and the `document` member will likely not be relevant when this is implemented. Otherwise, you will note that a very simple abstraction layer has been introduced and that all `RowSchema` subclasses have the freedom to implement their `parse_and_validate` function as they see fit. This memo also introduces the simple `SchemaResult` data class. This allows the return value of the schema's `parse_and_validate` function to be well defined and typed. This will help to prevent future developers from drilling down deep into the code to see what they should expect as a return value.


### Field
The current implementation of the `Field` class requires few changes to handle the remaining parsing functionality. This memo will generalize the `Field` class a little more and introduce some more canonical structures to replace existing static strings/magic constants. The template below provides a template for the suggested direction the implementer could follow to support the recommended changes above.

```python
from .validators.util import value_is_empty
from abc import ABC, abstractmethod
from enum import IntFlag, auto

class FieldType(IntFlag):
    NUMERIC = auto()
    ALPHA_NUMERIC = auto()


class Field:
    """Provides a mapping between a field and its position in a RawRow."""

    def __init__(
        self,
        name,
        friendly_name,
        type: FieldType,
        position: Position,
        required=True,
        validators=[],
        ignore_errors=False
    ):
        self.name = name
        self.friendly_name = friendly_name
        self.type = type
        self.position = position
        self.required = required
        self.validators = validators
        self.ignore_errors = ignore_errors

    def __repr__(self):
        """Return a string representation of the field."""
        return f"{self.name}({self.startIndex}-{self.endIndex})"

    def parse_value(self, row: RawRow):
        """Parse the value for a field given a RawRow."""
        value = row.value_at(self.position)
        value_length = len(self.position)

        if len(value) < value_length or value_is_empty(value, value_length):
            logger.debug(f"Field: '{self.name}' at position: [{self.startIndex}, {self.endIndex}) is empty.")
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


# This could technically be reabsorbed back into RowSchema since it only adds the `item` member. It's up to the
# implementer to decide what makes the most sense.
class ItemField:
    """Provides a mapping between a field name/item and its position in a RawRow."""

    def __init__(
        self,
        item,
        name,
        friendly_name,
        type,
        position: Position,
        required=True,
        validators=[],
        ignore_errors=False,
    ):
        super().__init__(name, friendly_name, type, position, required, validators, ignore_errors)
        self.item = item

    def __repr__(self):
        """Return a string representation of the field."""
        return f"{self.name}({self.position.start}-{self.position.end})"


class TransformField(ItemField):
    """Represents a field that requires some transformation before serializing."""

    def __init__(self, transform_func, item, name, friendly_name, type, position: Position, required=True,
                 validators=[], ignore_errors=False, **kwargs):
        super().__init__(
            item=item,
            name=name,
            type=type,
            friendly_name=friendly_name,
            position=position,
            required=required,
            validators=validators,
            ignore_errors=ignore_errors)
        self.transform_func = transform_func
        self.kwargs = kwargs

    def parse_value(self, row: RawRow):
        """Parse and transform the value for a field given a line, startIndex, endIndex, and field type."""
        # Same, but use row instead of line
        pass


```

The primary changes the reader should notice are the aggregation of the `Field`'s "index" members in favor of the `Position` class and the enumeration of the `type` field. Since the parser is doing all the heavy lifting to provide the `RowSchema` and subsequently it's `Field`s a consistent positional row interface, the changes needed for this class hierarchy are very simple.

## Affected Systems
- Entire parser hierarchy

## Use and Test cases to consider
- Every existing parser test should not change logically at all!
- Because the general interface of the schema class is staying the same, it is unlikely that any new tests will need to be added.
