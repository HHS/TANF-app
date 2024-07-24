"""Schema for SSP M1 record type."""

from tdpservice.parsers.transforms import zero_pad
from tdpservice.parsers.fields import Field, TransformField
from tdpservice.parsers.row_schema import RowSchema, SchemaManager
from tdpservice.parsers.validators.category1 import PreparsingValidators
from tdpservice.parsers.validators.category2 import FieldValidators
from tdpservice.parsers.validators.category3 import PostparsingValidators
from tdpservice.search_indexes.documents.ssp import SSP_M4DataSubmissionDocument
from tdpservice.parsers.util import generate_t1_t4_hashes, get_t1_t4_partial_hash_members

m4 = SchemaManager(
    schemas=[
        RowSchema(
            record_type="M4",
            document=SSP_M4DataSubmissionDocument(),
            generate_hashes_func=generate_t1_t4_hashes,
            get_partial_hash_members_func=get_t1_t4_partial_hash_members,
            preparsing_validators=[
                PreparsingValidators.recordHasLengthBetween(34, 66),
                PreparsingValidators.caseNumberNotEmpty(8, 19),
                PreparsingValidators.or_priority_validators([
                    PreparsingValidators.validate_fieldYearMonth_with_headerYearQuarter(),
                    PreparsingValidators.validateRptMonthYear(),
                ]),
            ],
            postparsing_validators=[],
            fields=[
                Field(
                    item="0",
                    name="RecordType",
                    friendly_name="record type",
                    type="string",
                    startIndex=0,
                    endIndex=2,
                    required=True,
                    validators=[],
                ),
                Field(
                    item="3",
                    name="RPT_MONTH_YEAR",
                    friendly_name="reporting month and year",
                    type="number",
                    startIndex=2,
                    endIndex=8,
                    required=True,
                    validators=[
                        FieldValidators.dateYearIsLargerThan(1998),
                        FieldValidators.dateMonthIsValid(),
                    ],
                ),
                Field(
                    item="5",
                    name="CASE_NUMBER",
                    friendly_name="case number",
                    type="string",
                    startIndex=8,
                    endIndex=19,
                    required=True,
                    validators=[FieldValidators.isNotEmpty()],
                ),
                TransformField(
                    zero_pad(3),
                    item="2",
                    name="COUNTY_FIPS_CODE",
                    friendly_name="county fips code",
                    type="string",
                    startIndex=19,
                    endIndex=22,
                    required=True,
                    validators=[FieldValidators.isNumber()],
                ),
                Field(
                    item="4",
                    name="STRATUM",
                    friendly_name="stratum",
                    type="string",
                    startIndex=22,
                    endIndex=24,
                    required=False,
                    validators=[FieldValidators.isBetween(0, 99, inclusive=True, cast=int)],
                ),
                Field(
                    item="6",
                    name="ZIP_CODE",
                    friendly_name="zip code",
                    type="string",
                    startIndex=24,
                    endIndex=29,
                    required=True,
                    validators=[FieldValidators.isBetween(0, 99999, inclusive=True, cast=int)],
                ),
                Field(
                    item="7",
                    name="DISPOSITION",
                    friendly_name="disposition",
                    type="number",
                    startIndex=29,
                    endIndex=30,
                    required=True,
                    validators=[FieldValidators.isEqual(1)],
                ),
                Field(
                    item="8",
                    name="CLOSURE_REASON",
                    friendly_name="closure reason",
                    type="string",
                    startIndex=30,
                    endIndex=32,
                    required=True,
                    validators=[
                        FieldValidators.or_validators(
                            FieldValidators.isBetween(1, 19, inclusive=True, cast=int),
                            FieldValidators.isEqual("99")
                        )
                    ],
                ),
                Field(
                    item="9",
                    name="REC_SUB_HOUSING",
                    friendly_name="receives subsidized housing",
                    type="number",
                    startIndex=32,
                    endIndex=33,
                    required=True,
                    validators=[FieldValidators.isBetween(1, 2, inclusive=True)],
                ),
                Field(
                    item="10`",
                    name="REC_MED_ASSIST",
                    friendly_name="receives medical assistance",
                    type="number",
                    startIndex=33,
                    endIndex=34,
                    required=True,
                    validators=[FieldValidators.isBetween(1, 2, inclusive=True)],
                ),
                Field(
                    item="11",
                    name="REC_FOOD_STAMPS",
                    friendly_name="receives food stamps",
                    type="number",
                    startIndex=34,
                    endIndex=35,
                    required=True,
                    validators=[FieldValidators.isBetween(1, 2, inclusive=True)],
                ),
                Field(
                    item="12",
                    name="REC_SUB_CC",
                    friendly_name="receives subsidized child care",
                    type="number",
                    startIndex=35,
                    endIndex=36,
                    required=True,
                    validators=[FieldValidators.isBetween(1, 2, inclusive=True)],
                ),
                Field(
                    item="-1",
                    name="BLANK",
                    friendly_name="blank",
                    type="string",
                    startIndex=36,
                    endIndex=66,
                    required=False,
                    validators=[],
                ),
            ],
        )
    ]
)
