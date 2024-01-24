"""Schema for HEADER row of all submission types."""


from tdpservice.parsers.util import SchemaManager
from tdpservice.parsers.fields import Field
from tdpservice.parsers.row_schema import RowSchema
from tdpservice.parsers import validators
from tdpservice.search_indexes.documents.tanf import TANF_T4DataSubmissionDocument


t4 = SchemaManager(
    schemas=[
        RowSchema(
            document=TANF_T4DataSubmissionDocument(),
            preparsing_validators=[
                validators.hasLength(71),
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
                    item="4",
                    name="RPT_MONTH_YEAR",
                    friendly_name="reporting month and year",
                    type="number",
                    startIndex=2,
                    endIndex=8,
                    required=True,
                    validators=[
                        validators.dateYearIsLargerThan(1998),
                        validators.dateMonthIsValid(),
                    ],
                ),
                Field(
                    item="6",
                    name="CASE_NUMBER",
                    friendly_name="case number",
                    type="string",
                    startIndex=8,
                    endIndex=19,
                    required=True,
                    validators=[validators.isAlphaNumeric()],
                ),
                Field(
                    item="2",
                    name="COUNTY_FIPS_CODE",
                    friendly_name="county fips code",
                    type="string",
                    startIndex=19,
                    endIndex=22,
                    required=True,
                    validators=[validators.isInStringRange(1, 999)],
                ),
                Field(
                    item="5",
                    name="STRATUM",
                    friendly_name="stratum",
                    type="string",
                    startIndex=22,
                    endIndex=24,
                    required=True,
                    validators=[validators.isInStringRange(0, 99)],
                ),
                Field(
                    item="7",
                    name="ZIP_CODE",
                    friendly_name="zip code",
                    type="string",
                    startIndex=24,
                    endIndex=29,
                    required=True,
                    validators=[],
                ),
                Field(
                    item="8",
                    name="DISPOSITION",
                    friendly_name="disposition",
                    type="number",
                    startIndex=29,
                    endIndex=30,
                    required=True,
                    validators=[validators.oneOf([1, 2])],
                ),
                Field(
                    item="9",
                    name="CLOSURE_REASON",
                    friendly_name="closure reason",
                    type="string",
                    startIndex=30,
                    endIndex=32,
                    required=True,
                    validators=[
                        validators.or_validators(
                            validators.isInStringRange(1, 19),
                            validators.matches("99")
                        )
                    ],
                ),
                Field(
                    item="10",
                    name="REC_SUB_HOUSING",
                    friendly_name="receives subsidized housing",
                    type="number",
                    startIndex=32,
                    endIndex=33,
                    required=True,
                    validators=[validators.isInLimits(1, 3)],
                ),
                Field(
                    item="11",
                    name="REC_MED_ASSIST",
                    friendly_name="receives medical assistance",
                    type="number",
                    startIndex=33,
                    endIndex=34,
                    required=True,
                    validators=[validators.isInLimits(1, 2)],
                ),
                Field(
                    item="12",
                    name="REC_FOOD_STAMPS",
                    friendly_name="receives food stamps",
                    type="number",
                    startIndex=34,
                    endIndex=35,
                    required=True,
                    validators=[validators.isInLimits(1, 2)],
                ),
                Field(
                    item="13",
                    name="REC_SUB_CC",
                    friendly_name="receives subsidized child care",
                    type="number",
                    startIndex=35,
                    endIndex=36,
                    required=True,
                    validators=[validators.isInLimits(1, 3)],
                ),
                Field(
                    item="14",
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
)
