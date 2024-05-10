"""Class definition for Category Four validator."""

from .models import ParserErrorCategoryChoices
from tdpservice.parsers.schema_defs.utils import get_program_model
import logging

logger = logging.getLogger(__name__)


class SortedRecordSchemaPairs:
    """Maintains list of case record-schema-pairs and a copy object sorted by rpt_month_year and model_type."""

    def __init__(self):
        self.cases = []
        self.sorted_cases = {}

    def clear(self, seed_record_schema_pair=None):
        """Reset both the list and sorted object. Optionally add a seed record for the next run."""
        self.cases = []
        self.sorted_cases = {}

        if seed_record_schema_pair:
            self.add_record(seed_record_schema_pair)

    def add_record(self, record_schema_pair):
        """Add a record_schema_pair to both the cases list and sorted_cases object."""
        self.__add_record_to_sorted_object(record_schema_pair)
        self.cases.append(record_schema_pair)

    def __add_record_to_sorted_object(self, record_schema_pair):
        """Add a record_schema_pair to the sorted_cases object."""
        record, schema = record_schema_pair
        rpt_month_year = getattr(record, 'RPT_MONTH_YEAR')

        reporting_year_cases = self.sorted_cases.get(rpt_month_year, {})
        records = reporting_year_cases.get(type(record), [])
        records.append(record_schema_pair)

        reporting_year_cases[type(record)] = records
        self.sorted_cases[rpt_month_year] = reporting_year_cases


class CaseConsistencyValidator:
    """Caches records of the same case and month to perform category four validation while actively parsing."""

    def __init__(self, header, generate_error):
        self.header = header
        self.record_schema_pairs = SortedRecordSchemaPairs()
        self.current_case = None
        self.case_has_errors = False
        self.section = header["type"]
        self.case_is_section_one_or_two = self.section in {'A', 'C'}
        self.program_type = header["program_type"]
        self.has_validated = False
        self.generate_error = generate_error
        self.generated_errors = []
        self.total_cases_cached = 0
        self.total_cases_validated = 0

    def __get_model(self, model_str):
        """Return a model for the current program type/section given the model's string name."""
        manager = get_program_model(self.program_type, self.section, model_str)
        return manager.schemas[0].document.Django.model

    def __generate_and_add_error(self, schema, record, field, msg):
        """Generate a ParserError and add it to the `generated_errors` list."""
        err = self.generate_error(
            error_category=ParserErrorCategoryChoices.CASE_CONSISTENCY,
            schema=schema,
            record=record,
            field=field,
            error_message=msg,
        )
        self.generated_errors.append(err)

    def clear_errors(self):
        """Reset generated errors."""
        self.generated_errors = []

    def get_generated_errors(self):
        """Return all errors generated for the current validated case."""
        return self.generated_errors

    def num_generated_errors(self):
        """Return current number of generated errors."""
        return len(self.generated_errors)

    def add_record(self, record, schema, case_has_errors):
        """Add record to cache and validate if new case is detected."""
        if self.case_is_section_one_or_two:
            if record.CASE_NUMBER != self.current_case and self.current_case is not None:
                self.validate()
                self.record_schema_pairs.clear((record, schema))
                self.case_has_errors = case_has_errors
                self.has_validated = False
            else:
                self.case_has_errors = self.case_has_errors if self.case_has_errors else case_has_errors
                self.record_schema_pairs.add_record((record, schema))
                self.has_validated = False
            self.current_case = record.CASE_NUMBER

    def validate(self):
        """Perform category four validation on all cached records."""
        num_errors = 0
        try:
            if self.case_is_section_one_or_two:
                self.total_cases_cached += 1
                num_errors = self.__validate()
            return num_errors
        except Exception as e:
            logger.error(f"Uncaught exception during category four validation: {e}")
            return num_errors

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
        return num_errors

    def __validate_family_affiliation(self, num_errors, t1s, t2s, t3s, error_msg):
        """Validate at least one record in t2s+t3s has FAMILY_AFFILIATION == 1."""
        passed = False
        for record, schema in t2s + t3s:
            family_affiliation = getattr(record, 'FAMILY_AFFILIATION')
            if family_affiliation == 1:
                passed = True
                break

        if not passed:
            for record, schema in t1s:
                self.__generate_and_add_error(
                    schema,
                    record,
                    field='FAMILY_AFFILIATION',
                    msg=error_msg
                )
                num_errors += 1

        return num_errors

    def __validate_s1_records_are_related(self):
        """
        Validate section 1 records are related.

        Every T1 record should have at least one corresponding T2 or T3
        record with the same RPT_MONTH_YEAR and CASE_NUMBER.
        """
        num_errors = 0
        is_ssp = self.program_type == 'SSP'

        t1_model_name = 'M1' if is_ssp else 'T1'
        t1_model = self.__get_model(t1_model_name)
        t2_model_name = 'M2' if is_ssp else 'T2'
        t2_model = self.__get_model(t2_model_name)
        t3_model_name = 'M3' if is_ssp else 'T3'
        t3_model = self.__get_model(t3_model_name)

        cases = self.record_schema_pairs.sorted_cases

        for reporting_year_cases in cases.values():
            t1s = reporting_year_cases.get(t1_model, [])
            t2s = reporting_year_cases.get(t2_model, [])
            t3s = reporting_year_cases.get(t3_model, [])

            if len(t1s) > 0:
                if len(t2s) == 0 and len(t3s) == 0:
                    logger.debug(f"t1 has no t2s or t3s")

                    for record, schema in t1s:
                        self.__generate_and_add_error(
                            schema,
                            record,
                            field='RPT_MONTH_YEAR',
                            msg=(
                                f'Every {t1_model_name} record should have at least one '
                                f'corresponding {t2_model_name} or {t3_model_name} record '
                                f'with the same RPT_MONTH_YEAR and CASE_NUMBER.'
                            )
                        )
                        num_errors += 1

                else:
                    # loop through all t2s and t3s
                    # to find record where FAMILY_AFFILIATION == 1
                    num_errors += self.__validate_family_affiliation(num_errors, t1s, t2s, t3s, (
                            f'Every {t1_model_name} record should have at least one corresponding '
                            f'{t2_model_name} or {t3_model_name} record with the same RPT_MONTH_YEAR and '
                            f'CASE_NUMBER, where FAMILY_AFFILIATION==1'
                        ))

                    # the successful route
                    # pass
            else:
                for record, schema in t2s:
                    logger.debug(f"t2 has no t1")
                    self.__generate_and_add_error(
                        schema,
                        record,
                        field='RPT_MONTH_YEAR',
                        msg=(
                            f'Every {t2_model_name} record should have at least one corresponding '
                            f'{t1_model_name} record with the same RPT_MONTH_YEAR and CASE_NUMBER.'
                        )
                    )
                    num_errors += 1

                for record, schema in t3s:
                    logger.debug(f"t3 has no t1")
                    self.__generate_and_add_error(
                        schema,
                        record,
                        field='RPT_MONTH_YEAR',
                        msg=(
                            f'Every {t3_model_name} record should have at least one corresponding '
                            f'{t1_model_name} record with the same RPT_MONTH_YEAR and CASE_NUMBER.'
                        )
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
        is_ssp = self.program_type == 'SSP'

        t4_model_name = 'M4' if is_ssp else 'T4'
        t4_model = self.__get_model(t4_model_name)
        t5_model_name = 'M5' if is_ssp else 'T5'
        t5_model = self.__get_model(t5_model_name)

        cases = self.record_schema_pairs.sorted_cases

        for reporting_year_cases in cases.values():
            t4s = reporting_year_cases.get(t4_model, [])
            t5s = reporting_year_cases.get(t5_model, [])

            if len(t4s) > 0:
                if len(t5s) == 0:
                    for record, schema in t4s:
                        self.__generate_and_add_error(
                            schema,
                            record,
                            field='RPT_MONTH_YEAR',
                            msg=(
                                f'Every {t4_model_name} record should have at least one corresponding '
                                f'{t5_model_name} record with the same RPT_MONTH_YEAR and CASE_NUMBER.'
                            )
                        )
                        num_errors += 1
                else:
                    # success
                    pass
            else:
                for record, schema in t5s:
                    self.__generate_and_add_error(
                        schema,
                        record,
                        field='RPT_MONTH_YEAR',
                        msg=(
                            f'Every {t5_model_name} record should have at least one corresponding '
                            f'{t4_model_name} record with the same RPT_MONTH_YEAR and CASE_NUMBER.'
                        )
                    )
                    num_errors += 1

        return num_errors
