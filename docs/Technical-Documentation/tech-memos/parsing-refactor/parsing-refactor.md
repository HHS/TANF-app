# Parsing Class Based Restructure

**Audience**: TDP Software Engineers <br>
**Subject**:  Refactor Functional Parsing to Class Based Parsing <br>
**Date**:     February 6, 2025 <br>

## Summary
This technical memorandum provides a set of suggestions to refactor the structure of the parsing engine from a functional approach to a class based approach. The introduction of the FRA report type/datafiles illuminates the parsing engine's deep coupling to current datafiles structure and the engine's low conformance to SOLID principles which prevent it from being generic, easily extensible, and readable. While generic, extensible, and readable code can be achieved in a functional design, this technical memorandum argues that a class based approach will be even more so. The #method/design section provides the suggested class templates to shift the parser to a class based structure that will support the parsing of any datafile type needed, while keeping the same general interface, usage patterns as the current functional approach, and more strictly adhering to SOLID principles.

## Out of Scope
The concrete code implementation for the `FRAParser` is out of scope for this technical memorandum since parsing logic actually occurs in the `RowSchema` and `Field` classes. Also, records that span multiple rows in the raw datafile will not be accounted for.

## Method/Design

### Revisiting SchemaManager
In the early days of the parsing engine, the implementation of the `SchemaManager` class was introduced to help keep the "parse and validate" method consistent across all `RowSchema`s. The extra abstraction was introduced because certain record types in TANF/SSP/Tribal datafiles required more than one `RowSchema` to parse and validate them, e.g T3 records. The `SchemaManager` is a thin wrapper around one or more `RowSchema`s which calls each of those schema's `parse_and_validate` method on the raw row. This general parsing functionality is still desirable, however, the way in which the parsing engine constructs and makes use of the `SchemaManager` is wasteful at best. For each record in a datafile, the parsing engine gets a pre constructed instance of a `SchemaManager` via `get_schema_manager`. Because this manager object is already initialized it has to be back-populated with other information about the file, raw row, and record type so that it can successfully parse the raw row into a record.

To unify the interface of the `SchemaManager` and make it more capable it should be updated to support a larger context with respect to the file it is helping to parse. Because we know the program type and section of any datafile before parsing begins, the `SchemaManager` can be initialized once at the beginning of parsing and should contain a reference to all possible schemas associated to the datafile and not just the schema(s) associated to an individual record. The code below provides a general template for the updated `SchemaManager` based on the recommended changes in the following sections which will leverage this class.

```python
class SchemaManager:
    """Manages all RowSchema's based on a file's program type and section."""

    def __init__(self, datafile, program_type, section):
        self.datafile = datafile
        self.program_type = program_type
        self.section = section
        self.schemas = dict() # e.g. {record type: RowSchema}
        self._init_schemas()

    def _init_schemas(self):
        """Initialize the schemas associated to the file."""
        # This method should take program type and section, get the correct RowSchemas initialized, and associate them with datafile.
        pass

    def parse_and_validate(self, raw_row, generate_error):
        """Run `parse_and_validate` for each schema provided and bubble up errors."""
        # Given the raw_row, get the record type and the appropriate schemas and call parse_and_validate
        pass

    def update_encrypted_fields(self, is_encrypted):
        """Update whether schema fields are encrypted or not."""
        # This should be called at the begining of parsing after the header has been parsed and we have access to is_encrypted for TANF/SSP/Tribal
        pass
```

## Handling Different File Types
The introduction of the FRA datafile introduces the need for the parsing engine to support different file types; e.g. .csv, .xlsx, .txt, etc... To support this capability, this technical memorandum will make the assumption that any files that will need to be parsed by the parsing engine will have two characteristics. Firstly, the data from the raw file (however it is encoded) can be read row by row. Second, the data for any record in the file does NOT span more than a single row.

The parsing engine currently makes the assumptions that all files are UTF-8 encoded and delimited in some way (indexes currently). This has been a good assumption for a long time. However, that assumption is no longer generic enough with the introduction of .csv and .xlsx files. Thus, the introduction of an abstract file decoding interface is required to seamlessly iterate over each row in a raw file and pass that decoded raw row to the appropriate schema for validation and parsing.

Now, the issue with a raw row after it has been decoded is that it may or may not be delimited. However, if we consider that the data in a raw row is positional instead of delimited, a standard output with well defined behaviors can be implemented for all decoders regardless of the raw data's encoding. This can be achieved because we know the data is, at it's most generic level, tabular; i.e. the data can be defined in rows, columns, and positions within a row. We know this to be true because of the assumptions made above. Defining a standard output from the decoder will make the `RowSchema` and `Field` class interfaces and parsing logic much simpler than if they were expected to handle the true raw output of a decoded row. Thus, the code block below introduces some suggested class templates to adhere to the above recommendations.

```python
"""Decoder and utility classes."""

from abc import ABC, abstractmethod
import csv
from dataclasses import dataclass
from openpyxl import load_workbook
from typing import List, Tuple, AnyStr

@dataclass
class Position:
    start: int
    end: int | None = None

    def __init__(self, start: int, end: int = None):
        self.start = start
        self.end = end if end is not None else start + 1

@dataclass
class RawRow:
    raw_data: AnyStr | List | Tuple
    row_num: int

    def value_at(self, position: Position):
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
```

The minimal implementations above are very simple technically but provide the abstraction, interface, and ease of use desired while also allowing for further expansion so long as their interface doesn't change. The `RawRow` from the decoder's `decode` method can then be fed to the `RowSchema` and `Field` which will let the developer standardize the interface of their `parse_and_validate` methods. Each `Field` will then be able to know it's `Position`, call the `value_at` method of the `RawRow` and get it's value. Similarly to the parser classes in the following sections, it is suggested to implement a decoder factory class to abstract the decision away from the caller on what is the correct decoder. This factory can then determine the correct decoder based on the encoding and type of the file. The check to do so could be as simple as a file extension check... Or, a more appropriate and dependable method to confirm the file encoding would be to use a combination of libraries. To detect the encoding of a binary file this memo recommends [puremagic](https://pypi.org/project/puremagic/). Puremagic uses a file's "magic numbers" to determine the files encoding and is a pure Python library with no dependencies. However, if the file is not binary we want to ensure that it is UTF-8 encoded. To handle that, this memo recommends making use of the pure Python library [chardet](https://pypi.org/project/chardet/). The template below outlines such a factory class.

```python
import chardet
import puremagic
from puremagic import PureError

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

```

## Parsing Interface & Concrete Classes
Transferring the functional parsing design to a class based design requires defining an interface class which will define the expected behavior of all parser subclasses. Similarly to the decoder interface, the parser class hierarchy should be kept as generic, extensible, and as readable as possible by conforming to SOLID principles. The class interface below provides a suggested template to produce a SOLID interface for other parsers to subclass.

```python
"""Base parser logic associated to all parser classes."""

from abc import ABC, abstractmethod
from tdpservice.parsers.row_schema import SchemaManager
from tdpservice.parsers.util import SortedRecords
import DecoderFactory

class BaseParser(ABC):
    """Abstract base class for all parsers."""

    def __init__(self, datafile, dfs, section, program_type):
        super().__init__()
        self.datafile = datafile
        self.dfs = dfs
        self.section = section
        self.program_type = program_type

        # Since we know the program type and the section of the file. We can explicitely initialize the schema manager.
        # This would involve making the schema manager "smarter". That is, we need to give the manager it's section and
        # program type, then it can instantiate all of the correct row schemas and parse more explicitely.
        self.schema_manager = SchemaManager(datafile, program_type, section)

        # Initialized decoder.
        self.decoder = DecoderFactory.get_instance(datafile.file)

        self.current_line = ""
        self.current_line_num = 0
        self.errors = dict()

        # Specifying unsaved_records here may or may not work for FRA files. If not, we can move it down the
        # inheritance hierarchy.
        self.unsaved_records = SortedRecords(section)
        self.unsaved_parser_errors = dict()
        self.num_errors = 0

    @abstractmethod
    def parse_and_validate(self) -> dict:
        """To be overriden in child class."""
        # Should have the same return as parse.py::parse_datafile
        pass

    def bulk_create_records(self, header_count, flush=False):
        """Bulk create unsaved_records."""
        pass

    def bulk_create_errors(self, batch_size=5000, flush=False):
        """Bulk create unsaved_parser_errors."""
        pass

    def rollback_records(self):
        """Delete created records in the event of a failure."""
        pass

    def rollback_parser_errors(self):
        """Delete created errors in the event of a failure."""
        pass

    def create_no_records_created_pre_check_error(self):
        """Generate a precheck error if no records were created."""
        pass
```

If you look at this class and compare it to `parse.py` you should see a lot of similarity! This class aggregates a lot of the current parser's utility functions while cleaning up their interfaces. Most or all of the input parameters to the functions were easily able to be moved to class level members. Using this template, TANF/SSP/Tribal and FRA based parsers can be created. The following templates provide an suggested initial implementation.

TANF/SSP/Tribal
```python
"""TANF/SSP/Tribal parser class."""

from tdpservice.parsers.parsers.base import BaseParser
from tdpservice.parsers.decoders import Utf8Decoder

# Waiting on naming guidance from Kathryn/Alex/Lauren
class TanfSspTribalParser(BaseParser):
    """Parser for TANF, SSP, and Tribal datafiles."""

    def __init__(self, datafile, dfs, section, program_type):
        super().__init__(datafile, dfs, section, program_type)
        self.case_consistency_validator = None
        self.trailer_count = 0
        self.multiple_trailer_errors = False
        self._init_schema_manager()

    def parse_and_validate(self):
        """Parse and validate the datafile."""
        header, field_vals, is_valid = self._validate_header()
        # Initialize CaseConsistencyValidator here

        # Move a lot of code from parse.py::parse_datafile_lines here to complete parsing.
        return self.errors

    def _validate_header(self):
        """Validate header and header fields."""
        # Basically all the code from parse.py::parse_datafile can go here.

        # This should return (header, field_vals, is_valid). We need the header and field_vals dicts
        # to instantiate the CaseConsistencyValidator.
        pass

    def validate_case_consistency(self):
        """Force category four validation if we have reached the last case in the file."""
        pass

    def evaluate_trailer(self, is_last_line):
        """Validate datafile trailer and return associated errors if any."""
        pass

    def generate_trailer_errors(self):
        """Generate trailer errors if we care to see them."""
        pass

    def delete_serialized_records(self, duplicate_manager, dfs):
        """Delete all records that have already been serialized to the DB that have cat4 errors."""
        pass

```

FRA
```python
"""FRA parser class."""

from tdpservice.parsers.parsers.base import BaseParser
from tdpservice.parsers.decoders import CsvDecoder, XlsxDecoder

class FRAParser(BaseParser):
    """Parser for FRA datafiles."""

    def __init__(self, datafile, dfs, section, program_type):
        super().__init__(datafile, dfs, section, program_type)

    def parse_and_validate(self):
        """Parse and validate the datafile."""
        # Stub for FRA specific parsing logic.
        return self.errors

```

Looking at the TANF/SSP/Tribal implementation you'll notice that the remaining functions from `parse.py` that were not included in `BaseParser` now live in the concrete class. You should also note that the functions that moved into the concrete TANF/SSP/Tribal class would be implemented in almost the exact same way as they currently are in `parse.py`. Note, the implementer may choose further separate out the concrete class into a `TanfParser`, `SspParser`, and `TribalParser` if that becomes more readable or specific logic can be moved to the separate classes.

The parsing logic for FRA files will be predicated on the implementation of FRA specific `RowSchema`s and `Field`s. As long as `RowSchema` and `Field` classes keep the same interface, the `parse_and_validate` method will be very similar to `TanfSspTribalParser::parse_and_validate`.

## Parser Factory & Parsing
To tie everything up, it would be nice to have a class that we could use to get the correct parser based on a datafile's metadata. That is exactly what the factory method was created for and is what this technical memorandum suggests the implementer uses. The factory should then be leveraged inside of the `parser_task.py` file to parse and validate the incoming file. The template below provides the suggested implementation for the parser factory class and the following code block indicates how the current parsing logic can be directly swapped for the suggested class based parsers this memo has laid out.

```python
"""Factory class for all parser classes."""

from tdpservice.parsers.parsers import fra, tanf_ssp_tribal

class ParserFactory:
    """Factory class to get/instantiate parsers."""

    @classmethod
    def get_class(cls, program_type):
        """Return the correct parser class to be constructed manually."""
        match program_type:
            case "TANF" | "SSP":
                return tanf_ssp_tribal.TanfSspTribalParser
            case "FRA":
                return fra.FRAParser
            case _:
                raise ValueError(f"No parser available for program type: {program_type}.")

    @classmethod
    def get_instance(cls, **kwargs):
        """Construct parser instance with the given kwargs."""
        program_type = kwargs.get('program_type', None)
        match program_type:
            case "TANF" | "SSP":
                return tanf_ssp_tribal.TanfSspTribalParser(**kwargs)
            case "FRA":
                return fra.FRAParser(**kwargs)
            case _:
                raise ValueError(f"No parser available for program type: {program_type}.")

```

Usage in `parser_task.py`.
```python
# Other imports ommitted
from tdpservice.parsers.parsers.factory import ParserFactory

# Other functions ommitted

@shared_task
def parse(data_file_id, reparse_id=None):
    """Send data file for processing."""
    # passing the data file FileField across redis was rendering non-serializable failures, doing the below lookup
    # to avoid those. I suppose good practice to not store/serializer large file contents in memory when stored in redis
    # for undetermined amount of time.
    try:
        data_file = DataFile.objects.get(id=data_file_id)
        logger.info(f"DataFile parsing started for file {data_file.filename}")

        file_meta = None
        if reparse_id:
            file_meta = ReparseFileMeta.objects.get(data_file_id=data_file_id, reparse_meta_id=reparse_id)
            file_meta.started_at = timezone.now()
            file_meta.save()

        dfs = DataFileSummary.objects.create(datafile=data_file, status=DataFileSummary.Status.PENDING)
        parser = ParserFactory.get_instance(datafile=data_file, dfs=dfs,
                                            section=data_file.section,
                                            program_type=data_file.program_type,
                                            is_program_audit=data_file.is_program_audit)
        errors = parser.parse_and_validate()
        # Rest of the file is exactly the same and is ommitted for brevity.
```

## Affected Systems
- This change effects almost the entire application. As such an exhaustive list is omitted.

## Use and Test cases to consider
- All current `test_parse.py` tests should leverage a new fixture to get the correct parser from the suggested factory. The calls to `parse.parse_datafile` should be replaced with the parser class' `parse_and_validate` method. Everything else in the tests should remain exactly the same.
- Consider adding stub tests for FRA datafiles
- Provide tests for the parser factory class
- Provide tests for the decoder
