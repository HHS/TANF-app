"""Class definition for record duplicate class and helper classes."""
from django.conf import settings
from enum import IntEnum
from .models import ParserErrorCategoryChoices

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


class CaseDuplicateDetector:
    """Container class.

    Container class to manage records of the same case, cases that should be removed because of category 4 errors,
    and to perform exact and partial duplicate detection of the records (a category 4 error type).
    """

    def __init__(self, my_hash, manager_error_dict, generate_error):
        self.my_hash = my_hash
        self.manager_error_dict = manager_error_dict
        self.generate_error = generate_error
        self.record_ids = dict()
        self.record_hashes = dict()
        self.partial_hashes = dict()
        self.error_precedence = ErrorPrecedence()
        self.num_errors = 0
        self.should_remove_from_db = False
        self.current_line_number = None

    def set_should_remove_from_db(self, should_remove):
        """Set should remove from DB."""
        self.should_remove_from_db = should_remove

    def has_errors(self):
        """Return case duplicate error state."""
        return self.num_errors > 0

    def get_records_for_post_parse_deletion(self):
        """Return record ids if case has duplicate errors."""
        if self.num_errors > 0 and self.should_remove_from_db:
            return self.record_ids
        return dict()

    def __generate_error(self, err_msg, record, schema, has_precedence, is_new_max_precedence):
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
                        schema=schema,
                        record=record,
                        field=None,
                        error_message=err_msg,
                    )
            if is_new_max_precedence:
                self.manager_error_dict[self.my_hash] = [error]
            else:
                self.manager_error_dict.setdefault(self.my_hash, []).append(error)
            self.num_errors = len(self.manager_error_dict[self.my_hash])

    def __get_partial_dup_error_msg(self, schema, record_type, curr_line_number, existing_line_number):
        """Generate partial duplicate error message with friendly names."""
        field_names = schema.get_partial_hash_members_func()
        err_msg = (f"Partial duplicate record detected with record type "
                   f"{record_type} at line {curr_line_number}. Record is a partial duplicate of the "
                   f"record at line number {existing_line_number}. Duplicated fields causing error: ")
        for i, name in enumerate(field_names):
            if i == len(field_names) - 1:
                err_msg += f"and {schema.get_field_by_name(name).friendly_name}."
            else:
                err_msg += f"{schema.get_field_by_name(name).friendly_name}, "
        return err_msg

    def add_case_member(self, record, schema, line, line_number):
        """Add case member and generate errors if needed.

        @param record: a Django model representing a datafile record
        @param schema: the schema from which the record was created
        @param line: the raw string line representing the record
        @param line_number: the line number the record was generated from in the datafile
        @return: the number of duplicate errors
        """
        # We do not run duplicate detection for records that have been generated on the same line: T3, M3, T6, M6, T7,
        # M7. This is because we would incorrectly generate both duplicate and partial duplicate errors.
        if self.current_line_number is None or self.current_line_number != line_number:
            self.current_line_number = line_number
            self.record_ids.setdefault(schema.document, []).append(record.id)
            err_msg = None
            has_precedence = False
            is_new_max_precedence = False

            line_hash, partial_hash = schema.generate_hashes_func(line, record)
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

            self.__generate_error(err_msg, record, schema, has_precedence, is_new_max_precedence)
            if line_hash not in self.record_hashes:
                self.record_hashes[line_hash] = line_number
            if partial_hash is not None and partial_hash not in self.partial_hashes:
                self.partial_hashes[partial_hash] = line_number

        return self.num_errors


class DuplicateManager:
    """Manages all CaseDuplicateDetectors and their errors."""

    def __init__(self, generate_error):
        self.case_duplicate_detectors = dict()
        self.generate_error = generate_error
        self.generated_errors = dict()

    def add_record(self, record, case_hash, schema, line, line_number):
        """Add record to CaseDuplicateDetector and return whether the record's case has errors.

        @param record: a Django model representing a datafile record
        @param case_hash: a hash value representing the @record's unique case
        @param schema: the schema from which the record was created
        @param line: the raw string from the datafile representing the record
        @param line_number: the line number the record was generated from in the datafile
        @return: the number of duplicate errors
        """
        if case_hash not in self.case_duplicate_detectors:
            case_duplicate_detector = CaseDuplicateDetector(case_hash, self.generated_errors, self.generate_error)
            self.case_duplicate_detectors[case_hash] = case_duplicate_detector
        return self.case_duplicate_detectors[case_hash].add_case_member(record, schema, line, line_number)

    def get_generated_errors(self):
        """Return all errors from all CaseDuplicateDetectors."""
        # TODO: Test having the dup manager return it's errors on each iteration and let case consistency manage it.
        generated_errors = list()
        for errors in self.generated_errors.values():
            generated_errors.extend(errors)
        return generated_errors

    def clear_errors(self):
        """Clear all generated errors."""
        # We MUST call .clear() here instead of re-assigning a new dict() because the case_duplicate_detectors have a
        # reference to this dictionary. Re-assigning the dictionary means the case_duplicate_detectors lose their
        # reference.
        self.generated_errors.clear()

    def get_records_to_remove(self):
        """Return dictionary of document:[errors]."""
        records_to_remove = dict()
        for case_duplicate_detector in self.case_duplicate_detectors.values():
            for document, ids in case_duplicate_detector.get_records_for_post_parse_deletion().items():
                records_to_remove.setdefault(document, []).extend(ids)

        return records_to_remove

    def update_removed(self, case_hash, was_removed):
        """Notify CaseDuplicateDetectors whether case could or could not be removed from memory."""
        case_duplicate_detector = self.case_duplicate_detectors.get(case_hash, False)
        if case_duplicate_detector:
            if was_removed:
                case_duplicate_detector.set_should_remove_from_db(False)
            else:
                case_duplicate_detector.set_should_remove_from_db(True)
