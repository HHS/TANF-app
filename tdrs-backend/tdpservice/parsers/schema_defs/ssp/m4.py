"""Schema for SSP M1 record type."""


from tdpservice.parsers.fields import Field
from tdpservice.parsers.row_schema import RowSchema, SchemaManager
from tdpservice.parsers import validators
from tdpservice.search_indexes.documents.ssp import SSP_M4DataSubmissionDocument

m4 = SchemaManager(
    schemas=[
        RowSchema(
            document=SSP_M4DataSubmissionDocument(),
            preparsing_validators=[
                validators.hasLength(66),
                validators.or_priority_validators([
                validators.field_year_month_with_header_year_quarter(),
                validators.validateRptMonthYear(),
                ]),
                validators.notEmpty(8, 19)
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
                    item="3",
                    name="RPT_MONTH_YEAR",
                    friendly_name="Reporting Year and Month",
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
                    friendly_name="Case Number",
                    type="string",
                    startIndex=8,
                    endIndex=19,
                    required=True,
                    validators=[validators.notEmpty()],
                ),
                Field(
                    item="2",
                    name="COUNTY_FIPS_CODE",
                    friendly_name="County FIPS Code",
                    type="string",
                    startIndex=19,
                    endIndex=22,
                    required=True,
                    validators=[validators.isInStringRange(0, 999)],
                ),
                Field(
                    item="4",
                    name="STRATUM",
                    friendly_name="Stratum",
                    type="string",
                    startIndex=22,
                    endIndex=24,
                    required=False,
                    validators=[validators.isInStringRange(0, 99)],
                ),
                Field(
                    item="6",
                    name="ZIP_CODE",
                    friendly_name="ZIP Code",
                    type="string",
                    startIndex=24,
                    endIndex=29,
                    required=True,
                    validators=[validators.isInStringRange(0, 99999)],
                ),
                Field(
                    item="7",
                    name="DISPOSITION",
                    friendly_name="Disposition",
                    type="number",
                    startIndex=29,
                    endIndex=30,
                    required=True,
                    validators=[validators.matches(1)],
                ),
                Field(
                    item="8",
                    name="CLOSURE_REASON",
                    friendly_name="Reason for Closure",
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
                    item="9",
                    name="REC_SUB_HOUSING",
                    friendly_name="Received Subsidized Housing",
                    type="number",
                    startIndex=32,
                    endIndex=33,
                    required=True,
                    validators=[validators.isInLimits(1, 2)],
                ),
                Field(
                    item="10`",
                    name="REC_MED_ASSIST",
                    friendly_name="Received Medical Assistance",
                    type="number",
                    startIndex=33,
                    endIndex=34,
                    required=True,
                    validators=[validators.isInLimits(1, 2)],
                ),
                Field(
                    item="11",
                    name="REC_FOOD_STAMPS",
                    friendly_name="Received Assistance from the Supplemental Nutrition Assistance Program (SNAP)",
                    type="number",
                    startIndex=34,
                    endIndex=35,
                    required=True,
                    validators=[validators.isInLimits(1, 2)],
                ),
                Field(
                    item="12",
                    name="REC_SUB_CC",
                    friendly_name="Received Subsidized Child Care",
                    type="number",
                    startIndex=35,
                    endIndex=36,
                    required=True,
                    validators=[validators.isInLimits(1, 2)],
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
