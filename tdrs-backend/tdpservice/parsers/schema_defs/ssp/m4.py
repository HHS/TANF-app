"""Schema for SSP M4 record type."""

from tdpservice.parsers.dataclasses import FieldType
from tdpservice.parsers.transforms import zero_pad
from tdpservice.parsers.fields import Field, TransformField
from tdpservice.parsers.row_schema import TanfDataReportSchema
from tdpservice.parsers.validators import category1, category2, category3
from tdpservice.search_indexes.models.ssp import SSP_M4
from tdpservice.parsers.util import generate_t1_t4_hashes, get_t1_t4_partial_hash_members

m4 = [
    TanfDataReportSchema(
        record_type="M4",
        model=SSP_M4,
        generate_hashes_func=generate_t1_t4_hashes,
        get_partial_hash_members_func=get_t1_t4_partial_hash_members,
        preparsing_validators=[
            category1.recordHasLengthBetween(34, 66),
            category1.caseNumberNotEmpty(8, 19),
            category1.or_priority_validators([
                category1.validate_fieldYearMonth_with_headerYearQuarter(),
                category1.validateRptMonthYear(),
            ]),
        ],
        postparsing_validators=[],
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
                item="3",
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
                item="5",
                name="CASE_NUMBER",
                friendly_name="Case Number",
                type=FieldType.ALPHA_NUMERIC,
                startIndex=8,
                endIndex=19,
                required=True,
                validators=[category2.isNotEmpty()],
            ),
            TransformField(
                zero_pad(3),
                item="2",
                name="COUNTY_FIPS_CODE",
                friendly_name="County FIPS code",
                type=FieldType.ALPHA_NUMERIC,
                startIndex=19,
                endIndex=22,
                required=True,
                validators=[category2.isNumber()],
            ),
            Field(
                item="4",
                name="STRATUM",
                friendly_name="Stratum",
                type=FieldType.ALPHA_NUMERIC,
                startIndex=22,
                endIndex=24,
                required=False,
                validators=[category2.isBetween(0, 99, inclusive=True, cast=int)],
            ),
            Field(
                item="6",
                name="ZIP_CODE",
                friendly_name="ZIP Code",
                type=FieldType.ALPHA_NUMERIC,
                startIndex=24,
                endIndex=29,
                required=True,
                validators=[category2.isBetween(0, 99999, inclusive=True, cast=int)],
            ),
            Field(
                item="7",
                name="DISPOSITION",
                friendly_name="Disposition",
                type=FieldType.NUMERIC,
                startIndex=29,
                endIndex=30,
                required=True,
                validators=[category2.isEqual(1)],
            ),
            Field(
                item="8",
                name="CLOSURE_REASON",
                friendly_name="Reason for Closure",
                type=FieldType.ALPHA_NUMERIC,
                startIndex=30,
                endIndex=32,
                required=True,
                validators=[
                    category3.orValidators([
                        category3.isBetween(1, 19, inclusive=True, cast=int),
                        category3.isEqual("99")
                    ])
                ],
            ),
            Field(
                item="9",
                name="REC_SUB_HOUSING",
                friendly_name="Received Subsidized Housing",
                type=FieldType.NUMERIC,
                startIndex=32,
                endIndex=33,
                required=True,
                validators=[category2.isBetween(1, 2, inclusive=True)],
            ),
            Field(
                item="10`",
                name="REC_MED_ASSIST",
                friendly_name="Received Medical Assistance",
                type=FieldType.NUMERIC,
                startIndex=33,
                endIndex=34,
                required=True,
                validators=[category2.isBetween(1, 2, inclusive=True)],
            ),
            Field(
                item="11",
                name="REC_FOOD_STAMPS",
                friendly_name="Received SNAP Assistance",
                type=FieldType.NUMERIC,
                startIndex=34,
                endIndex=35,
                required=True,
                validators=[category2.isBetween(1, 2, inclusive=True)],
            ),
            Field(
                item="12",
                name="REC_SUB_CC",
                friendly_name="Received Subsidized Child Care",
                type=FieldType.NUMERIC,
                startIndex=35,
                endIndex=36,
                required=True,
                validators=[category2.isBetween(1, 2, inclusive=True)],
            ),
            Field(
                item="-1",
                name="BLANK",
                friendly_name="blank",
                type=FieldType.ALPHA_NUMERIC,
                startIndex=36,
                endIndex=66,
                required=False,
                validators=[],
            ),
        ],
    )
]
