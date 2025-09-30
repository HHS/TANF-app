"""Schema for T3 record type."""

from django.db.models import Q

from tdpservice.parsers.dataclasses import FieldType
from tdpservice.parsers.fields import Field, TransformField
from tdpservice.parsers.row_schema import TanfDataReportSchema
from tdpservice.parsers.transforms import tanf_ssn_decryption_func
from tdpservice.parsers.util import get_t2_t3_t5_partial_dup_fields
from tdpservice.parsers.validators import category1, category2, category3
from tdpservice.parsers.validators.util import is_quiet_preparser_errors
from tdpservice.search_indexes.models.program_audit import ProgramAudit_T3

FIRST_CHILD = 1
SECOND_CHILD = 2

child_one = TanfDataReportSchema(
    record_type="T3",
    model=ProgramAudit_T3,
    get_partial_dup_fields=get_t2_t3_t5_partial_dup_fields,
    partial_dup_exclusion_query=Q(FAMILY_AFFILIATION__in=(2, 4, 5)),
    preparsing_validators=[
        category1.program_audit_t3_validator(FIRST_CHILD),
        category1.caseNumberNotEmpty(8, 19),
        category1.or_priority_validators(
            [
                category1.validate_fieldYearMonth_with_headerYearQuarter(),
                category1.validateRptMonthYear(),
            ]
        ),
    ],
    postparsing_validators=[
        category3.ifThenAlso(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=category3.isEqual(1),
            result_field_name="CITIZENSHIP_STATUS",
            result_function=category3.isOneOf((1, 2, 3)),
        ),
        category3.ifThenAlso(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=category3.isEqual(2),
            result_field_name="CITIZENSHIP_STATUS",
            result_function=category3.isOneOf((1, 2, 3, 9)),
        ),
    ],
    fields=[
        Field(
            item="0",
            name="RecordType",
            friendly_name="Record Type",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=0,
            endIndex=2,
            required=True,
            validators=[],
        ),
        Field(
            item="4",
            name="RPT_MONTH_YEAR",
            friendly_name="Reporting Year and Month",
            type=FieldType.NUMERIC,
            startIndex=2,
            endIndex=8,
            required=True,
            validators=[
                category2.dateYearIsLargerThan(2023),
                category2.dateMonthIsValid(),
            ],
        ),
        Field(
            item="6",
            name="CASE_NUMBER",
            friendly_name="Case Number",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=8,
            endIndex=19,
            required=True,
            validators=[category2.isNotEmpty()],
        ),
        Field(
            item="67",
            name="FAMILY_AFFILIATION",
            friendly_name="Family Affiliation",
            type=FieldType.NUMERIC,
            startIndex=19,
            endIndex=20,
            required=True,
            validators=[category2.isOneOf([1, 2, 4])],
        ),
        Field(
            item="68",
            name="DATE_OF_BIRTH",
            friendly_name="Date of Birth",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=20,
            endIndex=28,
            required=True,
            validators=[
                category2.intHasLength(8),
                category2.dateYearIsLargerThan(1900),
                category2.dateMonthIsValid(),
                category2.dateDayIsValid(),
            ],
        ),
        TransformField(
            transform_func=tanf_ssn_decryption_func,
            item="69",
            name="SSN",
            friendly_name="Social Security Number",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=28,
            endIndex=37,
            required=True,
            validators=[category2.isNumber()],
            is_encrypted=False,
        ),
        Field(
            item="76",
            name="CITIZENSHIP_STATUS",
            friendly_name="Citizenship/Immigration Status",
            type=FieldType.NUMERIC,
            startIndex=51,
            endIndex=52,
            required=False,
            validators=[category2.isOneOf([1, 2, 3, 9])],
        ),
    ],
)


child_two = TanfDataReportSchema(
    record_type="T3",
    model=ProgramAudit_T3,
    get_partial_dup_fields=get_t2_t3_t5_partial_dup_fields,
    partial_dup_exclusion_query=Q(FAMILY_AFFILIATION__in=(2, 4, 5)),
    quiet_preparser_errors=is_quiet_preparser_errors(min_length=61),
    preparsing_validators=[
        category1.program_audit_t3_validator(SECOND_CHILD),
        category1.caseNumberNotEmpty(8, 19),
        category1.or_priority_validators(
            [
                category1.validate_fieldYearMonth_with_headerYearQuarter(),
                category1.validateRptMonthYear(),
            ]
        ),
    ],
    # all conditions from first child should be met, otherwise we don't parse second child
    postparsing_validators=[
        category3.ifThenAlso(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=category3.isEqual(1),
            result_field_name="CITIZENSHIP_STATUS",
            result_function=category3.isOneOf((1, 2, 3)),
        ),
        category3.ifThenAlso(
            condition_field_name="FAMILY_AFFILIATION",
            condition_function=category3.isEqual(2),
            result_field_name="CITIZENSHIP_STATUS",
            result_function=category3.isOneOf((1, 2, 3, 9)),
        ),
    ],
    fields=[
        Field(
            item="0",
            name="RecordType",
            friendly_name="Recod Type",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=0,
            endIndex=2,
            required=True,
            validators=[],
        ),
        Field(
            item="4",
            name="RPT_MONTH_YEAR",
            friendly_name="Reporting Year and Month",
            type=FieldType.NUMERIC,
            startIndex=2,
            endIndex=8,
            required=True,
            validators=[
                category2.dateYearIsLargerThan(2023),
                category2.dateMonthIsValid(),
            ],
        ),
        Field(
            item="6",
            name="CASE_NUMBER",
            friendly_name="Case Number",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=8,
            endIndex=19,
            required=True,
            validators=[category2.isNotEmpty()],
        ),
        Field(
            item="67",
            name="FAMILY_AFFILIATION",
            friendly_name="Family Affiliation",
            type=FieldType.NUMERIC,
            startIndex=60,
            endIndex=61,
            required=True,
            validators=[category2.isOneOf([1, 2, 4])],
        ),
        Field(
            item="68",
            name="DATE_OF_BIRTH",
            friendly_name="Date of Birth",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=61,
            endIndex=69,
            required=True,
            validators=[
                category2.intHasLength(8),
                category2.dateYearIsLargerThan(1900),
                category2.dateMonthIsValid(),
                category2.dateDayIsValid(),
            ],
        ),
        TransformField(
            transform_func=tanf_ssn_decryption_func,
            item="69",
            name="SSN",
            friendly_name="Social Security Number",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=69,
            endIndex=78,
            required=True,
            validators=[category2.isNumber()],
            is_encrypted=False,
        ),
        Field(
            item="76",
            name="CITIZENSHIP_STATUS",
            friendly_name="Citizenship/Immigration Status",
            type=FieldType.NUMERIC,
            startIndex=92,
            endIndex=93,
            required=False,
            validators=[category2.isOneOf([1, 2, 3, 9])],
        ),
    ],
)

t3 = [child_one, child_two]
