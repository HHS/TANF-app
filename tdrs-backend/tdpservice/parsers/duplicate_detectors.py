"""Class definition for record duplicate class and helper classes."""
from abc import ABC, abstractmethod
from django.conf import settings
from enum import IntEnum
from .models import ParserErrorCategoryChoices
from tdpservice.parsers.dataclasses import RawRow

class ErrorLevel(IntEnum):
    """Error level enumerations for precedence."""

    DUPLICATE = 0
    PARTIAL_DUPLICATE = 1
    NONE = 2  # This should always be the last level in the list


class ErrorPrecedence:
    """Data structure to manage error precedence."""

    def __init__(self):
        self.curr_max_precedence = ErrorLevel.NONE

    def has_precedence(self, error_level):
        """Return tuple of bools: (has_precidence, is_new_max_precedence)."""
        if settings.IGNORE_DUPLICATE_ERROR_PRECEDENCE:
            return (True, False)
        if self.curr_max_precedence == ErrorLevel.NONE:
            self.curr_max_precedence = error_level
            return (True, True)
        elif self.curr_max_precedence > error_level:
            self.curr_max_precedence = error_level
            return (True, True)
        elif self.curr_max_precedence == error_level:
            return (True, False)
        else:
            return (False, False)


class DuplicateDetectorFactory:
    """Factory class for DuplicateDetector."""

    @staticmethod
    def create(schema, detector_hash, manager_error_dict, generate_error):
        """Create a DuplicateDetector instance."""
        match schema.record_type:
            case "TE1":
                return TE1DuplicateDetector(detector_hash, manager_error_dict, generate_error)
            case _:
                return CaseDuplicateDetector(detector_hash, manager_error_dict, generate_error)


class DuplicateDetector(ABC):
    """Abstract base class for duplicate detectors."""

    def __init__(self, my_hash, manager_error_dict, generate_error):
        self.my_hash = my_hash
        ################################################################################################################
        # WARNING
        self.manager_error_dict = manager_error_dict
        # Do not change/re-assign this dictionary unless you know exactly what you're doing! This object is owned by the
        # DuplicateManager object. The CaseDuplicateDetector has a reference to this object as a performance
        # optimization which lets the DuplicateManager avoid having to iterate over all CaseDuplicateDetectors to get
        # all of the duplicate errors.
        ################################################################################################################
        self.generate_error = generate_error
        self.record_ids = dict()
        self.record_hashes = dict()
        self.partial_hashes = dict()
        self.error_precedence = ErrorPrecedence()
        self.num_errors = 0
        self.should_remove_from_db = False
        self.current_line_number = None

    @abstractmethod
    def add_member(self, record, schema, row: RawRow, line_number):
        """Add record and generate errors if needed."""
        pass

    def set_should_remove_from_db(self, should_remove):
        """Set should remove from DB."""
        self.should_remove_from_db = should_remove

    def has_errors(self):
        """Return case duplicate error state."""
        return self.num_errors > 0

    def get_num_errors(self):
        """Return the number of errors."""
        return self.num_errors

    def get_records_for_post_parse_deletion(self):
        """Return record ids if case has duplicate errors."""
        if self.should_remove_from_db:
            return self.record_ids
        return dict()

    def _generate_error(self, err_msg, record, schema, line_number, has_precedence, is_new_max_precedence):
        """Add an error to the managers error dictionary.

        @param err_msg: string representation of the error message
        @param record: a Django model representing a datafile record
        @param schema: the schema from which the record was created
        @param has_precedence: boolean indicating if this incoming error has equivalent precedence to current errors
        @param is_new_max_precedence: boolean indicating if this error has the new max precedence
        """
        if has_precedence:
            error = self.generate_error(
                        error_category=ParserErrorCategoryChoices.CASE_CONSISTENCY,
                        line_number=line_number,
                        schema=schema,
                        record=record,
                        field=schema.fields,
                        error_message=err_msg,
                    )
            if is_new_max_precedence:
                self.manager_error_dict[self.my_hash] = [error]
            else:
                self.manager_error_dict.setdefault(self.my_hash, []).append(error)
            self.num_errors = len(self.manager_error_dict[self.my_hash])


class TE1DuplicateDetector(DuplicateDetector):
    """Container class.

    Container class to manage TE1 records, records that should be removed because of category 4 errors,
    and to perform exact and partial duplicate detection of the records (a category 4 error type).
    """

    def __init__(self, my_hash, manager_error_dict, generate_error):
        super().__init__(my_hash, manager_error_dict, generate_error)

    def add_member(self, record, schema, row: RawRow, line_number):
        """Add TE1 record and generate errors if needed. Only performing exact duplicate detection.

        @param record: a Django model representing a datafile record
        @param schema: the schema from which the record was created
        @param row: the RawRow parsed from the decoder
        @param line_number: the line number the record was generated from in the datafile
        """
        # Add all records the detector receives to id dictionary. That way a line that has more than one record
        # created from it will have all of it's records appropriately marked for deletion if need be.
        self.record_ids.setdefault(schema.model, []).append(record.id)

        self.current_line_number = line_number
        err_msg = None
        has_precedence = False
        is_new_max_precedence = False

        line_hash, partial_hash = schema.generate_hashes_func(row, record)

        if line_hash in self.record_hashes:
            has_precedence, is_new_max_precedence = self.error_precedence.has_precedence(ErrorLevel.DUPLICATE)
            existing_record_line_number = self.record_hashes[line_hash]
            err_msg = ("Duplicate Social Security Number within a month. Check that individual SSNs "
                       "within a single exit month are not included more than once. "
                       f"SSN is a duplicate of the record at line number {existing_record_line_number}.")

        self._generate_error(err_msg, record, schema, line_number, has_precedence, is_new_max_precedence)
        if line_hash not in self.record_hashes:
            self.record_hashes[line_hash] = line_number


class CaseDuplicateDetector(DuplicateDetector):
    """Container class.

    Container class to manage records of the same TANF case, cases that should be removed because of category 4 errors,
    and to perform exact and partial duplicate detection of the records (a category 4 error type).
    """

    def __init__(self, my_hash, manager_error_dict, generate_error):
        super().__init__(my_hash, manager_error_dict, generate_error)

    def __get_partial_dup_error_msg(self, schema, record_type, curr_line_number, existing_line_number):
        """Generate partial duplicate error message with friendly names."""
        field_names = schema.get_partial_hash_members_func()
        err_msg = (f"Partial duplicate record detected with record type "
                   f"{record_type} at line {curr_line_number}. Record is a partial duplicate of the "
                   f"record at line number {existing_line_number}. Duplicated fields causing error: ")
        for i, name in enumerate(field_names):
            field = schema.get_field_by_name(name)
            item_and_name = f"Item {field.item} ({field.friendly_name})"
            if i == len(field_names) - 1 and len(field_names) != 1:
                err_msg += f"and {item_and_name}."
            elif len(field_names) == 1:
                err_msg += f"{item_and_name}."
            else:
                err_msg += f"{item_and_name}, "
        return err_msg

    def add_member(self, record, schema, row: RawRow, line_number):
        """Add case member and generate errors if needed.

        @param record: a Django model representing a datafile record
        @param schema: the schema from which the record was created
        @param row: the RawRow parsed from the decoder
        @param line_number: the line number the record was generated from in the datafile
        """
        # Add all records detector receives to id dictionary. That way if a line that has more than one record created
        # from it will have all of it's records appropriately marked for deletion if need be.
        self.record_ids.setdefault(schema.model, []).append(record.id)

        # We do not run duplicate detection for records that have been generated on the same line: T3, M3, T6, M6, T7,
        # M7. This is because we would incorrectly generate both duplicate and partial duplicate errors.
        if self.current_line_number is None or self.current_line_number != line_number:
            self.current_line_number = line_number
            err_msg = None
            has_precedence = False
            is_new_max_precedence = False

            line_hash, partial_hash = schema.generate_hashes_func(row, record)
            should_skip_partial_dup = schema.should_skip_partial_dup_func(record)

            if line_hash in self.record_hashes:
                has_precedence, is_new_max_precedence = self.error_precedence.has_precedence(ErrorLevel.DUPLICATE)
                existing_record_line_number = self.record_hashes[line_hash]
                err_msg = (f"Duplicate record detected with record type "
                           f"{record.RecordType} at line {line_number}. Record is a duplicate of the record at "
                           f"line number {existing_record_line_number}.")
            elif not should_skip_partial_dup and partial_hash in self.partial_hashes:
                has_precedence, is_new_max_precedence = self.error_precedence.has_precedence(
                    ErrorLevel.PARTIAL_DUPLICATE)
                existing_record_line_number = self.partial_hashes[partial_hash]
                err_msg = self.__get_partial_dup_error_msg(schema, record.RecordType,
                                                           line_number, existing_record_line_number)

            self._generate_error(err_msg, record, schema, line_number, has_precedence, is_new_max_precedence)
            if line_hash not in self.record_hashes:
                self.record_hashes[line_hash] = line_number
            if partial_hash is not None and partial_hash not in self.partial_hashes:
                self.partial_hashes[partial_hash] = line_number
