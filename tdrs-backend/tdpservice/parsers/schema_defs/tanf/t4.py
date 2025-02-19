"""Schema for HEADER row of all submission types."""

from tdpservice.parsers.transforms import zero_pad
from tdpservice.parsers.fields import Field, TransformField
from tdpservice.parsers.row_schema import TanfDataReportSchema
from tdpservice.parsers.validators import category1, category2, category3
from tdpservice.search_indexes.documents.tanf import TANF_T4DataSubmissionDocument
from tdpservice.parsers.util import generate_t1_t4_hashes, get_t1_t4_partial_hash_members


t4 = [
    TanfDataReportSchema(
        record_type="T4",
        document=TANF_T4DataSubmissionDocument(),
        generate_hashes_func=generate_t1_t4_hashes,
        get_partial_hash_members_func=get_t1_t4_partial_hash_members,
        preparsing_validators=[
            category1.recordHasLengthBetween(36, 71),
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
                type="string",
                startIndex=0,
                endIndex=2,
                required=True,
                validators=[],
            ),
            Field(
                item="4",
                name="RPT_MONTH_YEAR",
                friendly_name="Reporting Year and Month",
                type="number",
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
                type="string",
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
                type="string",
                startIndex=19,
                endIndex=22,
                required=True,
                validators=[category2.isNumber()],
            ),
            Field(
                item="5",
                name="STRATUM",
                friendly_name="Stratum",
                type="string",
                startIndex=22,
                endIndex=24,
                required=False,
                validators=[category2.isBetween(0, 99, inclusive=True, cast=int)],
            ),
            Field(
                item="7",
                name="ZIP_CODE",
                friendly_name="ZIP Code",
                type="string",
                startIndex=24,
                endIndex=29,
                required=True,
                validators=[],
            ),
            Field(
                item="8",
                name="DISPOSITION",
                friendly_name="Disposition",
                type="number",
                startIndex=29,
                endIndex=30,
                required=True,
                validators=[category2.isOneOf([1, 2])],
            ),
            Field(
                item="9",
                name="CLOSURE_REASON",
                friendly_name="Reason for Closure",
                type="string",
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
                item="10",
                name="REC_SUB_HOUSING",
                friendly_name="Received Subsidized Housing",
                type="number",
                startIndex=32,
                endIndex=33,
                required=True,
                validators=[category2.isBetween(1, 2, inclusive=True)],
            ),
            Field(
                item="11",
                name="REC_MED_ASSIST",
                friendly_name="Received Medical Assistance",
                type="number",
                startIndex=33,
                endIndex=34,
                required=True,
                validators=[category2.isBetween(1, 2, inclusive=True)],
            ),
            Field(
                item="12",
                name="REC_FOOD_STAMPS",
                friendly_name="Received SNAP Assistance",
                type="number",
                startIndex=34,
                endIndex=35,
                required=True,
                validators=[category2.isBetween(1, 2, inclusive=True)],
            ),
            Field(
                item="13",
                name="REC_SUB_CC",
                friendly_name="Received Subsidized Child Care",
                type="number",
                startIndex=35,
                endIndex=36,
                required=True,
                validators=[category2.isBetween(1, 3, inclusive=True)],
            ),
            Field(
                item="-1",
                name="BLANK",
                friendly_name="blank",
                type="string",
                startIndex=36,
                endIndex=71,
                required=False,
                validators=[],
            ),
        ],
    )
]
