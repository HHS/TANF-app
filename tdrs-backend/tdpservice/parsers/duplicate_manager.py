from .models import ParserErrorCategoryChoices
from .schema_defs import tanf

class CaseHashtainer:
    def __init__(self, CASE_NUMBER, RPT_MONTH_YEAR, manager_error_list, generate_error):
        self.CASE_NUMBER = CASE_NUMBER
        self.RPT_MONTH_YEAR = RPT_MONTH_YEAR
        self.manager_error_list = manager_error_list
        self.generate_error = generate_error
        self.record_ids = set()
        self.record_hashes = dict()
        self.partial_hashes = dict()
    
    def __generate_error(self, err_msg):
        if err_msg is not None:
            error = self.generate_error(
                        error_category=ParserErrorCategoryChoices.CASE_CONSISTENCY,
                        schema=None, ## TODO: Do we need the right schema? Can this be None to avoid so much state?
                        record=None,
                        field=None,
                        error_message=err_msg,
                    )
            self.manager_error_list.append(error)

    def add_case_member(self, record, line, line_number):
        self.record_ids.add(record.id)
        line_hash = hash(line)
        partial_hash = None
        if record.RecordType == "T1":
            partial_hash = hash(record.RecordType + str(record.RPT_MONTH_YEAR) + record.CASE_NUMBER)
        else:
            partial_hash = hash(record.RecordType + str(record.RPT_MONTH_YEAR) + record.CASE_NUMBER + str(record.FAMILY_AFFILIATION) + record.DATE_OF_BIRTH + record.SSN)

        is_exact_dup = False
        err_msg = None
        if line_hash in self.record_hashes:
            existing_record_id, existing_record_line_number = self.record_hashes[line_hash]
            err_msg = (f"Duplicate record detected for record id {record.id} with record type {record.RecordType} at "
                               f"line {line_number}. Record is a duplicate of the record at line number "
                               f"{existing_record_line_number}, with record id {existing_record_id}")
            is_exact_dup = True

        skip_partial = False
        if  record.RecordType != "T1":
            skip_partial = record.FAMILY_AFFILIATION == 3 or record.FAMILY_AFFILIATION == 5
        if not skip_partial and not is_exact_dup and partial_hash in self.partial_hashes:
            err_msg = (f"Partial duplicate record detected for record id {record.id} with record type {record.RecordType} at "
                               f"line {line_number}. Record is a partial duplicate of the record at line number "
                               f"{self.partial_hashes[partial_hash][1]}, with record id {self.partial_hashes[partial_hash][0]}")
        
        self.__generate_error(err_msg)
        self.record_hashes[line_hash] = (record.id, line_number)
        self.partial_hashes[partial_hash] = (record.id, line_number)


class RecordDuplicateManager:

    def __init__(self, generate_error):
        self.hashtainers = dict()
        self.generate_error = generate_error
        self.generated_errors = []

    def add_record(self, record, line, line_number):
        hash_val = hash(str(record.RPT_MONTH_YEAR) + record.CASE_NUMBER)
        if hash_val not in self.hashtainers:
            hashtainer = CaseHashtainer(record.CASE_NUMBER, str(record.RPT_MONTH_YEAR), 
                                        self.generated_errors, self.generate_error)
            self.hashtainers[hash_val] = hashtainer
        self.hashtainers[hash_val].add_case_member(record, line, line_number)

    def get_generated_errors(self):
        return self.generated_errors
    
    def get_num_generated_errors(self):
        return len(self.generated_errors)
