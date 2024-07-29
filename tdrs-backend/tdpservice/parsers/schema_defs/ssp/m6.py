"""Schema for HEADER row of all submission types."""


from tdpservice.parsers.transforms import calendar_quarter_to_rpt_month_year
from tdpservice.parsers.fields import Field, TransformField
from tdpservice.parsers.row_schema import RowSchema, SchemaManager
from tdpservice.parsers.validators.category1 import PreparsingValidators
from tdpservice.parsers.validators.category2 import FieldValidators
from tdpservice.parsers.validators.category3 import ComposableValidators
from tdpservice.search_indexes.documents.ssp import SSP_M6DataSubmissionDocument

s1 = RowSchema(
    record_type="M6",
    document=SSP_M6DataSubmissionDocument(),
    preparsing_validators=[
        PreparsingValidators.recordHasLength(259),
        PreparsingValidators.validate_fieldYearMonth_with_headerYearQuarter(),
        PreparsingValidators.calendarQuarterIsValid(2, 7),
    ],
    postparsing_validators=[
        ComposableValidators.sumIsEqual(
            "SSPMOE_FAMILIES", [
                "NUM_2_PARENTS",
                "NUM_1_PARENTS",
                "NUM_NO_PARENTS"
            ]
        ),
        ComposableValidators.sumIsEqual(
            "NUM_RECIPIENTS", [
                "ADULT_RECIPIENTS",
                "CHILD_RECIPIENTS"
            ]
        ),
    ],
    fields=[
        Field(
            item="0",
            name='RecordType',
            friendly_name='Record Type',
            type='string',
            startIndex=0,
            endIndex=2,
            required=True,
            validators=[]
        ),
        Field(
            item="2",
            name='CALENDAR_QUARTER',
            friendly_name='Calendar Quarter',
            type='number',
            startIndex=2,
            endIndex=7,
            required=True,
            validators=[
                FieldValidators.dateYearIsLargerThan(2020),
                FieldValidators.quarterIsValid()
            ]
        ),
        TransformField(
            calendar_quarter_to_rpt_month_year(0),
            item="2B",
            name='RPT_MONTH_YEAR',
            friendly_name='Reporting Year and Month',
            type='number',
            startIndex=2,
            endIndex=7,
            required=True,
            validators=[
                FieldValidators.dateYearIsLargerThan(1998),
                FieldValidators.dateMonthIsValid()
            ]
        ),
        Field(
            item="3A",
            name='SSPMOE_FAMILIES',
            friendly_name='SSP-MOE Families',
            type='number',
            startIndex=7,
            endIndex=15,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="4A",
            name='NUM_2_PARENTS',
            friendly_name='SSP-MOE Two-Parent Families',
            type='number',
            startIndex=31,
            endIndex=39,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="5A",
            name='NUM_1_PARENTS',
            friendly_name='SSP-MOE One-Parent Families',
            type='number',
            startIndex=55,
            endIndex=63,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="6A",
            name='NUM_NO_PARENTS',
            friendly_name='SSP-MOE No-Parent Families',
            type='number',
            startIndex=79,
            endIndex=87,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="7A",
            name='NUM_RECIPIENTS',
            friendly_name='SSP-MOE Recipient',
            type='number',
            startIndex=103,
            endIndex=111,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="8A",
            name='ADULT_RECIPIENTS',
            friendly_name='SSP-MOE Adult Recipients',
            type='number',
            startIndex=127,
            endIndex=135,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="9A",
            name='CHILD_RECIPIENTS',
            friendly_name='SSP-MOE Child Recipients',
            type='number',
            startIndex=151,
            endIndex=159,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="10A",
            name='NONCUSTODIALS',
            friendly_name='Total Number of Noncustodial Parents Participating in Work Activities',
            type='number',
            startIndex=175,
            endIndex=183,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="11A",
            name='AMT_ASSISTANCE',
            friendly_name='SSP-MOE Amount of Assistance',
            type='number',
            startIndex=199,
            endIndex=211,
            required=True,
            validators=[FieldValidators.isBetween(0, 999999999999, inclusive=True)]
        ),
        Field(
            item="12A",
            name='CLOSED_CASES',
            friendly_name='SSP-MOE Number of Closed Cases',
            type='number',
            startIndex=235,
            endIndex=243,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
    ],
)

s2 = RowSchema(
    record_type="M6",
    document=SSP_M6DataSubmissionDocument(),
    quiet_preparser_errors=True,
    preparsing_validators=[
        PreparsingValidators.recordHasLength(259),
        PreparsingValidators.validate_fieldYearMonth_with_headerYearQuarter(),
        PreparsingValidators.calendarQuarterIsValid(2, 7),
    ],
    postparsing_validators=[
        ComposableValidators.sumIsEqual(
            "SSPMOE_FAMILIES", [
                "NUM_2_PARENTS",
                "NUM_1_PARENTS",
                "NUM_NO_PARENTS"
            ]
        ),
        ComposableValidators.sumIsEqual(
            "NUM_RECIPIENTS", [
                "ADULT_RECIPIENTS",
                "CHILD_RECIPIENTS"
            ]
        ),
    ],
    fields=[
        Field(
            item="0",
            name='RecordType',
            friendly_name='Record Type',
            type='string',
            startIndex=0,
            endIndex=2,
            required=True,
            validators=[]
        ),
        Field(
            item="2",
            name='CALENDAR_QUARTER',
            friendly_name='Calendar Quarter',
            type='number',
            startIndex=2,
            endIndex=7,
            required=True,
            validators=[
                FieldValidators.dateYearIsLargerThan(2020),
                FieldValidators.quarterIsValid()
            ]
        ),
        TransformField(
            calendar_quarter_to_rpt_month_year(1),
            item="2B",
            name='RPT_MONTH_YEAR',
            friendly_name='Reporting Year and Month',
            type='number',
            startIndex=2,
            endIndex=7,
            required=True,
            validators=[
                FieldValidators.dateYearIsLargerThan(1998),
                FieldValidators.dateMonthIsValid()
            ]
        ),
        Field(
            item="3B",
            name='SSPMOE_FAMILIES',
            friendly_name='SSP-MOE Families',
            type='number',
            startIndex=15,
            endIndex=23,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="4B",
            name='NUM_2_PARENTS',
            friendly_name='SSP-MOE Two-Parent Families',
            type='number',
            startIndex=39,
            endIndex=47,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="5B",
            name='NUM_1_PARENTS',
            friendly_name='SSP-MOE One-Parent Families',
            type='number',
            startIndex=63,
            endIndex=71,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="6B",
            name='NUM_NO_PARENTS',
            friendly_name='SSP-MOE No-Parent Families',
            type='number',
            startIndex=87,
            endIndex=95,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="7B",
            name='NUM_RECIPIENTS',
            friendly_name='SSP-MOE Recipients',
            type='number',
            startIndex=111,
            endIndex=119,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="8B",
            name='ADULT_RECIPIENTS',
            friendly_name='SSP-MOE Adult Recipients',
            type='number',
            startIndex=135,
            endIndex=143,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="9B",
            name='CHILD_RECIPIENTS',
            friendly_name='SSP-MOE Child Recipients',
            type='number',
            startIndex=159,
            endIndex=167,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="10B",
            name='NONCUSTODIALS',
            friendly_name='SSP-MOE Noncustodial Parents Participating in Work Activities',
            type='number',
            startIndex=183,
            endIndex=191,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="11B",
            name='AMT_ASSISTANCE',
            friendly_name='SSP-MOE Amount of Assistance',
            type='number',
            startIndex=211,
            endIndex=223,
            required=True,
            validators=[FieldValidators.isBetween(0, 999999999999, inclusive=True)]
        ),
        Field(
            item="12B",
            name='CLOSED_CASES',
            friendly_name='SSP-MOE Number of Closed Cases',
            type='number',
            startIndex=243,
            endIndex=251,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
    ],
)

s3 = RowSchema(
    record_type="M6",
    document=SSP_M6DataSubmissionDocument(),
    quiet_preparser_errors=True,
    preparsing_validators=[
        PreparsingValidators.recordHasLength(259),
        PreparsingValidators.validate_fieldYearMonth_with_headerYearQuarter(),
        PreparsingValidators.calendarQuarterIsValid(2, 7),
    ],
    postparsing_validators=[
        ComposableValidators.sumIsEqual(
            "SSPMOE_FAMILIES", [
                "NUM_2_PARENTS",
                "NUM_1_PARENTS",
                "NUM_NO_PARENTS"
            ]
        ),
        ComposableValidators.sumIsEqual(
            "NUM_RECIPIENTS", [
                "ADULT_RECIPIENTS",
                "CHILD_RECIPIENTS"
            ]
        ),
    ],
    fields=[
        Field(
            item="0",
            name='RecordType',
            friendly_name='Record Type',
            type='string',
            startIndex=0,
            endIndex=2,
            required=True,
            validators=[]
        ),
        Field(
            item="2",
            name='CALENDAR_QUARTER',
            friendly_name='Calendar Quarter',
            type='number',
            startIndex=2,
            endIndex=7,
            required=True,
            validators=[
                FieldValidators.dateYearIsLargerThan(2020),
                FieldValidators.quarterIsValid()
            ]
        ),
        TransformField(
            calendar_quarter_to_rpt_month_year(2),
            item="2B",
            name='RPT_MONTH_YEAR',
            friendly_name='Reporting Year and Month',
            type='number',
            startIndex=2,
            endIndex=7,
            required=True,
            validators=[
                FieldValidators.dateYearIsLargerThan(1998),
                FieldValidators.dateMonthIsValid()
            ]
        ),
        Field(
            item="3C",
            name='SSPMOE_FAMILIES',
            friendly_name='SSP-MOE Families',
            type='number',
            startIndex=23,
            endIndex=31,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="4C",
            name='NUM_2_PARENTS',
            friendly_name='SSP-MOE Two-Parent Families',
            type='number',
            startIndex=47,
            endIndex=55,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="5C",
            name='NUM_1_PARENTS',
            friendly_name='SSP-MOE One-Parent Families',
            type='number',
            startIndex=71,
            endIndex=79,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="6C",
            name='NUM_NO_PARENTS',
            friendly_name='SSP-MOE No-Parent Families',
            type='number',
            startIndex=95,
            endIndex=103,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="7C",
            name='NUM_RECIPIENTS',
            friendly_name='SSP-MOE Recipients',
            type='number',
            startIndex=119,
            endIndex=127,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="8C",
            name='ADULT_RECIPIENTS',
            friendly_name='SSP-MOE Adult Recipients',
            type='number',
            startIndex=143,
            endIndex=151,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="9C",
            name='CHILD_RECIPIENTS',
            friendly_name='SSP-MOE Child Recipients',
            type='number',
            startIndex=167,
            endIndex=175,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="10C",
            name='NONCUSTODIALS',
            friendly_name='SSP-MOE Noncustodial Parents Participating in Work Activities',
            type='number',
            startIndex=191,
            endIndex=199,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
        Field(
            item="11C",
            name='AMT_ASSISTANCE',
            friendly_name='SSP-MOE Amount of Assistance',
            type='number',
            startIndex=223,
            endIndex=235,
            required=True,
            validators=[FieldValidators.isBetween(0, 999999999999, inclusive=True)]
        ),
        Field(
            item="12C",
            name='CLOSED_CASES',
            friendly_name='SSP-MOE Number of Closed Cases',
            type='number',
            startIndex=251,
            endIndex=259,
            required=True,
            validators=[FieldValidators.isBetween(0, 99999999, inclusive=True)]
        ),
    ],
)


m6 = SchemaManager(schemas=[s1, s2, s3])
