"""Class definition for Category Four validator."""

from datetime import datetime
from .models import ParserErrorCategoryChoices
from .util import get_rpt_month_year_list
from tdpservice.stts.models import STT
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
    """Caches records of the same case to perform category four validation while actively parsing."""

    def __init__(self, header, stt_type, generate_error):
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
        self.stt_type = stt_type

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
        if self.has_validated:
            return self.generated_errors
        return []

    def add_record(self, record, schema, case_has_errors):
        """Add record to cache and validate if new case is detected."""
        if self.case_is_section_one_or_two:
            if record.CASE_NUMBER != self.current_case and self.current_case is not None:
                self.validate()
                self.record_schema_pairs.clear((record, schema))
                self.case_has_errors = case_has_errors
            else:
                self.case_has_errors = self.case_has_errors if self.case_has_errors else case_has_errors
                self.record_schema_pairs.add_record((record, schema))
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

                if self.section == "A":
                    num_errors += self.__validate_section1(num_errors)
                elif self.section == "C":
                    num_errors += self.__validate_section2(num_errors)
                else:
                    self.total_cases_validated -= 1
                    logger.warn(f"Case: {self.current_case} has no errors but has either an incorrect program type: "
                                f"{self.program_type} or an incorrect section: {self.section}. No validation occurred.")
                    self.has_validated = False
            else:
                logger.debug(f"Case: {self.current_case} has errors associated with it's records. "
                             "Skipping Cat4 validation")
        return num_errors

    def __validate_section1(self, num_errors):
        """Perform TANF Section 1 category four validation on all cached records."""
        num_errors += self.__validate_header_with_records()
        num_errors += self.__validate_s1_records_are_related()
        return num_errors

    def __validate_section2(self, num_errors):
        """Perform TANF Section 2 category four validation on all cached records."""
        num_errors += self.__validate_header_with_records()
        num_errors += self.__validate_s2_records_are_related()
        num_errors += self.__validate_t5_aabd_and_ssi()
        return num_errors

    def __validate_header_with_records(self):
        """Header YEAR + header QUARTER must be consistent with RPT_MONTH_YEAR for all T1, T2, and T3 records."""
        year = self.header["year"]
        quarter = self.header["quarter"]
        header_rpt_month_year_list = get_rpt_month_year_list(year, quarter)
        num_errors = 0
        for record, schema in self.record_schema_pairs.cases:
            if record.RPT_MONTH_YEAR not in header_rpt_month_year_list:
                num_errors += 1
                err_msg = (f"Failed to validate record with CASE_NUMBER={record.CASE_NUMBER} and "
                           f"RPT_MONTH_YEAR={record.RPT_MONTH_YEAR} against header. If YEAR={year} and "
                           f"QUARTER={quarter}, then RPT_MONTH_YEAR must be in {header_rpt_month_year_list}.")
                self.__generate_and_add_error(
                    schema,
                    record,
                    field='RPT_MONTH_YEAR',
                    msg=err_msg
                )

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

        logger.debug('validating records are related')
        logger.debug(f'program type: {self.program_type}')
        logger.debug(f'section: {self.section}')
        logger.debug(f'is_ssp: {is_ssp}')
        logger.debug(f'models - T1: {t1_model}; T2: {t2_model}; T3: {t3_model}')

        cases = self.record_schema_pairs.sorted_cases
        logger.debug(f'cases obj: {cases}')

        for rpt_month_year, reporting_year_cases in cases.items():
            t1s = reporting_year_cases.get(t1_model, [])
            t2s = reporting_year_cases.get(t2_model, [])
            t3s = reporting_year_cases.get(t3_model, [])

            logger.debug(f't1s: {t1s}')
            logger.debug(f't2s: {t2s}')
            logger.debug(f't3s: {t3s}')

            if len(t1s) > 0:
                logger.debug('t1s')
                if len(t2s) == 0 and len(t3s) == 0:
                    logger.debug('no t2s or t3s')
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
                    logger.debug('t2s/t3s')
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
                logger.debug('no t1s')
                for record, schema in t2s:
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

        # logger.debug('validating records are related')
        # logger.debug(f'program type: {self.program_type}')
        # logger.debug(f'section: {self.section}')
        # logger.debug(f'is_ssp: {is_ssp}')
        # logger.debug(f'models - T4: {t4_model}; T5: {t5_model};')

        cases = self.record_schema_pairs.sorted_cases
        # logger.debug(f'cases obj: {cases}')

        for rpt_month_year, reporting_year_cases in cases.items():
            t4s = reporting_year_cases.get(t4_model, [])
            t5s = reporting_year_cases.get(t5_model, [])

            # logger.debug(f't4s: {t4s}')
            # logger.debug(f't5s: {t5s}')

            if len(t4s) > 0:
                if len(t5s) == 0:
                    logger.debug('no t5s')
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
                logger.debug('no t4s')
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

    def __validate_t5_aabd_and_ssi(self):
        print('validate t5')
        num_errors = 0
        is_ssp = self.program_type == 'SSP'

        t5_model_name = 'M5' if is_ssp else 'T5'
        t5_model = self.__get_model(t5_model_name)

        is_state = self.stt_type == STT.EntityType.STATE
        is_territory = self.stt_type == STT.EntityType.TERRITORY

        for rpt_month_year, reporting_year_cases in self.record_schema_pairs.sorted_cases.items():
            t5s = reporting_year_cases.get(t5_model, [])

            for record, schema in t5s:
                rec_aabd = getattr(record, 'REC_AID_TOTALLY_DISABLED')
                rec_ssi = getattr(record, 'REC_SSI')
                family_affiliation = getattr(record, 'FAMILY_AFFILIATION')
                dob = getattr(record, 'DATE_OF_BIRTH')

                rpt_month_year_dd = f'{rpt_month_year}01'
                rpt_date = datetime.strptime(rpt_month_year_dd, '%Y%m%d')
                dob_date = datetime.strptime(dob, '%Y%m%d')
                delta = rpt_date - dob_date
                age = delta.days/365.25
                is_adult = age >= 18

                if is_territory and is_adult and rec_aabd != 1:
                    self.__generate_and_add_error(
                        schema,
                        record,
                        field='REC_AID_TOTALLY_DISABLED',
                        msg=(
                            f'{t5_model_name} Adults in territories must have a valid value for 19C.'
                        )
                    )
                    num_errors += 1
                elif is_state and rec_aabd != 2:
                    self.__generate_and_add_error(
                        schema,
                        record,
                        field='REC_AID_TOTALLY_DISABLED',
                        msg=(
                            f'{t5_model_name} People in states shouldn\'t have a value of 1.'
                        )
                    )
                    num_errors += 1

                if is_territory and rec_ssi != 2:
                    self.__generate_and_add_error(
                        schema,
                        record,
                        field='REC_SSI',
                        msg=(
                            f'{t5_model_name} People in territories must have a valid value for 19E.'
                        )
                    )
                    num_errors += 1
                elif is_state and family_affiliation == 1 and rec_ssi != 1:
                    self.__generate_and_add_error(
                        schema,
                        record,
                        field='REC_SSI',
                        msg=(
                            f'{t5_model_name} People in states must have a valid value.'
                        )
                    )
                    num_errors += 1

        return num_errors
