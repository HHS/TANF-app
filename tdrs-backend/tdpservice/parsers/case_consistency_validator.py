"""Class definition for Category Four validator."""

from datetime import datetime
from .duplicate_manager import DuplicateManager
from .models import ParserErrorCategoryChoices
from .util import get_years_apart
from tdpservice.stts.models import STT
from tdpservice.parsers.schema_defs.utils import get_program_model
from tdpservice.parsers.validators.util import ValidationErrorArgs
from tdpservice.parsers.validators.category3 import format_error_context
import logging

logger = logging.getLogger(__name__)


class CaseConsistencyValidator:
    """Caches records of the same case and month to perform category four validation while actively parsing."""

    def __init__(self, header, program_type, stt_type, generate_error):
        self.header = header
        self.sorted_cases = dict()
        self.cases = list()
        self.duplicate_manager = DuplicateManager(generate_error)
        self.current_rpt_month_year = None
        self.current_case = None
        self.current_case_hash = None
        self.case_has_errors = False
        self.section = header["type"]
        self.case_is_section_one_or_two = self.section in {"A", "C"}
        self.program_type = program_type
        self.is_ssp = self.program_type == "SSP"
        self.has_validated = False
        self.generate_error = generate_error
        self.generated_errors = list()
        self.total_cases_cached = 0
        self.total_cases_validated = 0
        self.stt_type = stt_type
        self.s1s = None
        self.s2s = None

    def __get_model(self, model_str):
        """Return a model for the current program type/section given the model"s string name."""
        manager = get_program_model(self.program_type, self.section, model_str)
        return manager.schemas[0].document.Django.model

    def __get_error_context(self, field_name, schema):
        if schema is None:
            return field_name
        field = schema.get_field_by_name(field_name)
        error_args = ValidationErrorArgs(value=None,
                                         row_schema=schema,
                                         friendly_name=field.friendly_name,
                                         item_num=field.item,
                                         )
        return format_error_context(error_args)

    def __generate_and_add_error(self, schema, record, field, line_num, msg):
        """Generate a ParserError and add it to the `generated_errors` list."""
        err = self.generate_error(
            error_category=ParserErrorCategoryChoices.CASE_CONSISTENCY,
            schema=schema,
            line_number=line_num,
            record=record,
            field=field,
            error_message=msg,
        )
        self.generated_errors.append(err)

    def clear_errors(self, clear_dup=True):
        """Reset generated errors."""
        self.generated_errors = []
        if clear_dup:
            self.duplicate_manager.clear_errors()

    def get_generated_errors(self):
        """Return all errors generated for the current validated case."""
        dup_errors = self.duplicate_manager.get_generated_errors()
        self.generated_errors.extend(dup_errors)
        return self.generated_errors

    def num_generated_errors(self):
        """Return current number of generated errors for the current case."""
        return len(self.generated_errors)

    def add_record_to_structs(self, record_triplet):
        """Add record_schema_pair to structs."""
        record = record_triplet[0]
        self.sorted_cases.setdefault(type(record), []).append(record_triplet)
        self.cases.append(record_triplet)

    def clear_structs(self, seed_record_triplet=None):
        """Reset and optionally seed the structs."""
        self.sorted_cases = dict()
        self.cases = list()
        if seed_record_triplet:
            self.add_record_to_structs(seed_record_triplet)

    def update_removed(self, case_hash, should_remove, was_removed):
        """Notify duplicate manager's CaseDuplicateDetectors whether they need to mark their records for DB removal."""
        self.duplicate_manager.update_removed(case_hash, should_remove, was_removed)

    def _get_case_hash(self, record):
        # Section 3/4 records don't have a CASE_NUMBER, and they're broken into multiple records for the same line.
        # The duplicate manager saves us from dupe validating the records on teh same line, however, we use record
        # type as the "case number" here because there should only ever be one line in a section 3/4 file with a
        # record type. If we generate the same hash twice we guarentee an error and therefore need only check the
        # record type.
        if not self.case_is_section_one_or_two:
            return hash(record.RecordType)
        return hash(str(record.RPT_MONTH_YEAR) + record.CASE_NUMBER)

    def add_record(self, record, schema, line, line_number, case_has_errors):
        """Add record to cache, validate if new case is detected, and check for duplicate errors.

        @param record: a Django model representing a datafile record
        @param schema: the schema from which the record was created
        @param line: the raw string line representing the record
        @param line_number: the line number the record was generated from in the datafile
        @param case_has_errors: boolean indictating whether the record's case has any cat2 or cat3 errors
        @return: (boolean indicating existence of cat4 errors, a hash value generated from fields in the record
                 based on the records section)
        """
        num_errors = 0
        latest_case_hash = self._get_case_hash(record)
        case_hash_to_remove = latest_case_hash
        self.current_rpt_month_year = record.RPT_MONTH_YEAR
        if self.case_is_section_one_or_two:
            if latest_case_hash != self.current_case_hash and self.current_case_hash is not None:
                num_errors += self.validate()
                self.clear_structs((record, schema, line_number))
                self.case_has_errors = case_has_errors
                self.has_validated = False
                case_hash_to_remove = self.current_case_hash
            else:
                self.case_has_errors = self.case_has_errors if self.case_has_errors else case_has_errors
                self.add_record_to_structs((record, schema, line_number))
                self.has_validated = False
            self.current_case = record.CASE_NUMBER

        # Need to return the hash of what we just cat4 validated, i.e. case_hash_to_remove = self.current_case_hash. If
        # we didn't cat4 validate then we return the latest case hash, i.e. case_hash_to_remove = latest_case_hash.
        # However, we always call self.duplicate_manager.add_record with the latest case_hash.
        self.duplicate_manager.add_record(record, latest_case_hash, schema, line, line_number)
        num_errors += self.duplicate_manager.get_num_dup_errors(case_hash_to_remove)

        self.current_case_hash = latest_case_hash

        return num_errors > 0, case_hash_to_remove, latest_case_hash

    def validate(self):
        """Perform category four validation on all cached records."""
        num_errors = 0
        try:
            if self.case_is_section_one_or_two:
                self.total_cases_cached += 1
                num_errors = self.__validate()
            return num_errors
        except Exception:
            logger.exception("Uncaught exception during category four validation.")
            return num_errors
        finally:
            self.s1s = None
            self.s2s = None

    def __validate(self):
        """Private validate, lint complexity."""
        num_errors = 0
        self.total_cases_validated += 1
        self.has_validated = True
        logger.debug(f"Attempting to execute Cat4 validation for case: {self.current_case}.")

        if self.section == "A":
            num_errors += self.__validate_section1(num_errors)
        elif self.section == "C":
            num_errors += self.__validate_section2(num_errors)
        else:
            self.total_cases_validated -= 1
            logger.warn(f"Case: {self.current_case} has no errors but has either an incorrect program type: "
                        f"{self.program_type} or an incorrect section: {self.section}. No validation occurred.")
            self.has_validated = False
        return num_errors

    def __validate_section1(self, num_errors):
        """Perform TANF Section 1 category four validation on all cached records."""
        num_errors += self.__validate_s1_records_are_related()
        return num_errors

    def __validate_section2(self, num_errors):
        """Perform TANF Section 2 category four validation on all cached records."""
        num_errors += self.__validate_s2_records_are_related()
        num_errors += self.__validate_t5_atd_and_ssi()
        return num_errors

    def __has_family_affil(self, records, passed):
        """Check if a set of records (T2s or T3s) has correct family affiliation."""
        context = ""
        is_records = len(records) > 0
        if is_records and not passed:
            context = self.__get_error_context("FAMILY_AFFILIATION", records[0][1]) + "==1"
            for record, schema, line_num in records:
                family_affiliation = getattr(record, "FAMILY_AFFILIATION")
                if family_affiliation == 1:
                    return context, True, False
        return context, passed, is_records

    def __validate_family_affiliation(self,
                                      num_errors,
                                      t1_model_name, t1s,
                                      t2_model_name, t2s,
                                      t3_model_name, t3s):
        """Validate at least one record in t2s+t3s has FAMILY_AFFILIATION == 1."""
        num_errors = 0
        passed = False
        error_msg = (
                        f"Every {t1_model_name} record should have at least one corresponding "
                        f"{t2_model_name} or {t3_model_name} record with the same "
                    )

        t2_context, passed, is_t2 = self.__has_family_affil(t2s, passed)
        t3_context, passed, is_t3 = self.__has_family_affil(t3s, passed)

        final_context = ""
        if is_t2 and is_t3:
            final_context += t2_context + " or " + t3_context + "."
        elif is_t2:
            final_context += t2_context + "."
        else:
            final_context += t3_context + "."

        if not passed:
            for record, schema, line_num in t1s:
                rpt_context = f"{self.__get_error_context('RPT_MONTH_YEAR', schema)} and "
                case_context = f"{self.__get_error_context('CASE_NUMBER', schema)}, where "
                error_msg += rpt_context + case_context + final_context
                self.__generate_and_add_error(
                    schema,
                    record,
                    field="FAMILY_AFFILIATION",
                    line_num=line_num,
                    msg=error_msg
                )
                num_errors += 1

        return num_errors

    def __get_s1_triplets_and_names(self):
        if self.s1s is None:
            t1_model_name = "M1" if self.is_ssp else "T1"
            t1_model = self.__get_model(t1_model_name)
            t2_model_name = "M2" if self.is_ssp else "T2"
            t2_model = self.__get_model(t2_model_name)
            t3_model_name = "M3" if self.is_ssp else "T3"
            t3_model = self.__get_model(t3_model_name)

            t1s = self.sorted_cases.get(t1_model, [])
            t2s = self.sorted_cases.get(t2_model, [])
            t3s = self.sorted_cases.get(t3_model, [])
            self.s1s = (t1s, t1_model_name, t2s, t2_model_name, t3s, t3_model_name)
        return self.s1s

    def __get_s2_triplets_and_names(self):
        if self.s2s is None:
            t4_model_name = "M4" if self.is_ssp else "T4"
            t4_model = self.__get_model(t4_model_name)
            t5_model_name = "M5" if self.is_ssp else "T5"
            t5_model = self.__get_model(t5_model_name)

            t4s = self.sorted_cases.get(t4_model, [])
            t5s = self.sorted_cases.get(t5_model, [])
            self.s2s = (t4s, t4_model_name, t5s, t5_model_name)
        return self.s2s

    def __validate_s1_records_are_related(self):
        """
        Validate section 1 records are related.

        Every T1 record should have at least one corresponding T2 or T3
        record with the same RPT_MONTH_YEAR and CASE_NUMBER.
        """
        num_errors = 0
        t1s, t1_model_name, t2s, t2_model_name, t3s, t3_model_name = self.__get_s1_triplets_and_names()

        if len(t1s) > 0:
            if len(t2s) == 0 and len(t3s) == 0:
                for record, schema, line_num in t1s:
                    self.__generate_and_add_error(
                        schema,
                        record,
                        field="RPT_MONTH_YEAR",
                        line_num=line_num,
                        msg=(
                            f"Every {t1_model_name} record should have at least one "
                            f"corresponding {t2_model_name} or {t3_model_name} record "
                            f"with the same {self.__get_error_context('RPT_MONTH_YEAR', schema)} and "
                            f"{self.__get_error_context('CASE_NUMBER', schema)}."
                        )
                    )
                    num_errors += 1

            else:
                # loop through all t2s and t3s
                # to find record where FAMILY_AFFILIATION == 1
                num_errors += self.__validate_family_affiliation(num_errors,
                                                                 t1_model_name, t1s,
                                                                 t2_model_name, t2s,
                                                                 t3_model_name, t3s)

                # the successful route
                # pass
        else:
            for record, schema, line_num in t2s:
                self.__generate_and_add_error(
                    schema,
                    record,
                    field="RPT_MONTH_YEAR",
                    line_num=line_num,
                    msg=(
                        f"Every {t2_model_name} record should have at least one corresponding "
                        f"{t1_model_name} record with the same {self.__get_error_context('RPT_MONTH_YEAR', schema)} "
                        f"and {self.__get_error_context('CASE_NUMBER', schema)}."
                    )
                )
                num_errors += 1

            for record, schema, line_num in t3s:
                self.__generate_and_add_error(
                    schema,
                    record,
                    field="RPT_MONTH_YEAR",
                    line_num=line_num,
                    msg=(
                        f"Every {t3_model_name} record should have at least one corresponding "
                        f"{t1_model_name} record with the same {self.__get_error_context('RPT_MONTH_YEAR', schema)} "
                        f"and {self.__get_error_context('CASE_NUMBER', schema)}."
                    )
                )
                num_errors += 1

        return num_errors

    def __validate_case_closure_employment(self, t4, t5s, error_msg):
        """
        Validate case closure.

        If case closure reason = 01:employment, then at least one person on
        the case must have employment status = 1:Yes in the same month.
        """
        num_errors = 0
        t4_record, t4_schema, line_num = t4

        passed = False
        for record, schema, line_num in t5s:
            employment_status = getattr(record, "EMPLOYMENT_STATUS")

            if employment_status == 1:
                passed = True
                break

        if not passed:
            self.__generate_and_add_error(
                t4_schema,
                t4_record,
                "EMPLOYMENT_STATUS",
                line_num,
                error_msg
            )
            num_errors += 1

        return num_errors

    def __validate_case_closure_ftl(self, t4, t5s, error_msg):
        """
        Validate case closure.

        If closure reason = FTL, then at least one person who is HoH
        or spouse of HoH on case must have FTL months >=60.
        """
        num_errors = 0
        t4_record, t4_schema, line_num = t4

        passed = False
        for record, schema, line_num in t5s:
            relationship_hoh = getattr(record, "RELATIONSHIP_HOH")
            ftl_months = getattr(record, "COUNTABLE_MONTH_FED_TIME")

            if (relationship_hoh == "01" or relationship_hoh == "02") and int(ftl_months) >= 60:
                passed = True
                break

        if not passed:
            self.__generate_and_add_error(
                t4_schema,
                t4_record,
                "COUNTABLE_MONTH_FED_TIME",
                line_num,
                error_msg
            )
            num_errors += 1

        return num_errors

    def __validate_s2_records_are_related(self):
        """
        Validate section 2 records are related.

        Every T4 record should have at least one corresponding T5 record
        with the same RPT_MONTH_YEAR and CASE_NUMBER.
        """
        num_errors = 0
        t4s, t4_model_name, t5s, t5_model_name = self.__get_s2_triplets_and_names()

        if len(t4s) > 0:
            if len(t4s) == 1:
                t4 = t4s[0]
                t4_record, t4_schema, line_num = t4
                closure_reason = getattr(t4_record, "CLOSURE_REASON")

                if closure_reason == "01":
                    num_errors += self.__validate_case_closure_employment(t4, t5s, (
                        f"At least one person on the case must have "
                        f"{self.__get_error_context('EMPLOYMENT_STATUS', t5s[0][1] if t5s else None)} = 1:Yes in the "
                        f"same {self.__get_error_context('RPT_MONTH_YEAR', t4_schema)} since "
                        f"{self.__get_error_context('CLOSURE_REASON', t4_schema)} = 1:Employment/excess earnings."
                    ))
                elif closure_reason == "03" and not self.is_ssp:
                    num_errors += self.__validate_case_closure_ftl(
                        t4,
                        t5s,
                        ("At least one person who is head-of-household or "
                         "spouse of head-of-household on case must have "
                         f"{self.__get_error_context('COUNTABLE_MONTH_FED_TIME', t5s[0][1] if t5s else None)} >= 60 "
                         f"since {self.__get_error_context('CLOSURE_REASON', t4_schema)} = 03: "
                         "federal 5 year time limit.")
                         )
            if len(t5s) == 0:
                for record, schema, line_num in t4s:
                    self.__generate_and_add_error(
                        schema,
                        record,
                        field="RPT_MONTH_YEAR",
                        line_num=line_num,
                        msg=(
                            f"Every {t4_model_name} record should have at least one corresponding "
                            f"{t5_model_name} record with the same {self.__get_error_context('RPT_MONTH_YEAR', schema)}"
                            f" and {self.__get_error_context('CASE_NUMBER', schema)}."
                        )
                    )
                    num_errors += 1
            else:
                # success
                pass
        else:
            for record, schema, line_num in t5s:
                self.__generate_and_add_error(
                    schema,
                    record,
                    field="RPT_MONTH_YEAR",
                    line_num=line_num,
                    msg=(
                        f"Every {t5_model_name} record should have at least one corresponding "
                        f"{t4_model_name} record with the same {self.__get_error_context('RPT_MONTH_YEAR', schema)} "
                        f"and {self.__get_error_context('CASE_NUMBER', schema)}."
                    )
                )
                num_errors += 1
        return num_errors

    def __validate_t5_atd_and_ssi(self):
        num_errors = 0
        t4s, t4_model_name, t5s, t5_model_name = self.__get_s2_triplets_and_names()

        is_state = self.stt_type == STT.EntityType.STATE
        is_territory = self.stt_type == STT.EntityType.TERRITORY

        for record, schema, line_num in t5s:
            rec_atd = getattr(record, 'REC_AID_TOTALLY_DISABLED')
            rec_ssi = getattr(record, 'REC_SSI')
            family_affiliation = getattr(record, 'FAMILY_AFFILIATION')
            dob = getattr(record, 'DATE_OF_BIRTH')

            rpt_month_year_dd = f'{self.current_rpt_month_year}01'
            rpt_date = datetime.strptime(rpt_month_year_dd, '%Y%m%d')
            dob_date = datetime.strptime(dob, '%Y%m%d')
            is_adult = get_years_apart(rpt_date, dob_date) >= 19

            if is_territory and is_adult and rec_atd not in {1, 2}:
                self.__generate_and_add_error(
                    schema,
                    record,
                    field="REC_AID_TOTALLY_DISABLED",
                    line_num=line_num,
                    msg=(
                        f"{t5_model_name} Adults in territories must have a valid "
                        f"value for {self.__get_error_context('REC_AID_TOTALLY_DISABLED', schema)}."
                    )
                )
                num_errors += 1
            elif is_state and rec_atd == 1:
                self.__generate_and_add_error(
                    schema,
                    record,
                    field="REC_AID_TOTALLY_DISABLED",
                    line_num=line_num,
                    msg=(
                        f"{t5_model_name} People in states should not have a value "
                        f"of 1 for {self.__get_error_context('REC_AID_TOTALLY_DISABLED', schema)}."
                    )
                )
                num_errors += 1

            if is_territory and rec_ssi != 2:
                self.__generate_and_add_error(
                    schema,
                    record,
                    field="REC_SSI",
                    line_num=line_num,
                    msg=(
                        f"{t5_model_name} People in territories must have value = 2:No for "
                        f"{self.__get_error_context('REC_SSI', schema)}."
                    )
                )
                num_errors += 1
            elif is_state and family_affiliation == 1 and rec_ssi not in {1, 2}:
                self.__generate_and_add_error(
                    schema,
                    record,
                    field="REC_SSI",
                    line_num=line_num,
                    msg=(
                        f"{t5_model_name} People in states must have a valid value for "
                        f"{self.__get_error_context('REC_SSI', schema)}."
                    )
                )
                num_errors += 1

        return num_errors
