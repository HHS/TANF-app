"""Schema for T1 record types."""

from tdpservice.parsers.dataclasses import FieldType
from tdpservice.parsers.fields import Field
from tdpservice.parsers.row_schema import TanfDataReportSchema
from tdpservice.parsers.util import get_t1_t4_partial_dup_fields
from tdpservice.parsers.validators import category1, category2, category3
from tdpservice.search_indexes.models.program_audit import ProgramAudit_T1

t1 = [
    TanfDataReportSchema(
        record_type="T1",
        model=ProgramAudit_T1,
        get_partial_dup_fields=get_t1_t4_partial_dup_fields,
        preparsing_validators=[
            category1.recordHasLengthOfAtLeast(117),
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
                condition_field_name="CASH_AMOUNT",
                condition_function=category3.isGreaterThan(0),
                result_field_name="NBR_MONTHS",
                result_function=category3.isGreaterThan(0),
            ),
            category3.ifThenAlso(
                condition_field_name="CC_AMOUNT",
                condition_function=category3.isGreaterThan(0),
                result_field_name="CHILDREN_COVERED",
                result_function=category3.isGreaterThan(0),
            ),
            category3.ifThenAlso(
                condition_field_name="CC_AMOUNT",
                condition_function=category3.isGreaterThan(0),
                result_field_name="CC_NBR_MONTHS",
                result_function=category3.isGreaterThan(0),
            ),
            category3.ifThenAlso(
                condition_field_name="TRANSP_AMOUNT",
                condition_function=category3.isGreaterThan(0),
                result_field_name="TRANSP_NBR_MONTHS",
                result_function=category3.isGreaterThan(0),
            ),
            category3.ifThenAlso(
                condition_field_name="TRANSITION_SERVICES_AMOUNT",
                condition_function=category3.isGreaterThan(0),
                result_field_name="TRANSITION_NBR_MONTHS",
                result_function=category3.isGreaterThan(0),
            ),
            category3.ifThenAlso(
                condition_field_name="OTHER_AMOUNT",
                condition_function=category3.isGreaterThan(0),
                result_field_name="OTHER_NBR_MONTHS",
                result_function=category3.isGreaterThan(0),
            ),
            category3.ifThenAlso(
                condition_field_name="SANC_REDUCTION_AMT",
                condition_function=category3.isGreaterThan(0),
                result_field_name="WORK_REQ_SANCTION",
                result_function=category3.isOneOf((1, 2)),
            ),
            category3.ifThenAlso(
                condition_field_name="SANC_REDUCTION_AMT",
                condition_function=category3.isGreaterThan(0),
                result_field_name="SANC_TEEN_PARENT",
                result_function=category3.isOneOf((1, 2)),
            ),
            category3.ifThenAlso(
                condition_field_name="SANC_REDUCTION_AMT",
                condition_function=category3.isGreaterThan(0),
                result_field_name="NON_COOPERATION_CSE",
                result_function=category3.isOneOf((1, 2)),
            ),
            category3.ifThenAlso(
                condition_field_name="SANC_REDUCTION_AMT",
                condition_function=category3.isGreaterThan(0),
                result_field_name="FAILURE_TO_COMPLY",
                result_function=category3.isOneOf((1, 2)),
            ),
            category3.ifThenAlso(
                condition_field_name="SANC_REDUCTION_AMT",
                condition_function=category3.isGreaterThan(0),
                result_field_name="OTHER_SANCTION",
                result_function=category3.isOneOf((1, 2)),
            ),
            category3.ifThenAlso(
                condition_field_name="OTHER_TOTAL_REDUCTIONS",
                condition_function=category3.isGreaterThan(0),
                result_field_name="FAMILY_CAP",
                result_function=category3.isOneOf((1, 2)),
            ),
            category3.ifThenAlso(
                condition_field_name="OTHER_TOTAL_REDUCTIONS",
                condition_function=category3.isGreaterThan(0),
                result_field_name="REDUCTIONS_ON_RECEIPTS",
                result_function=category3.isOneOf((1, 2)),
            ),
            category3.ifThenAlso(
                condition_field_name="OTHER_TOTAL_REDUCTIONS",
                condition_function=category3.isGreaterThan(0),
                result_field_name="OTHER_NON_SANCTION",
                result_function=category3.isOneOf((1, 2)),
            ),
            category3.sumIsLarger(
                (
                    "AMT_FOOD_STAMP_ASSISTANCE",
                    "AMT_SUB_CC",
                    "CASH_AMOUNT",
                    "CC_AMOUNT",
                    "TRANSP_AMOUNT",
                ),
                0,
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
                    category2.dateYearIsLargerThan(1998),
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
                item="8",
                name="FUNDING_STREAM",
                friendly_name="Funding Stream",
                type=FieldType.NUMERIC,
                startIndex=29,
                endIndex=30,
                required=True,
                validators=[
                    category2.isBetween(1, 2, inclusive=True),
                ],
            ),
            Field(
                item="21A",
                name="CASH_AMOUNT",
                friendly_name="Cash",
                type=FieldType.NUMERIC,
                startIndex=55,
                endIndex=59,
                required=True,
                validators=[
                    category2.isGreaterThan(0, inclusive=True),
                ],
            ),
        ],
    )
]
