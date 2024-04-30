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


class CaseHashtainer:
    """Container class to manage hashed values for records of the same CASE_NUMBER and RPT_MONTH_YEAR."""

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

    def __get_partial_hash(self, record):
        partial_hash = None
        if record.RecordType in {"T1", "T4"}:
            partial_hash = hash(record.RecordType + str(record.RPT_MONTH_YEAR) + record.CASE_NUMBER)
        elif record.RecordType in {"T2", "T3", "T5"}:
            partial_hash = hash(record.RecordType + str(record.RPT_MONTH_YEAR) + record.CASE_NUMBER +
                                str(record.FAMILY_AFFILIATION) + record.DATE_OF_BIRTH + record.SSN)
        return partial_hash

    def __skip_partial(self, record):
        skip_partial = False
        if record.RecordType == "T2":
            skip_partial = record.FAMILY_AFFILIATION in {3, 5}
        if record.RecordType == "T3":
            skip_partial = record.FAMILY_AFFILIATION in {2, 4, 5}
        if record.RecordType == "T5":
            skip_partial = record.FAMILY_AFFILIATION in {3, 4, 5}
        return skip_partial

    def add_case_member(self, record, schema, line, line_number):
        """Add case member and generate errors if needed.

        @param record: a Django model representing a datafile record
        @param schema: the schema from which the record was created
        @param line: the raw string line representing the record
        @param line_number: the line number the record was generated from in the datafile
        @return: the number of duplicate errors
        """
        # TODO: Need to add support for T6 and T7 detection.

        if self.current_line_number is None or self.current_line_number != line_number:
            self.current_line_number = line_number
            self.record_ids.setdefault(schema.document, []).append(record.id)
            is_exact_dup = False
            err_msg = None
            has_precedence = False
            is_new_max_precedence = False

            line_hash = hash(line)
            if line_hash in self.record_hashes:
                has_precedence, is_new_max_precedence = self.error_precedence.has_precedence(ErrorLevel.DUPLICATE)
                existing_record_line_number = self.record_hashes[line_hash]
                err_msg = (f"Duplicate record detected with record type "
                           f"{record.RecordType} at line {line_number}. Record is a duplicate of the record at "
                           f"line number {existing_record_line_number}.")
                is_exact_dup = True

            skip_partial = self.__skip_partial(record)
            partial_hash = self.__get_partial_hash(record)
            if not skip_partial and not is_exact_dup and partial_hash in self.partial_hashes:
                has_precedence, is_new_max_precedence = self.error_precedence.has_precedence(
                    ErrorLevel.PARTIAL_DUPLICATE)
                existing_record_line_number = self.partial_hashes[partial_hash]
                err_msg = (f"Partial duplicate record detected with record type "
                           f"{record.RecordType} at line {line_number}. Record is a partial duplicate of the "
                           f"record at line number {existing_record_line_number}.")

            self.__generate_error(err_msg, record, schema, has_precedence, is_new_max_precedence)
            if line_hash not in self.record_hashes:
                self.record_hashes[line_hash] = line_number
            if partial_hash is not None and partial_hash not in self.partial_hashes:
                self.partial_hashes[partial_hash] = line_number

        return self.num_errors


class RecordDuplicateManager:
    """Manages all CaseHashtainers and their errors."""

    def __init__(self, generate_error):
        self.hashtainers = dict()
        self.generate_error = generate_error
        self.generated_errors = dict()

    def add_record(self, record, hash_val, schema, line, line_number):
        """Add record to existing CaseHashtainer or create new one and return whether the record's case has errors.

        @param record: a Django model representing a datafile record
        @param hash_val: a hash value generated from fields in the record based on the records section
        @param schema: the schema from which the record was created
        @param line: the raw string line representing the record
        @param line_number: the line number the record was generated from in the datafile
        @return: the number of duplicate errors
        """
        if hash_val not in self.hashtainers:
            hashtainer = CaseHashtainer(hash_val, self.generated_errors, self.generate_error)
            self.hashtainers[hash_val] = hashtainer
        return self.hashtainers[hash_val].add_case_member(record, schema, line, line_number)

    def get_generated_errors(self):
        """Return all errors from all CaseHashtainers."""
        generated_errors = list()
        for errors in self.generated_errors.values():
            generated_errors.extend(errors)
        return generated_errors

    def clear_errors(self):
        """Clear all generated errors."""
        # We MUST call .clear() here instead of re-assigning a new dict() because the hashtainers have a reference to
        # this dictionary. Re-assigning the dictionary means the hashtainers lose their reference.
        self.generated_errors.clear()

    def get_records_to_remove(self):
        """Return dictionary of document:[errors]."""
        records_to_remove = dict()
        for hashtainer in self.hashtainers.values():
            for document, ids in hashtainer.get_records_for_post_parse_deletion().items():
                records_to_remove.setdefault(document, []).extend(ids)

        return records_to_remove

    def update_removed(self, hash_val, was_removed):
        """Notify hashtainers whether case could or could not be removed from memory."""
        hashtainer = self.hashtainers.get(hash_val, False)
        if hashtainer:
            if was_removed:
                hashtainer.set_should_remove_from_db(False)
            else:
                hashtainer.set_should_remove_from_db(True)
