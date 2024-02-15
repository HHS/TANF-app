"""Class definition for Category Four validator."""

from .models import ParserErrorCategoryChoices
from .util import get_rpt_month_year_list
import logging

logger = logging.getLogger(__name__)

class CaseConsistencyValidator:
    """Caches records of the same case to perform category four validation while actively parsing."""

    def __init__(self, header, generate_error):
        self.header = header
        self.record_schema_pairs = []
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

    def clear_errors(self):
        """Reset generated errors."""
        self.generated_errors = []

    def get_generated_errors(self):
        """Return all errors generated for the current case."""
        return self.generated_errors

    def add_record(self, record, schema, case_has_errors):
        """Add record to cache and validate if new case is detected."""
        if self.case_is_section_one_or_two:
            if record.CASE_NUMBER != self.current_case and self.current_case is not None:
                self.validate()
                self.record_schema_pairs = [(record, schema)]
                self.case_has_errors = case_has_errors
            else:
                self.case_has_errors = self.case_has_errors if self.case_has_errors else case_has_errors
                self.record_schema_pairs.append((record, schema))
                self.has_validated = False
            self.current_case = record.CASE_NUMBER

    def validate(self):
        """Perform category four validation on all cached records."""
        num_errors = 0
        if self.case_is_section_one_or_two:
            self.total_cases_cached += 1
            if not self.case_has_errors:
                self.total_cases_validated += 1
                self.has_validated = True
                logger.debug(f"Attempting to execute Cat4 validation for case: {self.current_case}.")
                if self.program_type == "TAN" and self.section == "A" and "state_fips" in self.header:
                    num_errors += self.__validate_tanf_s1_case(num_errors)
                elif self.program_type == "TAN" and self.section == "C" and "state_fips" in self.header:
                    num_errors += self.__validate_tanf_s2_case(num_errors)
                elif self.program_type == "TAN" and self.section == "A" and "tribe_code" in self.header:
                    num_errors += self.__validate_tribal_tanf_s1_case(num_errors)
                elif self.program_type == "TAN" and self.section == "C" and "tribe_code" in self.header:
                    num_errors += self.__validate_tribal_tanf_s2_case(num_errors)
                elif self.program_type == "SSP" and self.section == "A":
                    num_errors += self.__validate_ssp_s1_case(num_errors)
                elif self.program_type == "SSP" and self.section == "C":
                    num_errors += self.__validate_ssp_s2_case(num_errors)
                else:
                    self.total_cases_validated -= 1
                    logger.warn(f"Case: {self.current_case} has no errors but has either an incorrect program type: "
                                f"{self.program_type} or an incorrect section: {self.section}. No validation occurred.")
                    self.has_validated = False
            else:
                logger.debug(f"Case: {self.current_case} has errors associated with it's records. "
                             "Skipping Cat4 validation")
        return num_errors

    def __validate_tanf_s1_case(self, num_errors):
        """Perform TANF Section 1 category four validation on all cached records."""
        num_errors += self.__validate_tanf_s1_header_with_records()
        return num_errors

    def __validate_tanf_s2_case(self, num_errors):
        """Perform TANF Section 2 category four validation on all cached records."""
        return 0

    def __validate_tribal_tanf_s1_case(self, num_errors):
        """Perform Tribal TANF Section 1 category four validation on all cached records."""
        return 0

    def __validate_tribal_tanf_s2_case(self, num_errors):
        """Perform Tribal TANF Section 2 category four validation on all cached records."""
        return 0

    def __validate_ssp_s1_case(self, num_errors):
        """Perform SSP Section 1 category four validation on all cached records."""
        return 0

    def __validate_ssp_s2_case(self, num_errors):
        """Perform SSP Section 2 category four validation on all cached records."""
        return 0

    def __validate_tanf_s1_header_with_records(self):
        """Header YEAR + header QUARTER must be consistent with RPT_MONTH_YEAR for all T1, T2, and T3 records."""
        year = self.header["year"]
        quarter = self.header["quarter"]
        header_rpt_month_year_list = get_rpt_month_year_list(year, quarter)
        num_errors = 0
        for record, schema in self.record_schema_pairs:
            if record.RPT_MONTH_YEAR not in header_rpt_month_year_list:
                num_errors += 1
                err_msg = (f"Failed to validate record with CASE_NUMBER={record.CASE_NUMBER} and "
                           f"RPT_MONTH_YEAR={record.RPT_MONTH_YEAR} against header. If YEAR={year} and "
                           f"QUARTER={quarter}, then RPT_MONTH_YEAR must be in {header_rpt_month_year_list}.")
                self.generated_errors.append(
                    self.generate_error(schema=schema,
                                        error_category=ParserErrorCategoryChoices.CASE_CONSISTENCY,
                                        error_message=err_msg,
                                        record=record,
                                        field="RPT_MONTH_YEAR"
                                        )
                                    )
        return num_errors
