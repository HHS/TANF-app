"""Schema for SSP M1 record type."""


from tdpservice.parsers.util import SchemaManager
from tdpservice.parsers.fields import Field
from tdpservice.parsers.row_schema import RowSchema
from tdpservice.parsers import validators
from tdpservice.search_indexes.models.ssp import SSP_M4

m4 = SchemaManager(
    schemas=[
        RowSchema(
            model=SSP_M4,
            preparsing_validators=[
                validators.hasLength(66),
            ],
            postparsing_validators=[],
            fields=[
                Field(
                    item="0",
                    name="RecordType",
                    type="string",
                    startIndex=0,
                    endIndex=2,
                    required=True,
                    validators=[],
                ),
                Field(
                    item="3",
                    name="RPT_MONTH_YEAR",
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
                    item="5",
                    name="CASE_NUMBER",
                    type="string",
                    startIndex=8,
                    endIndex=19,
                    required=True,
                    validators=[validators.isAlphaNumeric()],
                ),
                Field(
                    item="2",
                    name="COUNTY_FIPS_CODE",
                    type="string",
                    startIndex=19,
                    endIndex=22,
                    required=True,
                    validators=[validators.isInStringRange(0, 999)],
                ),
                Field(
                    item="4",
                    name="STRATUM",
                    type="string",
                    startIndex=22,
                    endIndex=24,
                    required=False,
                    validators=[validators.isInStringRange(0, 99)],
                ),
                Field(
                    item="6",
                    name="ZIP_CODE",
                    type="string",
                    startIndex=24,
                    endIndex=29,
                    required=True,
                    validators=[validators.isInStringRange(0, 99999)],
                ),
                Field(
                    item="7",
                    name="DISPOSITION",
                    type="number",
                    startIndex=29,
                    endIndex=30,
                    required=True,
                    validators=[validators.matches(1)],
                ),
                Field(
                    item="8",
                    name="CLOSURE_REASON",
                    type="string",
                    startIndex=30,
                    endIndex=32,
                    required=True,
                    validators=[
                        validators.or_validators(
                            validators.isInStringRange(1, 19), validators.matches("99")
                        )
                    ],
                ),
                Field(
                    item="9",
                    name="REC_SUB_HOUSING",
                    type="number",
                    startIndex=32,
                    endIndex=33,
                    required=True,
                    validators=[validators.isInLimits(1, 2)],
                ),
                Field(
                    item="10`",
                    name="REC_MED_ASSIST",
                    type="number",
                    startIndex=33,
                    endIndex=34,
                    required=True,
                    validators=[validators.isInLimits(1, 2)],
                ),
                Field(
                    item="11",
                    name="REC_FOOD_STAMPS",
                    type="number",
                    startIndex=34,
                    endIndex=35,
                    required=True,
                    validators=[validators.isInLimits(1, 2)],
                ),
                Field(
                    item="12",
                    name="REC_SUB_CC",
                    type="number",
                    startIndex=35,
                    endIndex=36,
                    required=True,
                    validators=[validators.isInLimits(1, 2)],
                ),
                Field(
                    item="-1",
                    name="BLANK",
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
