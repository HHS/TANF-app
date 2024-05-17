"""Test the CaseConsistencyValidator and SortedRecordSchemaPairs classes."""

import pytest
import logging
from tdpservice.parsers.test import factories
from .. import schema_defs, util
from ..case_consistency_validator import CaseConsistencyValidator
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
        return schema_defs.header.parse_and_validate(
            header_line,
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
        s1 = schema_defs.tanf.t1.schemas[0]
        s2 = schema_defs.tanf.t2.schemas[0]
        s3 = schema_defs.tanf.t3.schemas[0]
        return [s1, s2, s3, s3]

    @pytest.fixture
    def small_correct_file(self, stt_user, stt):
        """Fixture for small_correct_file."""
        return util.create_test_datafile('small_correct_file.txt', stt_user, stt)

    @pytest.fixture
    def small_correct_file_header(self, small_correct_file):
        """Return a valid header record."""
        header, header_is_valid, header_errors = self.parse_header(small_correct_file)

        if not header_is_valid:
            logger.error('Header is not valid: %s', header_errors)
            return None
        return header

    @pytest.mark.django_db
    def test_add_record(self, small_correct_file_header, small_correct_file, tanf_s1_records, tanf_s1_schemas):
        """Test add_record logic."""
        case_consistency_validator = CaseConsistencyValidator(
            small_correct_file_header,
            small_correct_file_header['program_type'],
            STT.EntityType.STATE,
            util.make_generate_parser_error(small_correct_file, None)
        )

        for record, schema in zip(tanf_s1_records, tanf_s1_schemas):
            case_consistency_validator.add_record(record, schema, True)

        assert case_consistency_validator.has_validated is False
        assert case_consistency_validator.case_has_errors is True
        assert len(case_consistency_validator.record_schema_pairs.cases) == 4
        assert case_consistency_validator.total_cases_cached == 0
        assert case_consistency_validator.total_cases_validated == 0

        # Add record with different case number to proc validation again and start caching a new case.
        t1 = factories.TanfT1Factory.create()
        t1.CASE_NUMBER = 2
        case_consistency_validator.add_record(t1, tanf_s1_schemas[0], False)
        assert case_consistency_validator.has_validated is False
        assert case_consistency_validator.case_has_errors is False
        assert len(case_consistency_validator.record_schema_pairs.cases) == 1
        assert case_consistency_validator.total_cases_cached == 1
        assert case_consistency_validator.total_cases_validated == 1

        # Complete the case to proc validation and verify that it occured. Even if the next case has errors.
        t2 = factories.TanfT2Factory.create()
        t3 = factories.TanfT3Factory.create()
        t2.CASE_NUMBER = 2
        t3.CASE_NUMBER = 2
        case_consistency_validator.add_record(t2, tanf_s1_schemas[1], False)
        case_consistency_validator.add_record(t3, tanf_s1_schemas[2], False)
        assert case_consistency_validator.case_has_errors is False

        case_consistency_validator.add_record(tanf_s1_records[0], tanf_s1_schemas[0], True)

        assert case_consistency_validator.has_validated is False
        assert case_consistency_validator.case_has_errors is True
        assert len(case_consistency_validator.record_schema_pairs.cases) == 1
        assert case_consistency_validator.total_cases_cached == 2
        assert case_consistency_validator.total_cases_validated == 2

    @pytest.mark.parametrize("header,T1Stuff,T2Stuff,T3Stuff,stt_type", [
        (
            {"type": "A", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT1Factory, schema_defs.tanf.t1.schemas[0], 'T1'),
            (factories.TanfT2Factory, schema_defs.tanf.t2.schemas[0], 'T2'),
            (factories.TanfT3Factory, schema_defs.tanf.t3.schemas[0], 'T3'),
            STT.EntityType.STATE,
        ),
        (
            {"type": "A", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT1Factory, schema_defs.tribal_tanf.t1.schemas[0], 'T1'),
            (factories.TribalTanfT2Factory, schema_defs.tribal_tanf.t2.schemas[0], 'T2'),
            (factories.TribalTanfT3Factory, schema_defs.tribal_tanf.t3.schemas[0], 'T3'),
            STT.EntityType.TRIBE,
        ),
        (
            {"type": "A", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM1Factory, schema_defs.ssp.m1.schemas[0], 'M1'),
            (factories.SSPM2Factory, schema_defs.ssp.m2.schemas[0], 'M2'),
            (factories.SSPM3Factory, schema_defs.ssp.m3.schemas[0], 'M3'),
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
            header['program_type'],
            stt_type,
            util.make_generate_parser_error(small_correct_file, None)
        )

        t1s = [
            T1Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
            ),
        ]
        for t1 in t1s:
            case_consistency_validator.add_record(t1, t1_schema, False)

        t2s = [
            T2Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=1,
            ),
            T2Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
            ),
        ]
        for t2 in t2s:
            case_consistency_validator.add_record(t2, t2_schema, False)

        t3s = [
            T3Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=1,
            ),
            T3Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
            ),
        ]
        for t3 in t3s:
            case_consistency_validator.add_record(t3, t3_schema, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 0
        assert num_errors == 0

    @pytest.mark.parametrize("header,T1Stuff,T2Stuff,T3Stuff,stt_type", [
        (
            {"type": "A", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT1Factory, schema_defs.tanf.t1.schemas[0], 'T1'),
            (factories.TanfT2Factory, schema_defs.tanf.t2.schemas[0], 'T2'),
            (factories.TanfT3Factory, schema_defs.tanf.t3.schemas[0], 'T3'),
            STT.EntityType.STATE,
        ),
        (
            {"type": "A", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT1Factory, schema_defs.tribal_tanf.t1.schemas[0], 'T1'),
            (factories.TribalTanfT2Factory, schema_defs.tribal_tanf.t2.schemas[0], 'T2'),
            (factories.TribalTanfT3Factory, schema_defs.tribal_tanf.t3.schemas[0], 'T3'),
            STT.EntityType.TRIBE,
        ),
        (
            {"type": "A", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM1Factory, schema_defs.ssp.m1.schemas[0], 'M1'),
            (factories.SSPM2Factory, schema_defs.ssp.m2.schemas[0], 'M2'),
            (factories.SSPM3Factory, schema_defs.ssp.m3.schemas[0], 'M3'),
            STT.EntityType.STATE,
        ),
    ])
    @pytest.mark.django_db
    def test_section1_records_are_related_validator_fail_no_t2_or_t3(
            self, small_correct_file, header, T1Stuff, T2Stuff, T3Stuff, stt_type):
        """Test records are related validator fails with no t2s or t3s."""
        (T1Factory, t1_schema, t1_model_name) = T1Stuff
        (T2Factory, t2_schema, t2_model_name) = T2Stuff
        (T3Factory, t3_schema, t3_model_name) = T3Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header['program_type'],
            stt_type,
            util.make_generate_parser_error(small_correct_file, None)
        )

        t1s = [
            T1Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123'
            ),
        ]
        for t1 in t1s:
            case_consistency_validator.add_record(t1, t1_schema, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 1
        assert num_errors == 1
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[0].error_message == (
            f'Every {t1_model_name} record should have at least one corresponding '
            f'{t2_model_name} or {t3_model_name} record with the same RPT_MONTH_YEAR and CASE_NUMBER.'
        )

    @pytest.mark.parametrize("header,T1Stuff,T2Stuff,T3Stuff,stt_type", [
        (
            {"type": "A", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT1Factory, schema_defs.tanf.t1.schemas[0], 'T1'),
            (factories.TanfT2Factory, schema_defs.tanf.t2.schemas[0], 'T2'),
            (factories.TanfT3Factory, schema_defs.tanf.t3.schemas[0], 'T3'),
            STT.EntityType.STATE,
        ),
        (
            {"type": "A", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT1Factory, schema_defs.tribal_tanf.t1.schemas[0], 'T1'),
            (factories.TribalTanfT2Factory, schema_defs.tribal_tanf.t2.schemas[0], 'T2'),
            (factories.TribalTanfT3Factory, schema_defs.tribal_tanf.t3.schemas[0], 'T3'),
            STT.EntityType.TRIBE,
        ),
        (
            {"type": "A", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM1Factory, schema_defs.ssp.m1.schemas[0], 'M1'),
            (factories.SSPM2Factory, schema_defs.ssp.m2.schemas[0], 'M2'),
            (factories.SSPM3Factory, schema_defs.ssp.m3.schemas[0], 'M3'),
            STT.EntityType.STATE,
        ),
    ])
    @pytest.mark.django_db
    def test_section1_records_are_related_validator_fail_no_t1(
            self, small_correct_file, header, T1Stuff, T2Stuff, T3Stuff, stt_type):
        """Test records are related validator fails with no t1s."""
        (T1Factory, t1_schema, t1_model_name) = T1Stuff
        (T2Factory, t2_schema, t2_model_name) = T2Stuff
        (T3Factory, t3_schema, t3_model_name) = T3Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header['program_type'],
            stt_type,
            util.make_generate_parser_error(small_correct_file, None)
        )

        t2s = [
            T2Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=1,
            ),
            T2Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
            ),
        ]
        for t2 in t2s:
            case_consistency_validator.add_record(t2, t2_schema, False)

        t3s = [
            T3Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=1,
            ),
            T3Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
            ),
        ]
        for t3 in t3s:
            case_consistency_validator.add_record(t3, t3_schema, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 4
        assert num_errors == 4
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[0].error_message == (
            f'Every {t2_model_name} record should have at least one corresponding '
            f'{t1_model_name} record with the same RPT_MONTH_YEAR and CASE_NUMBER.'
        )
        assert errors[1].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[1].error_message == (
            f'Every {t2_model_name} record should have at least one corresponding '
            f'{t1_model_name} record with the same RPT_MONTH_YEAR and CASE_NUMBER.'
        )
        assert errors[2].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[2].error_message == (
            f'Every {t3_model_name} record should have at least one corresponding '
            f'{t1_model_name} record with the same RPT_MONTH_YEAR and CASE_NUMBER.'
        )
        assert errors[3].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[3].error_message == (
            f'Every {t3_model_name} record should have at least one corresponding '
            f'{t1_model_name} record with the same RPT_MONTH_YEAR and CASE_NUMBER.'
        )

    @pytest.mark.parametrize("header,T1Stuff,T2Stuff,T3Stuff,stt_type", [
        (
            {"type": "A", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT1Factory, schema_defs.tanf.t1.schemas[0], 'T1'),
            (factories.TanfT2Factory, schema_defs.tanf.t2.schemas[0], 'T2'),
            (factories.TanfT3Factory, schema_defs.tanf.t3.schemas[0], 'T3'),
            STT.EntityType.STATE,
        ),
        (
            {"type": "A", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT1Factory, schema_defs.tribal_tanf.t1.schemas[0], 'T1'),
            (factories.TribalTanfT2Factory, schema_defs.tribal_tanf.t2.schemas[0], 'T2'),
            (factories.TribalTanfT3Factory, schema_defs.tribal_tanf.t3.schemas[0], 'T3'),
            STT.EntityType.TRIBE,
        ),
        (
            {"type": "A", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM1Factory, schema_defs.ssp.m1.schemas[0], 'M1'),
            (factories.SSPM2Factory, schema_defs.ssp.m2.schemas[0], 'M2'),
            (factories.SSPM3Factory, schema_defs.ssp.m3.schemas[0], 'M3'),
            STT.EntityType.STATE,
        ),
    ])
    @pytest.mark.django_db
    def test_section1_records_are_related_validator_fail_multiple_t1s(
            self, small_correct_file, header, T1Stuff, T2Stuff, T3Stuff, stt_type):
        """Test records are related validator fails when there are multiple t1s."""
        (T1Factory, t1_schema, t1_model_name) = T1Stuff
        (T2Factory, t2_schema, t2_model_name) = T2Stuff
        (T3Factory, t3_schema, t3_model_name) = T3Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header['program_type'],
            stt_type,
            util.make_generate_parser_error(small_correct_file, None)
        )

        t1s = [
            T1Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123'
            ),
            T1Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123'
            ),
        ]
        for t1 in t1s:
            case_consistency_validator.add_record(t1, t1_schema, False)

        t2s = [
            T2Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=1,
            ),
            T2Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
            ),
        ]
        for t2 in t2s:
            case_consistency_validator.add_record(t2, t2_schema, False)

        t3s = [
            T3Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=1,
            ),
            T3Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
            ),
        ]
        for t3 in t3s:
            case_consistency_validator.add_record(t3, t3_schema, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 1
        assert num_errors == 1
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[0].error_message == (
            f'There should only be one {t1_model_name} record '
            f'per RPT_MONTH_YEAR and CASE_NUMBER.'
        )

    @pytest.mark.parametrize("header,T1Stuff,T2Stuff,T3Stuff,stt_type", [
        (
            {"type": "A", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT1Factory, schema_defs.tanf.t1.schemas[0], 'T1'),
            (factories.TanfT2Factory, schema_defs.tanf.t2.schemas[0], 'T2'),
            (factories.TanfT3Factory, schema_defs.tanf.t3.schemas[0], 'T3'),
            STT.EntityType.STATE,
        ),
        (
            {"type": "A", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT1Factory, schema_defs.tribal_tanf.t1.schemas[0], 'T1'),
            (factories.TribalTanfT2Factory, schema_defs.tribal_tanf.t2.schemas[0], 'T2'),
            (factories.TribalTanfT3Factory, schema_defs.tribal_tanf.t3.schemas[0], 'T3'),
            STT.EntityType.TRIBE,
        ),
        (
            {"type": "A", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM1Factory, schema_defs.ssp.m1.schemas[0], 'M1'),
            (factories.SSPM2Factory, schema_defs.ssp.m2.schemas[0], 'M2'),
            (factories.SSPM3Factory, schema_defs.ssp.m3.schemas[0], 'M3'),
            STT.EntityType.STATE,
        ),
    ])
    @pytest.mark.django_db
    def test_section1_records_are_related_validator_fail_no_family_affiliation(
            self, small_correct_file, header, T1Stuff, T2Stuff, T3Stuff, stt_type):
        """Test records are related validator fails when no t2 or t3 has family_affiliation == 1."""
        (T1Factory, t1_schema, t1_model_name) = T1Stuff
        (T2Factory, t2_schema, t2_model_name) = T2Stuff
        (T3Factory, t3_schema, t3_model_name) = T3Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header['program_type'],
            stt_type,
            util.make_generate_parser_error(small_correct_file, None)
        )

        t1s = [
            T1Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123'
            ),
        ]
        for t1 in t1s:
            case_consistency_validator.add_record(t1, t1_schema, False)

        t2s = [
            T2Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
            ),
            T2Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
            ),
        ]
        for t2 in t2s:
            case_consistency_validator.add_record(t2, t2_schema, False)

        t3s = [
            T3Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
            ),
            T3Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
            ),
        ]
        for t3 in t3s:
            case_consistency_validator.add_record(t3, t3_schema, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 1
        assert num_errors == 1
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[0].error_message == (
            f'Every {t1_model_name} record should have at least one corresponding '
            f'{t2_model_name} or {t3_model_name} record with the same RPT_MONTH_YEAR and '
            f'CASE_NUMBER, where FAMILY_AFFILIATION==1'
        )

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff,stt_type", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4.schemas[0], 'T4'),
            (factories.TanfT5Factory, schema_defs.tanf.t5.schemas[0], 'T5'),
            STT.EntityType.STATE,
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4.schemas[0], 'T4'),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5.schemas[0], 'T5'),
            STT.EntityType.TRIBE,
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4.schemas[0], 'M4'),
            (factories.SSPM5Factory, schema_defs.ssp.m5.schemas[0], 'M5'),
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
            header['program_type'],
            stt_type,
            util.make_generate_parser_error(small_correct_file, None)
        )

        t4s = [
            T4Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
            ),
        ]
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, False)

        t5s = [
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=2
            ),
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=2
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 0
        assert num_errors == 0

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff,stt_type", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4.schemas[0], 'T4'),
            (factories.TanfT5Factory, schema_defs.tanf.t5.schemas[0], 'T5'),
            STT.EntityType.STATE,
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4.schemas[0], 'T4'),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5.schemas[0], 'T5'),
            STT.EntityType.TRIBE,
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4.schemas[0], 'M4'),
            (factories.SSPM5Factory, schema_defs.ssp.m5.schemas[0], 'M5'),
            STT.EntityType.STATE,
        ),
    ])
    @pytest.mark.django_db
    def test_section2_validator_fail_multiple_t4s(self, small_correct_file, header, T4Stuff, T5Stuff, stt_type):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header['program_type'],
            stt_type,
            util.make_generate_parser_error(small_correct_file, None)
        )

        t4s = [
            T4Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
            ),
            T4Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123'
            ),
        ]
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, False)

        t5s = [
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=2
            ),
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=2
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 1
        assert num_errors == 1
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[0].error_message == (
            f'There should only be one {t4_model_name} record  '
            f'per RPT_MONTH_YEAR and CASE_NUMBER.'
        )

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff,stt_type", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4.schemas[0], 'T4'),
            (factories.TanfT5Factory, schema_defs.tanf.t5.schemas[0], 'T5'),
            STT.EntityType.STATE,
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4.schemas[0], 'T4'),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5.schemas[0], 'T5'),
            STT.EntityType.TRIBE,
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4.schemas[0], 'M4'),
            (factories.SSPM5Factory, schema_defs.ssp.m5.schemas[0], 'M5'),
            STT.EntityType.STATE,
        ),
    ])
    @pytest.mark.django_db
    def test_section2_validator_fail_case_closure_employment(
            self, small_correct_file, header, T4Stuff, T5Stuff, stt_type):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header['program_type'],
            stt_type,
            util.make_generate_parser_error(small_correct_file, None)
        )

        t4s = [
            T4Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                CLOSURE_REASON='01'
            ),
        ]
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, False)

        t5s = [
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=2,
                EMPLOYMENT_STATUS=3,
            ),
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=2,
                EMPLOYMENT_STATUS=2,
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 1
        assert num_errors == 1
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[0].error_message == (
            'At least one person on the case must have employment status = 1:Yes'
            ' in the same RPT_MONTH_YEAR since CLOSURE_REASON = 1:Employment/excess earnings.'
        )

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff,stt_type", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4.schemas[0], 'T4'),
            (factories.TanfT5Factory, schema_defs.tanf.t5.schemas[0], 'T5'),
            STT.EntityType.STATE,
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4.schemas[0], 'T4'),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5.schemas[0], 'T5'),
            STT.EntityType.TRIBE,
        ),
    ])
    @pytest.mark.django_db
    def test_section2_validator_fail_case_closure_ftl(self, small_correct_file, header, T4Stuff, T5Stuff, stt_type):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header['program_type'],
            stt_type,
            util.make_generate_parser_error(small_correct_file, None)
        )

        t4s = [
            T4Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                CLOSURE_REASON='03'
            ),
        ]
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, False)

        t5s = [
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=2,
                RELATIONSHIP_HOH='10',
                COUNTABLE_MONTH_FED_TIME='059',
            ),
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=2,
                RELATIONSHIP_HOH='03',
                COUNTABLE_MONTH_FED_TIME='001',
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 1
        assert num_errors == 1
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[0].error_message == (
            'At least one person who is HoH or spouse of HoH on case must have FTL months >=60.'
        )

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff,stt_type", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4.schemas[0], 'T4'),
            (factories.TanfT5Factory, schema_defs.tanf.t5.schemas[0], 'T5'),
            STT.EntityType.STATE,
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4.schemas[0], 'T4'),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5.schemas[0], 'T5'),
            STT.EntityType.TRIBE,
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4.schemas[0], 'M4'),
            (factories.SSPM5Factory, schema_defs.ssp.m5.schemas[0], 'M5'),
            STT.EntityType.STATE,
        ),
    ])
    @pytest.mark.django_db
    def test_section2_records_are_related_validator_fail_no_t5s(
            self, small_correct_file, header, T4Stuff, T5Stuff, stt_type):
        """Test records are related validator fails with no t5s."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header['program_type'],
            stt_type,
            util.make_generate_parser_error(small_correct_file, None)
        )

        t4s = [
            T4Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
            ),
        ]
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 1
        assert num_errors == 1
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[0].error_message == (
            f'Every {t4_model_name} record should have at least one corresponding '
            f'{t5_model_name} record with the same RPT_MONTH_YEAR and CASE_NUMBER.'
        )

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff,stt_type", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4.schemas[0], 'T4'),
            (factories.TanfT5Factory, schema_defs.tanf.t5.schemas[0], 'T5'),
            STT.EntityType.STATE,
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4.schemas[0], 'T4'),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5.schemas[0], 'T5'),
            STT.EntityType.TRIBE,
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4.schemas[0], 'M4'),
            (factories.SSPM5Factory, schema_defs.ssp.m5.schemas[0], 'M5'),
            STT.EntityType.STATE,
        ),
    ])
    @pytest.mark.django_db
    def test_section2_records_are_related_validator_fail_no_t4s(
            self, small_correct_file, header, T4Stuff, T5Stuff, stt_type):
        """Test records are related validator fails with no t4s."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header['program_type'],
            stt_type,
            util.make_generate_parser_error(small_correct_file, None)
        )

        t5s = [
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=2
            ),
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=2
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 2
        assert num_errors == 2
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[0].error_message == (
            f'Every {t5_model_name} record should have at least one corresponding '
            f'{t4_model_name} record with the same RPT_MONTH_YEAR and CASE_NUMBER.'
        )
        assert errors[1].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[1].error_message == (
            f'Every {t5_model_name} record should have at least one corresponding '
            f'{t4_model_name} record with the same RPT_MONTH_YEAR and CASE_NUMBER.'
        )

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4.schemas[0], 'T4'),
            (factories.TanfT5Factory, schema_defs.tanf.t5.schemas[0], 'T5'),
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4.schemas[0], 'T4'),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5.schemas[0], 'T5'),
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4.schemas[0], 'M4'),
            (factories.SSPM5Factory, schema_defs.ssp.m5.schemas[0], 'M5'),
        ),
    ])
    @pytest.mark.django_db
    def test_section2_aabd_ssi_validator_pass_territory_adult_aadb(self, small_correct_file, header, T4Stuff, T5Stuff):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header['program_type'],
            STT.EntityType.TERRITORY,
            util.make_generate_parser_error(small_correct_file, None)
        )

        t4s = [
            T4Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
            ),
        ]
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, False)

        t5s = [
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                DATE_OF_BIRTH="19970209",
                FAMILY_AFFILIATION=1,
                REC_AID_TOTALLY_DISABLED=1,
                REC_SSI=2
            ),
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                DATE_OF_BIRTH="19970209",
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=2
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 0
        assert num_errors == 0

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4.schemas[0], 'T4'),
            (factories.TanfT5Factory, schema_defs.tanf.t5.schemas[0], 'T5'),
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4.schemas[0], 'T4'),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5.schemas[0], 'T5'),
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4.schemas[0], 'M4'),
            (factories.SSPM5Factory, schema_defs.ssp.m5.schemas[0], 'M5'),
        ),
    ])
    @pytest.mark.django_db
    def test_section2_aabd_ssi_validator_fail_territory_adult_aabd(self, small_correct_file, header, T4Stuff, T5Stuff):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header['program_type'],
            STT.EntityType.TERRITORY,
            util.make_generate_parser_error(small_correct_file, None)
        )

        t4s = [
            T4Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
            ),
        ]
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, False)

        t5s = [
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                DATE_OF_BIRTH="19970209",
                FAMILY_AFFILIATION=1,
                REC_AID_TOTALLY_DISABLED=0,
                REC_SSI=2
            ),
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                DATE_OF_BIRTH="19970209",
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=0,
                REC_SSI=2
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 2
        assert num_errors == 2
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[0].error_message == (
            f'{t5_model_name} Adults in territories must have a valid value for 19C.'
        )
        assert errors[1].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[1].error_message == (
            f'{t5_model_name} Adults in territories must have a valid value for 19C.'
        )

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4.schemas[0], 'T4'),
            (factories.TanfT5Factory, schema_defs.tanf.t5.schemas[0], 'T5'),
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4.schemas[0], 'T4'),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5.schemas[0], 'T5'),
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4.schemas[0], 'M4'),
            (factories.SSPM5Factory, schema_defs.ssp.m5.schemas[0], 'M5'),
        ),
    ])
    @pytest.mark.django_db
    def test_section2_aabd_ssi_validator_pass_territory_child_aabd(self, small_correct_file, header, T4Stuff, T5Stuff):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header['program_type'],
            STT.EntityType.TERRITORY,
            util.make_generate_parser_error(small_correct_file, None)
        )

        t4s = [
            T4Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
            ),
        ]
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, False)

        t5s = [
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                DATE_OF_BIRTH="20170209",
                FAMILY_AFFILIATION=1,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=2
            ),
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                DATE_OF_BIRTH="20170209",
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=1,
                REC_SSI=2
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 0
        assert num_errors == 0

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4.schemas[0], 'T4'),
            (factories.TanfT5Factory, schema_defs.tanf.t5.schemas[0], 'T5'),
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4.schemas[0], 'T4'),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5.schemas[0], 'T5'),
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4.schemas[0], 'M4'),
            (factories.SSPM5Factory, schema_defs.ssp.m5.schemas[0], 'M5'),
        ),
    ])
    @pytest.mark.django_db
    def test_section2_aabd_ssi_validator_fail_state_aabd(self, small_correct_file, header, T4Stuff, T5Stuff):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header['program_type'],
            STT.EntityType.STATE,
            util.make_generate_parser_error(small_correct_file, None)
        )

        t4s = [
            T4Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
            ),
        ]
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, False)

        t5s = [
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                DATE_OF_BIRTH="19970209",
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=1,
                REC_SSI=2
            ),
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                DATE_OF_BIRTH="20170209",
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=1,
                REC_SSI=2
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 2
        assert num_errors == 2
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[0].error_message == (
            f'{t5_model_name} People in states should not have a value of 1.'
        )
        assert errors[1].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[1].error_message == (
            f'{t5_model_name} People in states should not have a value of 1.'
        )

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4.schemas[0], 'T4'),
            (factories.TanfT5Factory, schema_defs.tanf.t5.schemas[0], 'T5'),
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4.schemas[0], 'T4'),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5.schemas[0], 'T5'),
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4.schemas[0], 'M4'),
            (factories.SSPM5Factory, schema_defs.ssp.m5.schemas[0], 'M5'),
        ),
    ])
    @pytest.mark.django_db
    def test_section2_aabd_ssi_validator_fail_territory_ssi(self, small_correct_file, header, T4Stuff, T5Stuff):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header['program_type'],
            STT.EntityType.TERRITORY,
            util.make_generate_parser_error(small_correct_file, None)
        )

        t4s = [
            T4Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
            ),
        ]
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, False)

        t5s = [
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                DATE_OF_BIRTH="19970209",
                FAMILY_AFFILIATION=1,
                REC_AID_TOTALLY_DISABLED=1,
                REC_SSI=1
            ),
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                DATE_OF_BIRTH="19970209",
                FAMILY_AFFILIATION=2,
                REC_AID_TOTALLY_DISABLED=1,
                REC_SSI=1
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 2
        assert num_errors == 2
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[0].error_message == (
            f'{t5_model_name} People in territories must have value = 2:No for 19E.'
        )
        assert errors[1].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[1].error_message == (
            f'{t5_model_name} People in territories must have value = 2:No for 19E.'
        )

    @pytest.mark.parametrize("header,T4Stuff,T5Stuff", [
        (
            {"type": "C", "program_type": "TAN", "year": 2020, "quarter": "4"},
            (factories.TanfT4Factory, schema_defs.tanf.t4.schemas[0], 'T4'),
            (factories.TanfT5Factory, schema_defs.tanf.t5.schemas[0], 'T5'),
        ),
        (
            {"type": "C", "program_type": "Tribal TAN", "year": 2020, "quarter": "4"},
            (factories.TribalTanfT4Factory, schema_defs.tribal_tanf.t4.schemas[0], 'T4'),
            (factories.TribalTanfT5Factory, schema_defs.tribal_tanf.t5.schemas[0], 'T5'),
        ),
        (
            {"type": "C", "program_type": "SSP", "year": 2020, "quarter": "4"},
            (factories.SSPM4Factory, schema_defs.ssp.m4.schemas[0], 'M4'),
            (factories.SSPM5Factory, schema_defs.ssp.m5.schemas[0], 'M5'),
        ),
    ])
    @pytest.mark.django_db
    def test_section2_aabd_ssi_validator_fail_state_ssi(self, small_correct_file, header, T4Stuff, T5Stuff):
        """Test records are related validator section 2 success case."""
        (T4Factory, t4_schema, t4_model_name) = T4Stuff
        (T5Factory, t5_schema, t5_model_name) = T5Stuff

        case_consistency_validator = CaseConsistencyValidator(
            header,
            header['program_type'],
            STT.EntityType.STATE,
            util.make_generate_parser_error(small_correct_file, None)
        )

        t4s = [
            T4Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
            ),
        ]
        for t4 in t4s:
            case_consistency_validator.add_record(t4, t4_schema, False)

        t5s = [
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                DATE_OF_BIRTH="19970209",
                FAMILY_AFFILIATION=1,
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=2
            ),
            T5Factory.create(
                RPT_MONTH_YEAR=202010,
                CASE_NUMBER='123',
                DATE_OF_BIRTH="19970209",
                FAMILY_AFFILIATION=2,  # validator only applies to fam_affil = 1; won't generate error
                REC_AID_TOTALLY_DISABLED=2,
                REC_SSI=2
            ),
        ]
        for t5 in t5s:
            case_consistency_validator.add_record(t5, t5_schema, False)

        num_errors = case_consistency_validator.validate()

        errors = case_consistency_validator.get_generated_errors()

        assert len(errors) == 1
        assert num_errors == 1
        assert errors[0].error_type == ParserErrorCategoryChoices.CASE_CONSISTENCY
        assert errors[0].error_message == (
            f'{t5_model_name} People in states must have a valid value.'
        )
