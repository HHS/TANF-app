"""Test the CaseConsistencyValidator and SortedRecordSchemaPairs classes."""

import pytest
import logging
from tdpservice.parsers.test import factories
from .. import schema_defs, util
from ..case_consistency_validator import CaseConsistencyValidator
from tdpservice.parsers.dataclasses import RawRow
from tdpservice.parsers.models import ParserErrorCategoryChoices
from tdpservice.stts.models import STT


logger = logging.getLogger(__name__)


class TestCaseConsistencyValidator:
    """Test case consistency (cat4) validators."""

    def parse_header(self, datafile):
        """Parse datafile header into header object."""
        rawfile = datafile.file

        # parse header, trailer
        rawfile.seek(0)
        header_line = rawfile.readline().decode().strip()
        length = len(header_line)
        row = RawRow(data=header_line, raw_len=length, decoded_len=length, row_num=1, record_type="HEADER")
        return schema_defs.header.parse_and_validate(
            row,
            util.make_generate_file_precheck_parser_error(datafile, 1)
        )

    @pytest.fixture
    def tanf_s1_records(self):
        """Return group of TANF Section 1 records."""
        t1 = factories.TanfT1Factory.create()
        t2 = factories.TanfT2Factory.create()
        t3 = factories.TanfT3Factory.create()
        t3_1 = factories.TanfT3Factory.create()
        return [t1, t2, t3, t3_1]

    @pytest.fixture
    def tanf_s1_schemas(self):
        """Return group of TANF Section 1 schemas."""
        s1 = schema_defs.tanf.t1[0]
        s2 = schema_defs.tanf.t2[0]
        s3 = schema_defs.tanf.t3[0]
        return [s1, s2, s3, s3]

    @pytest.fixture
    def small_correct_file(self, stt_user, stt):
        """Fixture for small_correct_file."""
        return util.create_test_datafile("small_correct_file.txt", stt_user, stt)

    @pytest.fixture
    def small_correct_file_header(self, small_correct_file):
        """Return a valid header record."""
        header, header_is_valid, header_errors = self.parse_header(small_correct_file)

        if not header_is_valid:
            logger.error("Header is not valid: %s", header_errors)
            return None
        return header

    @pytest.mark.django_db
    def test_add_record(self, small_correct_file_header, small_correct_file, tanf_s1_records, tanf_s1_schemas):
        """Test add_record logic."""
        case_consistency_validator = CaseConsistencyValidator(
            small_correct_file_header,
            small_correct_file_header["program_type"],
            STT.EntityType.STATE,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        line_number = 1
        for record, schema in zip(tanf_s1_records, tanf_s1_schemas):
            line = str(record)
            length = len(line)
            row = RawRow(data=line, raw_len=length, decoded_len=length,
                         row_num=line_number, record_type=schema.record_type)
            case_consistency_validator.add_record(record, schema, row, line_number, True)
            line_number += 1

        assert case_consistency_validator.has_validated is False
        assert case_consistency_validator.case_has_errors is True
        assert len(case_consistency_validator.cases) == 4
        assert case_consistency_validator.total_cases_cached == 0
        assert case_consistency_validator.total_cases_validated == 0

        # Add record with different Case Number to proc validation again and start caching a new case.
        t1 = factories.TanfT1Factory.build()
        t1.CASE_NUMBER = "2"
        t1.RPT_MONTH_YEAR = 2
        line_number += 1
        line = str(t1)
        length = len(line)
        row1 = RawRow(data=line, raw_len=length, decoded_len=length,
                      row_num=line_number, record_type=t1.RecordType)
        case_consistency_validator.add_record(t1, tanf_s1_schemas[0], row1, line_number, False)
        assert case_consistency_validator.has_validated is False
        assert case_consistency_validator.case_has_errors is False
        assert len(case_consistency_validator.cases) == 1
        assert case_consistency_validator.total_cases_cached == 1
        assert case_consistency_validator.total_cases_validated == 1

        # Complete the case to proc validation and verify that it occured. Even if the next case has errors.
        t2 = factories.TanfT2Factory.build()
        t3 = factories.TanfT3Factory.build()
        t2.CASE_NUMBER = "2"
        t2.RPT_MONTH_YEAR = 2
        t3.CASE_NUMBER = "2"
        t3.RPT_MONTH_YEAR = 2
        line_number += 1
        line = str(t2)
        length = len(line)
        row2 = RawRow(data=line, raw_len=length, decoded_len=length,
                      row_num=line_number, record_type=t1.RecordType)
        case_consistency_validator.add_record(t2, tanf_s1_schemas[1], row2, line_number, False)
        line_number += 1
        line = str(t3)
        length = len(line)
        row3 = RawRow(data=line, raw_len=length, decoded_len=length,
                      row_num=line_number, record_type=t1.RecordType)
        case_consistency_validator.add_record(t3, tanf_s1_schemas[2], row3, line_number, False)
        assert case_consistency_validator.case_has_errors is False

        line_number += 1
        case_consistency_validator.add_record(tanf_s1_records[0], tanf_s1_schemas[0], row3, line_number, True)

        assert case_consistency_validator.has_validated is False
        assert case_consistency_validator.case_has_errors is True
        assert len(case_consistency_validator.cases) == 1
        assert case_consistency_validator.total_cases_cached == 2
        assert case_consistency_validator.total_cases_validated == 2

    @pytest.mark.parametrize("header,T1Stuff,T2Stuff,T3Stuff,stt_type", [
        (
            {"type": "A", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT1Factory, schema_defs.tanf.t1[0], "T1"),
            (factories.TanfT2Factory, schema_defs.tanf.t2[0], "T2"),
            (factories.TanfT3Factory, schema_defs.tanf.t3[0], "T3"),
            STT.EntityType.STATE,
        ),
        (
            {"type": "A", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT1Factory, schema_defs.tribal_tanf.t1[0], "T1"),
            (factories.TribalTanfT2Factory, schema_defs.tribal_tanf.t2[0], "T2"),
            (factories.TribalTanfT3Factory, schema_defs.tribal_tanf.t3[0], "T3"),
            STT.EntityType.TRIBE,
        ),
        (
            {"type": "A", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM1Factory, schema_defs.ssp.m1[0], "M1"),
            (factories.SSPM2Factory, schema_defs.ssp.m2[0], "M2"),
            (factories.SSPM3Factory, schema_defs.ssp.m3[0], "M3"),
            STT.EntityType.STATE,
        ),
    ])
    @pytest.mark.django_db
    def test_section1_records_are_related_validator_pass(
            self, small_correct_file, header, T1Stuff, T2Stuff, T3Stuff, stt_type):
        """Test records are related validator success case."""
        (T1Factory, t1_schema, t1_model_name) = T1Stuff
        (T2Factory, t2_schema, t2_model_name) = T2Stuff
        (T3Factory, t3_schema, t3_model_name) = T3Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            stt_type,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        t1s = [
            T1Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
            ),
        ]
        line_number = 1
        for t1 in t1s:
            case_consistency_validator.add_record(t1, t1_schema, str(t1), line_number, False)
            line_number += 1

        t2s = [
            T2Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=1,
            ),
            T2Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=2,
            ),
        ]
        for t2 in t2s:
            case_consistency_validator.add_record(t2, t2_schema, str(t2), line_number, False)
            line_number += 1

        t3s = [
            T3Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=1,
            ),
            T3Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=2,
            ),
        ]
        for t3 in t3s:
            case_consistency_validator.add_record(t3, t3_schema, str(t3), line_number, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 0
        assert num_errors == 0

    @pytest.mark.parametrize("header,T1Stuff,T2Stuff,T3Stuff,stt_type", [
        (
            {"type": "A", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT1Factory, schema_defs.tanf.t1[0], "T1", "4", "6"),
            (factories.TanfT2Factory, schema_defs.tanf.t2[0], "T2"),
            (factories.TanfT3Factory, schema_defs.tanf.t3[0], "T3"),
            STT.EntityType.STATE,
        ),
        (
            {"type": "A", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT1Factory, schema_defs.tribal_tanf.t1[0], "T1", "4", "6"),
            (factories.TribalTanfT2Factory, schema_defs.tribal_tanf.t2[0], "T2"),
            (factories.TribalTanfT3Factory, schema_defs.tribal_tanf.t3[0], "T3"),
            STT.EntityType.TRIBE,
        ),
        (
            {"type": "A", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM1Factory, schema_defs.ssp.m1[0], "M1", "3", "5"),
            (factories.SSPM2Factory, schema_defs.ssp.m2[0], "M2"),
            (factories.SSPM3Factory, schema_defs.ssp.m3[0], "M3"),
            STT.EntityType.STATE,
        ),
    ])
    @pytest.mark.django_db
    def test_section1_records_are_related_validator_fail_no_t2_or_t3(
            self, small_correct_file, header, T1Stuff, T2Stuff, T3Stuff, stt_type):
        """Test records are related validator fails with no t2s or t3s."""
        (T1Factory, t1_schema, t1_model_name, rpt_item_num, case_item_num) = T1Stuff
        (T2Factory, t2_schema, t2_model_name) = T2Stuff
        (T3Factory, t3_schema, t3_model_name) = T3Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            stt_type,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        t1s = [
            T1Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123"
            ),
        ]
        line_number = 1
        for t1 in t1s:
            case_consistency_validator.add_record(t1, t1_schema, str(t1), line_number, False)
            line_number += 1

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 1
        assert num_errors == 1
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        is_tribal = "Tribal" in header['program_type']
        case_num = "Case Number"
        case_num += "--TANF" if is_tribal else ""
        assert errors[0].error_message == (
            f"Every {t1_model_name} record should have at least one corresponding "
            f"{t2_model_name} or {t3_model_name} record with the same Item {rpt_item_num} "
            f"(Reporting Year and Month) and Item {case_item_num} ({case_num})."
        )

    @pytest.mark.parametrize("header,T1Stuff,T2Stuff,T3Stuff,stt_type", [
        (
            {"type": "A", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT1Factory, schema_defs.tanf.t1[0], "T1", "4", "6"),
            (factories.TanfT2Factory, schema_defs.tanf.t2[0], "T2"),
            (factories.TanfT3Factory, schema_defs.tanf.t3[0], "T3"),
            STT.EntityType.STATE,
        ),
        (
            {"type": "A", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT1Factory, schema_defs.tribal_tanf.t1[0], "T1", "4", "6"),
            (factories.TribalTanfT2Factory, schema_defs.tribal_tanf.t2[0], "T2"),
            (factories.TribalTanfT3Factory, schema_defs.tribal_tanf.t3[0], "T3"),
            STT.EntityType.TRIBE,
        ),
        (
            {"type": "A", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM1Factory, schema_defs.ssp.m1[0], "M1", "3", "5"),
            (factories.SSPM2Factory, schema_defs.ssp.m2[0], "M2"),
            (factories.SSPM3Factory, schema_defs.ssp.m3[0], "M3"),
            STT.EntityType.STATE,
        ),
    ])
    @pytest.mark.django_db
    def test_section1_records_are_related_validator_fail_no_t1(
            self, small_correct_file, header, T1Stuff, T2Stuff, T3Stuff, stt_type):
        """Test records are related validator fails with no t1s."""
        (T1Factory, t1_schema, t1_model_name, rpt_item_num, case_item_num) = T1Stuff
        (T2Factory, t2_schema, t2_model_name) = T2Stuff
        (T3Factory, t3_schema, t3_model_name) = T3Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            stt_type,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        t2s = [
            T2Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=1,
            ),
            T2Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=2,
            ),
        ]
        line_number = 1
        for t2 in t2s:
            case_consistency_validator.add_record(t2, t2_schema, str(t2), line_number, False)
            line_number += 1

        t3s = [
            T3Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=1,
            ),
            T3Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=2,
            ),
        ]
        for t3 in t3s:
            case_consistency_validator.add_record(t3, t3_schema, str(t3), line_number, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 4
        assert num_errors == 4
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY

        is_tribal = "Tribal" in header['program_type']
        case_num = "Case Number"
        case_num += "--TANF" if is_tribal else ""
        assert errors[0].error_message == (
            f"Every {t2_model_name} record should have at least one corresponding "
            f"{t1_model_name} record with the same Item {rpt_item_num} "
            f"(Reporting Year and Month) and Item {case_item_num} ({case_num})."
        )
        assert errors[1].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[1].error_message == (
            f"Every {t2_model_name} record should have at least one corresponding "
            f"{t1_model_name} record with the same Item {rpt_item_num} "
            f"(Reporting Year and Month) and Item {case_item_num} ({case_num})."
        )
        assert errors[2].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[2].error_message == (
            f"Every {t3_model_name} record should have at least one corresponding "
            f"{t1_model_name} record with the same Item {rpt_item_num} "
            f"(Reporting Year and Month) and Item {case_item_num} ({case_num})."
        )
        assert errors[3].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[3].error_message == (
            f"Every {t3_model_name} record should have at least one corresponding "
            f"{t1_model_name} record with the same Item {rpt_item_num} "
            f"(Reporting Year and Month) and Item {case_item_num} ({case_num})."
        )

    @pytest.mark.parametrize("header,T1Stuff,T2Stuff,T3Stuff,stt_type", [
        (
            {"type": "A", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT1Factory, schema_defs.tanf.t1[0], "T1", "4", "6"),
            (factories.TanfT2Factory, schema_defs.tanf.t2[0], "T2", "30"),
            (factories.TanfT3Factory, schema_defs.tanf.t3[0], "T3", "67"),
            STT.EntityType.STATE,
        ),
        (
            {"type": "A", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT1Factory, schema_defs.tribal_tanf.t1[0], "T1", "4", "6"),
            (factories.TribalTanfT2Factory, schema_defs.tribal_tanf.t2[0], "T2", "30"),
            (factories.TribalTanfT3Factory, schema_defs.tribal_tanf.t3[0], "T3", "66"),
            STT.EntityType.TRIBE,
        ),
        (
            {"type": "A", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM1Factory, schema_defs.ssp.m1[0], "M1", "3", "5"),
            (factories.SSPM2Factory, schema_defs.ssp.m2[0], "M2", "26"),
            (factories.SSPM3Factory, schema_defs.ssp.m3[0], "M3", "60"),
            STT.EntityType.STATE,
        ),
    ])
    @pytest.mark.django_db
    def test_section1_records_are_related_validator_fail_no_family_affiliation(
            self, small_correct_file, header, T1Stuff, T2Stuff, T3Stuff, stt_type):
        """Test records are related validator fails when no t2 or t3 has family_affiliation == 1."""
        (T1Factory, t1_schema, t1_model_name, rpt_item_num, case_item_num) = T1Stuff
        (T2Factory, t2_schema, t2_model_name, t2_fam_afil_item_num) = T2Stuff
        (T3Factory, t3_schema, t3_model_name, t3_fam_afil_item_num) = T3Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            stt_type,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        t1s = [
            T1Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123"
            ),
        ]
        line_number = 1
        for t1 in t1s:
            case_consistency_validator.add_record(t1, t1_schema, str(t1), line_number, False)
            line_number += 1

        t2s = [
            T2Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=2,
            ),
            T2Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=2,
            ),
        ]
        for t2 in t2s:
            case_consistency_validator.add_record(t2, t2_schema, str(t2), line_number, False)
            line_number += 1

        t3s = [
            T3Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=2,
            ),
            T3Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=2,
            ),
        ]
        for t3 in t3s:
            case_consistency_validator.add_record(t3, t3_schema, str(t3), line_number, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 2
        assert num_errors == 1
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        is_tribal = "Tribal" in header['program_type']
        case_num = "Case Number"
        case_num += "--TANF" if is_tribal else ""
        assert errors[0].error_message == (
            f"Every {t1_model_name} record should have at least one corresponding "
            f"{t2_model_name} or {t3_model_name} record with the same Item {rpt_item_num} (Reporting Year and Month) "
            f"and Item {case_item_num} ({case_num}), where Item {t2_fam_afil_item_num} (Family Affiliation)==1 or "
            f"Item {t3_fam_afil_item_num} (Family Affiliation)==1."
        )

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff,stt_type", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4[0], "T4"),
            (factories.TanfT5Factory, schema_defs.tanf.t5[0], "T5"),
            STT.EntityType.STATE,
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4[0], "T4"),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5[0], "T5"),
            STT.EntityType.TRIBE,
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4[0], "M4"),
            (factories.SSPM5Factory, schema_defs.ssp.m5[0], "M5"),
            STT.EntityType.STATE,
        ),
    ])
    @pytest.mark.django_db
    def test_section2_validator_pass(self, small_correct_file, header, T4Stuff, T5Stuff, stt_type):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            stt_type,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        t4s = [
            T4Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
            ),
        ]
        line_number = 1
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, str(t4), line_number, False)
            line_number += 1

        t5s = [
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=3,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=1
            ),
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=1
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, str(t5), line_number, False)
            line_number += 1

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 0
        assert num_errors == 0

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff,stt_type", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4[0], "T4", "4", "9"),
            (factories.TanfT5Factory, schema_defs.tanf.t5[0], "T5", "28"),
            STT.EntityType.STATE,
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4[0], "T4", "4", "9"),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5[0], "T5", "28"),
            STT.EntityType.TRIBE,
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4[0], "M4", "3", "8"),
            (factories.SSPM5Factory, schema_defs.ssp.m5[0], "M5", "25"),
            STT.EntityType.STATE,
        ),
    ])
    @pytest.mark.django_db
    def test_section2_validator_fail_case_closure_employment(
            self, small_correct_file, header, T4Stuff, T5Stuff, stt_type):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name, rpt_item_num, closure_item_num) = T4Stuff
        (T5Factory, t5_schema, t5_model_name, emp_status_item_num) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            stt_type,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        t4s = [
            T4Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                CLOSURE_REASON="01"
            ),
        ]
        line_number = 1
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, str(t4), line_number, False)
            line_number += 1

        t5s = [
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=3,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=1,
                EMPLOYMENT_STATUS=3,
            ),
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=1,
                EMPLOYMENT_STATUS=2,
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, str(t5), line_number, False)
            line_number += 1

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 1
        assert num_errors == 0
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[0].error_message == (
            f"At least one person on the case must have Item {emp_status_item_num} (Employment Status) = 1:Yes in the "
            f"same Item {rpt_item_num} (Reporting Year and Month) since Item {closure_item_num} (Reason for Closure) = "
            "1:Employment/excess earnings."
        )

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff,stt_type", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4[0], "T4", "9"),
            (factories.TanfT5Factory, schema_defs.tanf.t5[0], "T5", "26"),
            STT.EntityType.STATE,
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4[0], "T4", "9"),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5[0], "T5", "26"),
            STT.EntityType.TRIBE,
        ),
    ])
    @pytest.mark.django_db
    def test_section2_validator_fail_case_closure_ftl(self, small_correct_file, header, T4Stuff, T5Stuff, stt_type):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name, closure_item_num) = T4Stuff
        (T5Factory, t5_schema, t5_model_name, fed_time_item_num) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            stt_type,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        t4s = [
            T4Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                CLOSURE_REASON="03"
            ),
        ]
        line_number = 1
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, str(t4), line_number, False)
            line_number += 1

        t5s = [
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=2,
                RELATIONSHIP_HOH="10",
                COUNTABLE_MONTH_FED_TIME="059",
            ),
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=3,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=2,
                RELATIONSHIP_HOH="03",
                COUNTABLE_MONTH_FED_TIME="001",
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, str(t5), line_number, False)
            line_number += 1

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 1
        assert num_errors == 0
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        is_tribal = "Tribal" in header["program_type"]
        tribe_or_fed = "Tribal" if is_tribal else "Federal"
        assert errors[0].error_message == ("At least one person who is head-of-household or spouse of "
                                           f"head-of-household on case must have Item {fed_time_item_num} "
                                           f"(Number of Months Countable Toward {tribe_or_fed} Time Limit) >= 60 since "
                                           f"Item {closure_item_num} (Reason for Closure) = 03: federal 5 year time "
                                           "limit.")

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff,stt_type", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4[0], "T4", "4", "6"),
            (factories.TanfT5Factory, schema_defs.tanf.t5[0], "T5"),
            STT.EntityType.STATE,
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4[0], "T4", "4", "6"),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5[0], "T5"),
            STT.EntityType.TRIBE,
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4[0], "M4", "3", "5"),
            (factories.SSPM5Factory, schema_defs.ssp.m5[0], "M5"),
            STT.EntityType.STATE,
        ),
    ])
    @pytest.mark.django_db
    def test_section2_records_are_related_validator_fail_no_t5s(
            self, small_correct_file, header, T4Stuff, T5Stuff, stt_type):
        """Test records are related validator fails with no t5s."""
        (T4Factory, t4_schema, t4_model_name, rpt_item_num, case_item_num) = T4Stuff
        (T5Factory, t5_schema, t5_model_name) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            stt_type,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        t4s = [
            T4Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
            ),
        ]
        line_number = 1
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, str(t4), line_number, False)
            line_number += 1

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 1
        assert num_errors == 1
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        is_tribal = "Tribal" in header['program_type']
        case_num = "Case Number"
        case_num += "--TANF" if is_tribal else ""
        assert errors[0].error_message == (
            f"Every {t4_model_name} record should have at least one corresponding "
            f"{t5_model_name} record with the same Item {rpt_item_num} (Reporting Year and Month) "
            f"and Item {case_item_num} ({case_num})."
        )

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff,stt_type", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4[0], "T4", "4", "6"),
            (factories.TanfT5Factory, schema_defs.tanf.t5[0], "T5"),
            STT.EntityType.STATE,
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4[0], "T4", "4", "6"),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5[0], "T5"),
            STT.EntityType.TRIBE,
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4[0], "M4", "3", "5"),
            (factories.SSPM5Factory, schema_defs.ssp.m5[0], "M5"),
            STT.EntityType.STATE,
        ),
    ])
    @pytest.mark.django_db
    def test_section2_records_are_related_validator_fail_no_t4s(
            self, small_correct_file, header, T4Stuff, T5Stuff, stt_type):
        """Test records are related validator fails with no t4s."""
        (T4Factory, t4_schema, t4_model_name, rpt_item_num, case_item_num) = T4Stuff
        (T5Factory, t5_schema, t5_model_name) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            stt_type,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        t5s = [
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=3,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=1
            ),
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=1
            ),
        ]
        line_number = 1
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, str(t5), line_number, False)
            line_number += 1

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 2
        assert num_errors == 2
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        is_tribal = "Tribal" in header['program_type']
        case_num = "Case Number"
        case_num += "--TANF" if is_tribal else ""
        assert errors[0].error_message == (
            f"Every {t5_model_name} record should have at least one corresponding "
            f"{t4_model_name} record with the same Item {rpt_item_num} (Reporting Year and Month) "
            f"and Item {case_item_num} ({case_num})."
        )
        assert errors[1].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[1].error_message == (
            f"Every {t5_model_name} record should have at least one corresponding "
            f"{t4_model_name} record with the same Item {rpt_item_num} (Reporting Year and Month) "
            f"and Item {case_item_num} ({case_num})."
        )

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4[0], "T4"),
            (factories.TanfT5Factory, schema_defs.tanf.t5[0], "T5"),
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4[0], "T4"),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5[0], "T5"),
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4[0], "M4"),
            (factories.SSPM5Factory, schema_defs.ssp.m5[0], "M5"),
        ),
    ])
    @pytest.mark.django_db
    def test_section2_aabd_ssi_validator_pass_territory_adult_aadb(self, small_correct_file, header, T4Stuff, T5Stuff):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            STT.EntityType.TERRITORY,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        t4s = [
            T4Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
            ),
        ]
        line_number = 1
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, str(t4), line_number, False)
            line_number += 1

        t5s = [
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                DATE_OF_BIRTH="19970209",
                FAMILY_AFFILIATION=1,
                REC_AID_TOTALLY_DISABLED=1,
                REC_SSI=2
            ),
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                DATE_OF_BIRTH="19970209",
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=2
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, str(t5), line_number, False)
            line_number += 1

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 0
        assert num_errors == 0

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4[0], "T4"),
            (factories.TanfT5Factory, schema_defs.tanf.t5[0], "T5", "19C"),
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4[0], "T4"),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5[0], "T5", "19C"),
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4[0], "M4"),
            (factories.SSPM5Factory, schema_defs.ssp.m5[0], "M5", "18C"),
        ),
    ])
    @pytest.mark.django_db
    def test_section2_aabd_ssi_validator_fail_territory_adult_aabd(self, small_correct_file, header, T4Stuff, T5Stuff):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name, ratd_item_num) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            STT.EntityType.TERRITORY,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        t4s = [
            T4Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
            ),
        ]
        line_number = 1
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, str(t4), line_number, False)
            line_number += 1

        t5s = [
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                DATE_OF_BIRTH="19970209",
                FAMILY_AFFILIATION=1,
                REC_AID_TOTALLY_DISABLED=0,
                REC_SSI=2
            ),
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                DATE_OF_BIRTH="19970209",
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=0,
                REC_SSI=2
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, str(t5), line_number, False)
            line_number += 1

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 2
        assert num_errors == 0
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[0].error_message == (
            f"{t5_model_name} Adults in territories must have a valid value for Item {ratd_item_num} "
            "(Received Disability Benefits: Permanently and Totally Disabled)."
        )
        assert errors[1].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[1].error_message == (
            f"{t5_model_name} Adults in territories must have a valid value for Item {ratd_item_num} "
            "(Received Disability Benefits: Permanently and Totally Disabled)."
        )

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4[0], "T4"),
            (factories.TanfT5Factory, schema_defs.tanf.t5[0], "T5"),
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4[0], "T4"),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5[0], "T5"),
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4[0], "M4"),
            (factories.SSPM5Factory, schema_defs.ssp.m5[0], "M5"),
        ),
    ])
    @pytest.mark.django_db
    def test_section2_aabd_ssi_validator_pass_territory_child_aabd(self, small_correct_file, header, T4Stuff, T5Stuff):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            STT.EntityType.TERRITORY,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        t4s = [
            T4Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
            ),
        ]
        line_number = 1
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, str(t4), line_number, False)
            line_number += 1

        t5s = [
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                DATE_OF_BIRTH="20170209",
                FAMILY_AFFILIATION=1,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=2
            ),
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                DATE_OF_BIRTH="20170209",
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=1,
                REC_SSI=2
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, str(t5), line_number, False)
            line_number += 1

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 0
        assert num_errors == 0

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4[0], "T4"),
            (factories.TanfT5Factory, schema_defs.tanf.t5[0], "T5", "19C"),
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4[0], "T4"),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5[0], "T5", "19C"),
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4[0], "M4"),
            (factories.SSPM5Factory, schema_defs.ssp.m5[0], "M5", "18C"),
        ),
    ])
    @pytest.mark.django_db
    def test_section2_atd_ssi_validator_fail_state_atdd(self, small_correct_file, header, T4Stuff, T5Stuff):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name, item_no) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            STT.EntityType.STATE,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        t4s = [
            T4Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
            ),
        ]
        line_number = 1
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, str(t4), line_number, False)
            line_number += 1

        t5s = [
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                DATE_OF_BIRTH="19970209",
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=1,
                REC_SSI=2
            ),
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                DATE_OF_BIRTH="20170209",
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=1,
                REC_SSI=2
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, str(t5), line_number, False)
            line_number += 1

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 2
        assert num_errors == 0
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[0].error_message == (
            f"{t5_model_name} People in states should not have a value of 1 for Item {item_no} ("
            "Received Disability Benefits: Permanently and Totally Disabled)."
        )
        assert errors[1].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[1].error_message == (
            f"{t5_model_name} People in states should not have a value of 1 for Item {item_no} "
            "(Received Disability Benefits: Permanently and Totally Disabled)."
        )

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4[0], "T4"),
            (factories.TanfT5Factory, schema_defs.tanf.t5[0], "T5", "19E"),
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4[0], "T4"),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5[0], "T5", "19E"),
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4[0], "M4"),
            (factories.SSPM5Factory, schema_defs.ssp.m5[0], "M5", "18E"),
        ),
    ])
    @pytest.mark.django_db
    def test_section2_aabd_ssi_validator_fail_territory_ssi(self, small_correct_file, header, T4Stuff, T5Stuff):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name, rec_ssi_item_num) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            STT.EntityType.TERRITORY,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        t4s = [
            T4Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
            ),
        ]
        line_number = 1
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, str(t4), line_number, False)
            line_number += 1

        t5s = [
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                DATE_OF_BIRTH="19970209",
                FAMILY_AFFILIATION=1,
                REC_AID_TOTALLY_DISABLED=1,
                REC_SSI=1
            ),
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                DATE_OF_BIRTH="19970209",
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=1,
                REC_SSI=1
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, str(t5), line_number, False)
            line_number += 1

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 2
        assert num_errors == 0
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[0].error_message == (
            f"{t5_model_name} People in territories must have value = 2:No for Item {rec_ssi_item_num} "
            "(Received Disability Benefits: SSI)."
        )
        assert errors[1].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[1].error_message == (
            f"{t5_model_name} People in territories must have value = 2:No for Item {rec_ssi_item_num} "
            "(Received Disability Benefits: SSI)."
        )

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4[0], "T4"),
            (factories.TanfT5Factory, schema_defs.tanf.t5[0], "T5", "19E"),
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4[0], "T4"),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5[0], "T5", "19E"),
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4[0], "M4"),
            (factories.SSPM5Factory, schema_defs.ssp.m5[0], "M5", "18E"),
        ),
    ])
    @pytest.mark.django_db
    def test_section2_atd_ssi_validator_fail_state_ssi(self, small_correct_file, header, T4Stuff, T5Stuff):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name, rec_ssi_item_num) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            STT.EntityType.STATE,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        t4s = [
            T4Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
            ),
        ]
        line_number = 1
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, str(t4), line_number, False)
            line_number += 1

        t5s = [
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                DATE_OF_BIRTH="19970209",
                FAMILY_AFFILIATION=1,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=0
            ),
            T5Factory.build(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                DATE_OF_BIRTH="19970209",
                FAMILY_AFFILIATION=2,  # validator only applies to fam_affil = 1; won't generate error
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=0
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, str(t5), line_number, False)
            line_number += 1

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 1
        assert num_errors == 0
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[0].error_message == (
            f"{t5_model_name} People in states must have a valid value for Item {rec_ssi_item_num} "
            "(Received Disability Benefits: SSI)."
        )

    @pytest.mark.parametrize("header,T1Stuff,T2Stuff,T3Stuff,stt_type", [
        (
            {"type": "A", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT1Factory, schema_defs.tanf.t1[0], "T1"),
            (factories.TanfT2Factory, schema_defs.tanf.t2[0], "T2"),
            (factories.TanfT3Factory, schema_defs.tanf.t3[0], "T3"),
            STT.EntityType.STATE,
        ),
        (
            {"type": "A", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT1Factory, schema_defs.tribal_tanf.t1[0], "T1"),
            (factories.TribalTanfT2Factory, schema_defs.tribal_tanf.t2[0], "T2"),
            (factories.TribalTanfT3Factory, schema_defs.tribal_tanf.t3[0], "T3"),
            STT.EntityType.STATE,
        ),
        (
            {"type": "A", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.SSPM1Factory, schema_defs.ssp.m1[0], "M1"),
            (factories.SSPM2Factory, schema_defs.ssp.m2[0], "M2"),
            (factories.SSPM3Factory, schema_defs.ssp.m3[0], "M3"),
            STT.EntityType.STATE,
        )
    ])
    @pytest.mark.django_db
    def test_section1_duplicate_records(self, small_correct_file, header, T1Stuff, T2Stuff, T3Stuff, stt_type):
        """Test section 1 exact duplicate records."""
        (T1Factory, t1_schema, t1_model_name) = T1Stuff
        (T2Factory, t2_schema, t2_model_name) = T2Stuff
        (T3Factory, t3_schema, t3_model_name) = T3Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            stt_type,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        t1 = T1Factory.build(RecordType="T1", RPT_MONTH_YEAR=202010, CASE_NUMBER="123")
        line_number = 1
        case_consistency_validator.add_record(t1, t1_schema, str(t1), line_number, False)
        line_number += 1

        t2 = T2Factory.build(RecordType="T2", RPT_MONTH_YEAR=202010, CASE_NUMBER="123", FAMILY_AFFILIATION=1,
                             SSN="111111111", DATE_OF_BIRTH="22222222")
        case_consistency_validator.add_record(t2, t2_schema, str(t2), line_number, False)
        line_number += 1

        t3s = [
            T3Factory.build(
                RecordType="T3",
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                SSN="111111111",
                DATE_OF_BIRTH="22222222"
            ),
            T3Factory.build(
                RecordType="T3",
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                SSN="111111111",
                DATE_OF_BIRTH="22222222"
            ),
        ]

        for t3 in t3s:
            case_consistency_validator.add_record(t3, t3_schema, str(t3), line_number, False)

        t1_dup = T1Factory.build(RecordType="T1", RPT_MONTH_YEAR=202010, CASE_NUMBER="123")
        line_number += 1
        has_errors, _, _ = case_consistency_validator.add_record(t1_dup, t1_schema, str(t1), line_number, False)
        line_number += 1
        assert has_errors

        t2_dup = T2Factory.build(RecordType="T2", RPT_MONTH_YEAR=202010, CASE_NUMBER="123", FAMILY_AFFILIATION=1,
                                 SSN="111111111", DATE_OF_BIRTH="22222222")
        has_errors, _, _ = case_consistency_validator.add_record(t2_dup, t2_schema, str(t2), line_number, False)
        line_number += 1
        assert has_errors

        t3_dup = T3Factory.build(RecordType="T3", RPT_MONTH_YEAR=202010, CASE_NUMBER="123", FAMILY_AFFILIATION=1,
                                 SSN="111111111", DATE_OF_BIRTH="22222222")
        has_errors, _, _ = case_consistency_validator.add_record(t3_dup, t3_schema, str(t3s[0]), line_number, False)
        line_number += 1
        assert has_errors

        errors = case_consistency_validator.get_generated_errors()
        assert len(errors) == 3
        for i, error in enumerate(errors):
            expected_msg = f"Duplicate record detected with record type T{i + 1} at line {i + 4}. Record is a " + \
                f"duplicate of the record at line number {i + 1}."
            assert error.error_message == expected_msg

    @pytest.mark.parametrize("header,T1Stuff,T2Stuff,T3Stuff,stt_type", [
        (
            {"type": "A", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT1Factory, schema_defs.tanf.t1[0], "T1"),
            (factories.TanfT2Factory, schema_defs.tanf.t2[0], "T2"),
            (factories.TanfT3Factory, schema_defs.tanf.t3[0], "T3"),
            STT.EntityType.STATE,
        ),
        (
            {"type": "A", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT1Factory, schema_defs.tribal_tanf.t1[0], "T1"),
            (factories.TribalTanfT2Factory, schema_defs.tribal_tanf.t2[0], "T2"),
            (factories.TribalTanfT3Factory, schema_defs.tribal_tanf.t3[0], "T3"),
            STT.EntityType.STATE,
        ),
        (
            {"type": "A", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.SSPM1Factory, schema_defs.ssp.m1[0], "M1"),
            (factories.SSPM2Factory, schema_defs.ssp.m2[0], "M2"),
            (factories.SSPM3Factory, schema_defs.ssp.m3[0], "M3"),
            STT.EntityType.STATE,
        ),
    ])
    @pytest.mark.django_db
    def test_section1_partial_duplicate_records_and_precedence(self, small_correct_file, header, T1Stuff, T2Stuff,
                                                               T3Stuff, stt_type):
        """Test section 1 partial duplicate records."""
        (T1Factory, t1_schema, t1_model_name) = T1Stuff
        (T2Factory, t2_schema, t2_model_name) = T2Stuff
        (T3Factory, t3_schema, t3_model_name) = T3Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            stt_type,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        t1 = T1Factory.build(RecordType="T1", RPT_MONTH_YEAR=202010, CASE_NUMBER="123")
        line_number = 1
        case_consistency_validator.add_record(t1, t1_schema, str(t1), line_number, False)
        line_number += 1

        t2 = T2Factory.build(RecordType="T2", RPT_MONTH_YEAR=202010, CASE_NUMBER="123", FAMILY_AFFILIATION=1,
                             SSN="111111111", DATE_OF_BIRTH="22222222")
        case_consistency_validator.add_record(t2, t2_schema, str(t2), line_number, False)
        line_number += 1

        t3s = [
            T3Factory.build(
                RecordType="T3",
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                SSN="111111111",
                DATE_OF_BIRTH="22222222"
            ),
            T3Factory.build(
                RecordType="T3",
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER="123",
                SSN="111111111",
                DATE_OF_BIRTH="22222222"
            ),
        ]

        for t3 in t3s:
            case_consistency_validator.add_record(t3, t3_schema, str(t3), line_number, False)

        # Introduce partial dups
        t1_dup = T1Factory.build(RecordType="T1", RPT_MONTH_YEAR=202010, CASE_NUMBER="123")
        line_number += 1
        has_errors, _, _ = case_consistency_validator.add_record(t1_dup, t1_schema, str(t1_dup), line_number, False)
        line_number += 1
        assert has_errors

        t2_dup = T2Factory.build(RecordType="T2", RPT_MONTH_YEAR=202010, CASE_NUMBER="123", FAMILY_AFFILIATION=1,
                                 SSN="111111111", DATE_OF_BIRTH="22222222")
        has_errors, _, _ = case_consistency_validator.add_record(t2_dup, t2_schema, str(t2_dup), line_number, False)
        line_number += 1
        assert has_errors

        t3_dup = T3Factory.build(RecordType="T3", RPT_MONTH_YEAR=202010, CASE_NUMBER="123", FAMILY_AFFILIATION=1,
                                 SSN="111111111", DATE_OF_BIRTH="22222222")
        has_errors, _, _ = case_consistency_validator.add_record(t3_dup, t3_schema, str(t3_dup), line_number, False)
        line_number += 1
        assert has_errors

        errors = case_consistency_validator.get_generated_errors()
        assert len(errors) == 3
        for i, error in enumerate(errors):
            expected_msg = f"Partial duplicate record detected with record type T{i + 1} at line {i + 4}. " + \
                f"Record is a partial duplicate of the record at line number {i + 1}."
            assert expected_msg in error.error_message

        # We don't want to clear dup errors to show that when our errors change precedence, errors with lower precedence
        # are automatically replaced with the errors of higher precedence.
        case_consistency_validator.clear_errors(clear_dup=False)

        t1_complete_dup = T1Factory.build(RecordType="T1", RPT_MONTH_YEAR=202010, CASE_NUMBER="123")
        has_errors, _, _ = case_consistency_validator.add_record(t1_complete_dup, t1_schema, str(t1),
                                                                 line_number, False)

        errors = case_consistency_validator.get_generated_errors()
        assert len(errors) == 1
        for i, error in enumerate(errors):
            expected_msg = f"Duplicate record detected with record type T{i + 1} at line 7. Record is a " + \
                f"duplicate of the record at line number {i + 1}."
            assert error.error_message == expected_msg

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4[0], "T4"),
            (factories.TanfT5Factory, schema_defs.tanf.t5[0], "T5"),
        ),
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4[0], "T4"),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5[0], "T5"),
        ),
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4[0], "M4"),
            (factories.SSPM5Factory, schema_defs.ssp.m5[0], "M5"),
        ),
    ])
    @pytest.mark.django_db
    def test_section2_duplicate_records(self, small_correct_file, header, T4Stuff, T5Stuff):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            STT.EntityType.STATE,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        line_number = 1
        t4 = T4Factory.build(RecordType="T4", RPT_MONTH_YEAR=202010, CASE_NUMBER="123")
        case_consistency_validator.add_record(t4, t4_schema, str(t4), line_number, False)
        line_number += 1

        t5 = T5Factory.build(RecordType="T5", RPT_MONTH_YEAR=202010, CASE_NUMBER="123", FAMILY_AFFILIATION=1,
                             SSN="111111111", DATE_OF_BIRTH="22222222")
        case_consistency_validator.add_record(t5, t5_schema, str(t5), line_number, False)
        line_number += 1

        t4_dup = T4Factory.build(RecordType="T4", RPT_MONTH_YEAR=202010, CASE_NUMBER="123")
        case_consistency_validator.add_record(t4_dup, t4_schema, str(t4), line_number, False)
        line_number += 1

        t5_dup = T5Factory.build(RecordType="T5", RPT_MONTH_YEAR=202010, CASE_NUMBER="123", FAMILY_AFFILIATION=1,
                                 SSN="111111111", DATE_OF_BIRTH="22222222")
        case_consistency_validator.add_record(t5_dup, t5_schema, str(t5), line_number, False)
        line_number += 1

        errors = case_consistency_validator.get_generated_errors()
        assert len(errors) == 2
        for i, error in enumerate(errors):
            expected_msg = f"Duplicate record detected with record type T{i + 4} at line {i + 3}. Record is a " + \
                f"duplicate of the record at line number {i + 1}."
            assert error.error_message == expected_msg

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4[0], "T4"),
            (factories.TanfT5Factory, schema_defs.tanf.t5[0], "T5"),
        ),
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4[0], "T4"),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5[0], "T5"),
        ),
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4[0], "M4"),
            (factories.SSPM5Factory, schema_defs.ssp.m5[0], "M5"),
        ),
    ])
    @pytest.mark.django_db
    def test_section2_partial_duplicate_records_and_precedence(self, small_correct_file, header, T4Stuff, T5Stuff):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            STT.EntityType.STATE,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        line_number = 1
        t4 = T4Factory.build(RecordType="T4", RPT_MONTH_YEAR=202010, CASE_NUMBER="123")
        case_consistency_validator.add_record(t4, t4_schema, str(t4), line_number, False)
        line_number += 1

        t5 = T5Factory.build(RecordType="T5", RPT_MONTH_YEAR=202010, CASE_NUMBER="123", FAMILY_AFFILIATION=1,
                             SSN="111111111", DATE_OF_BIRTH="22222222")
        case_consistency_validator.add_record(t5, t5_schema, str(t5), line_number, False)
        line_number += 1

        t4_dup = T4Factory.build(RecordType="T4", RPT_MONTH_YEAR=202010, CASE_NUMBER="123")
        case_consistency_validator.add_record(t4_dup, t4_schema, str(t4_dup), line_number, False)
        line_number += 1

        t5_dup = T5Factory.build(RecordType="T5", RPT_MONTH_YEAR=202010, CASE_NUMBER="123", FAMILY_AFFILIATION=1,
                                 SSN="111111111", DATE_OF_BIRTH="22222222")
        case_consistency_validator.add_record(t5_dup, t5_schema, str(t5_dup), line_number, False)
        line_number += 1

        errors = case_consistency_validator.get_generated_errors()
        assert len(errors) == 2
        for i, error in enumerate(errors):
            expected_msg = f"Partial duplicate record detected with record type T{i + 4} at line {i + 3}. " + \
                f"Record is a partial duplicate of the record at line number {i + 1}."
            assert expected_msg in error.error_message

        # We don't want to clear dup errors to show that when our errors change precedence, errors with lower precedence
        # are automatically replaced with the errors of higher precedence.
        case_consistency_validator.clear_errors(clear_dup=False)

        t4_complete_dup = T4Factory.build(RecordType="T4", RPT_MONTH_YEAR=202010, CASE_NUMBER="123")
        has_errors, _, _ = case_consistency_validator.add_record(t4_complete_dup, t4_schema, str(t4),
                                                                 line_number, False)

        errors = case_consistency_validator.get_generated_errors()
        assert len(errors) == 1
        for i, error in enumerate(errors):
            expected_msg = f"Duplicate record detected with record type T{i + 4} at line 5. Record is a " + \
                f"duplicate of the record at line number {i + 1}."
            assert error.error_message == expected_msg

    @pytest.mark.parametrize("header,record_stuff", [
        (
            {"type": "A", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT2Factory, schema_defs.tanf.t2[0], "T2"),
        ),
        (
            {"type": "A", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT3Factory, schema_defs.tanf.t3[0], "T3"),
        ),
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT5Factory, schema_defs.tanf.t5[0], "T5"),
        ),
    ])
    @pytest.mark.django_db
    def test_family_affiliation_negate_partial_duplicate(self, small_correct_file, header, record_stuff):
        """Test records are related validator section 2 success case."""
        (Factory, schema, model_name) = record_stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            STT.EntityType.STATE,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        line_number = 1
        first_record = Factory.build(RecordType=model_name, RPT_MONTH_YEAR=202010, CASE_NUMBER="123")
        case_consistency_validator.add_record(first_record, schema, str(first_record), line_number, False)
        line_number += 1

        second_record = Factory.build(RecordType=model_name, RPT_MONTH_YEAR=202010, CASE_NUMBER="123",
                                      FAMILY_AFFILIATION=5)
        case_consistency_validator.add_record(second_record, schema, str(second_record), line_number, False)
        line_number += 1

        errors = case_consistency_validator.get_generated_errors()
        assert len(errors) == 0

    @pytest.mark.parametrize("header,record_stuff", [
        (
            {"type": "G", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT6Factory, schema_defs.tanf.t6[0], "T6"),
        ),
        (
            {"type": "G", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT6Factory, schema_defs.tribal_tanf.t6[0], "T6"),
        ),
        (
            {"type": "G", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.SSPM6Factory, schema_defs.ssp.m6[0], "M6"),
        ),
        (
            {"type": "S", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT7Factory, schema_defs.tanf.t7[0], "T7"),
        ),
        (
            {"type": "S", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT7Factory, schema_defs.tribal_tanf.t7[0], "T7"),
        ),
        (
            {"type": "S", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.SSPM7Factory, schema_defs.ssp.m7[0], "M7"),
        ),
    ])
    @pytest.mark.django_db
    def test_s3_s4_duplicates(self, small_correct_file, header, record_stuff):
        """Test records are related validator section 2 success case."""
        (Factory, schema, model_name) = record_stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header["program_type"],
            STT.EntityType.STATE,
            util.make_generate_case_consistency_parser_error(small_correct_file)
        )

        line_number = 1
        # Because the line number is not changing in the loop, we know these records are coming from a single record in
        # the file. If the line number was changing, we would be flagging duplicate errors.
        first_record = None
        for i in range(5):
            record = Factory.build(RecordType=model_name, RPT_MONTH_YEAR=202010)
            if i == 0:
                first_record = record
            case_consistency_validator.add_record(record, schema, str(record), line_number, False)
        line_number += 1

        errors = case_consistency_validator.get_generated_errors()
        assert len(errors) == 0

        second_record = Factory.build(RecordType=model_name, RPT_MONTH_YEAR=202010)
        case_consistency_validator.add_record(second_record, schema, str(first_record), line_number, False)

        errors = case_consistency_validator.get_generated_errors()
        assert len(errors) == 1
        assert errors[0].error_message == f"Duplicate record detected with record type {model_name} at line 2. " + \
            "Record is a duplicate of the record at line number 1."
