"""Class definition for record duplicate class and helper classes."""
from .models import ParserErrorCategoryChoices

class ErrorPrecedence:
    """Data structure to manage error precedence."""

    def __init__(self):
        self.max_precedence = None

    def has_precedence(self, error_level):
        """Return tuple of bools: (has_precidence, is_new_max_precedence)."""
        if self.max_precedence is None:
            self.max_precedence = error_level
            return (True, True)
        elif self.max_precedence > error_level:
            self.max_precedence = error_level
            return (True, True)
        elif self.max_precedence == error_level:
            return (True, False)
        else:
            return (False, False)


class CaseHashtainer:
    """Container class to manage hashed values for records of the same CASE_NUMBER and RPT_MONTH_YEAR."""

    def __init__(self, my_hash, CASE_NUMBER, RPT_MONTH_YEAR, manager_error_dict, generate_error):
        self.my_hash = my_hash
        self.CASE_NUMBER = CASE_NUMBER
        self.RPT_MONTH_YEAR = RPT_MONTH_YEAR
        self.manager_error_dict = manager_error_dict
        self.generate_error = generate_error
        self.record_ids = dict()
        self.record_hashes = dict()
        self.partial_hashes = dict()
        self.error_precedence = ErrorPrecedence()
        self.has_duplicate_errors = False

    def get_records_to_delete(self):
        """Return record ids if case has duplicate errors."""
        if self.has_duplicate_errors:
            return self.record_ids
        return dict()

    def __generate_error(self, err_msg, is_new_max_precedence):
        """Add an error to the managers error dictionary."""
        if err_msg is not None:
            error = self.generate_error(
                        error_category=ParserErrorCategoryChoices.CASE_CONSISTENCY,
                        schema=None,  # TODO: Do we need the right schema? Can this be None to avoid so much state?
                        record=None,
                        field=None,
                        error_message=err_msg,
                    )
            self.has_duplicate_errors = True
            if is_new_max_precedence:
                self.manager_error_dict[self.my_hash] = [error]
            else:
                self.manager_error_dict[self.my_hash].append(error)

    def add_case_member(self, record, schema, line, line_number):
        """Add case member and generate errors if needed."""
        self.record_ids.setdefault(schema.document.Django.model, []).append(record.id)
        line_hash = hash(line)
        partial_hash = None
        error_level = record.RecordType[1]
        if record.RecordType == "T1":
            partial_hash = hash(record.RecordType + str(record.RPT_MONTH_YEAR) + record.CASE_NUMBER)
        else:
            partial_hash = hash(record.RecordType + str(record.RPT_MONTH_YEAR) + record.CASE_NUMBER +
                                str(record.FAMILY_AFFILIATION) + record.DATE_OF_BIRTH + record.SSN)

        is_exact_dup = False
        err_msg = None
        has_precedence = False
        is_new_max_precedence = False

        if line_hash in self.record_hashes:
            has_precedence, is_new_max_precedence = self.error_precedence.has_precedence(error_level)
            existing_record_id, existing_record_line_number = self.record_hashes[line_hash]
            err_msg = (f"Duplicate record detected for record id {record.id} with record type {record.RecordType} at "
                       f"line {line_number}. Record is a duplicate of the record at line number "
                       f"{existing_record_line_number}, with record id {existing_record_id}")
            is_exact_dup = True

        skip_partial = False
        if record.RecordType != "T1":
            skip_partial = record.FAMILY_AFFILIATION == 3 or record.FAMILY_AFFILIATION == 5
        if not skip_partial and not is_exact_dup and partial_hash in self.partial_hashes:
            has_precedence, is_new_max_precedence = self.error_precedence.has_precedence(error_level)
            err_msg = (f"Partial duplicate record detected for record id {record.id} with record type "
                       f"{record.RecordType} at line {line_number}. Record is a partial duplicate of the "
                       f"record at line number {self.partial_hashes[partial_hash][1]}, with record id "
                       f"{self.partial_hashes[partial_hash][0]}")

        if not has_precedence:
            err_msg = None

        self.__generate_error(err_msg, is_new_max_precedence)
        if line_hash not in self.record_hashes:
            self.record_hashes[line_hash] = (record.id, line_number)
        if partial_hash not in self.partial_hashes:
            self.partial_hashes[partial_hash] = (record.id, line_number)


class RecordDuplicateManager:
    """Manages all CaseHashtainers and their errors."""

    def __init__(self, generate_error):
        self.hashtainers = dict()
        self.generate_error = generate_error
        self.generated_errors = dict()

    def add_record(self, record, schema, line, line_number):
        """Add record to existing CaseHashtainer or create new one and return whether the record's case has errors."""
        hash_val = hash(str(record.RPT_MONTH_YEAR) + record.CASE_NUMBER)
        if hash_val not in self.hashtainers:
            hashtainer = CaseHashtainer(hash_val, record.CASE_NUMBER, str(record.RPT_MONTH_YEAR),
                                        self.generated_errors, self.generate_error)
            self.hashtainers[hash_val] = hashtainer
        self.hashtainers[hash_val].add_case_member(record, schema, line, line_number)

    def get_generated_errors(self):
        """Return all errors from all CaseHashtainers."""
        generated_errors = list()
        for errors in self.generated_errors.values():
            generated_errors.extend(errors)
        return generated_errors

    def get_records_to_remove(self):
        records_to_remove = dict()
        for hashtainer in self.hashtainers.values():
            for model, ids in hashtainer.get_records_to_delete().items():
                records_to_remove.setdefault(model, []).extend(ids)

        return records_to_remove
