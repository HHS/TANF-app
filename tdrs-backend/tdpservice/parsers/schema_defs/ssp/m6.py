"""Schema for HEADER row of all submission types."""


from ...transforms import calendar_quarter_to_rpt_month_year
from ...fields import Field, TransformField
from ...row_schema import RowSchema, SchemaManager
from ... import validators
from tdpservice.search_indexes.documents.ssp import SSP_M6DataSubmissionDocument

s1 = RowSchema(
    document=SSP_M6DataSubmissionDocument(),
    preparsing_validators=[
        validators.recordHasLength(259, "M6"),
    ],
    postparsing_validators=[
        validators.sumIsEqual(
            "SSPMOE_FAMILIES", [
                "NUM_2_PARENTS",
                "NUM_1_PARENTS",
                "NUM_NO_PARENTS"
            ]
        ),
        validators.sumIsEqual(
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
            friendly_name='record type',
            type='string',
            startIndex=0,
            endIndex=2,
            required=True,
            validators=[]
        ),
        Field(
            item="2",
            name='CALENDAR_QUARTER',
            friendly_name='calendar quarter',
            type='number',
            startIndex=2,
            endIndex=7,
            required=True,
            validators=[
                validators.dateYearIsLargerThan(1998),
                validators.quarterIsValid()
            ]
        ),
        TransformField(
            calendar_quarter_to_rpt_month_year(0),
            item="2B",
            name='RPT_MONTH_YEAR',
            friendly_name='reporting month and year',
            type='number',
            startIndex=2,
            endIndex=7,
            required=True,
            validators=[
                validators.dateYearIsLargerThan(1998),
                validators.dateMonthIsValid()
            ]
        ),
        Field(
            item="3A",
            name='SSPMOE_FAMILIES',
            friendly_name='ssp/moe families',
            type='number',
            startIndex=7,
            endIndex=15,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="4A",
            name='NUM_2_PARENTS',
            friendly_name='number of two-parent families',
            type='number',
            startIndex=31,
            endIndex=39,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="5A",
            name='NUM_1_PARENTS',
            friendly_name='number of one-parent families',
            type='number',
            startIndex=55,
            endIndex=63,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="6A",
            name='NUM_NO_PARENTS',
            friendly_name='number of no-parent families',
            type='number',
            startIndex=79,
            endIndex=87,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="7A",
            name='NUM_RECIPIENTS',
            friendly_name='number of recipients',
            type='number',
            startIndex=103,
            endIndex=111,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="8A",
            name='ADULT_RECIPIENTS',
            friendly_name='number of adult recipients',
            type='number',
            startIndex=127,
            endIndex=135,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="9A",
            name='CHILD_RECIPIENTS',
            friendly_name='number of child recipients',
            type='number',
            startIndex=151,
            endIndex=159,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="10A",
            name='NONCUSTODIALS',
            friendly_name='number of noncustodial parents',
            type='number',
            startIndex=175,
            endIndex=183,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="11A",
            name='AMT_ASSISTANCE',
            friendly_name='amount of assistance',
            type='number',
            startIndex=199,
            endIndex=211,
            required=True,
            validators=[validators.isInLimits(0, 999999999999)]
        ),
        Field(
            item="12A",
            name='CLOSED_CASES',
            friendly_name='number of closed cases',
            type='number',
            startIndex=235,
            endIndex=243,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
    ],
)

s2 = RowSchema(
    document=SSP_M6DataSubmissionDocument(),
    preparsing_validators=[
        validators.recordHasLength(259, "M6"),
    ],
    postparsing_validators=[
        validators.sumIsEqual(
            "SSPMOE_FAMILIES", [
                "NUM_2_PARENTS",
                "NUM_1_PARENTS",
                "NUM_NO_PARENTS"
            ]
        ),
        validators.sumIsEqual(
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
            friendly_name='record type',
            type='string',
            startIndex=0,
            endIndex=2,
            required=True,
            validators=[]
        ),
        Field(
            item="2",
            name='CALENDAR_QUARTER',
            friendly_name='calendar quarter',
            type='number',
            startIndex=2,
            endIndex=7,
            required=True,
            validators=[
                validators.dateYearIsLargerThan(1998),
                validators.quarterIsValid()
            ]
        ),
        TransformField(
            calendar_quarter_to_rpt_month_year(1),
            item="2B",
            name='RPT_MONTH_YEAR',
            friendly_name='reporting month and year',
            type='number',
            startIndex=2,
            endIndex=7,
            required=True,
            validators=[
                validators.dateYearIsLargerThan(1998),
                validators.dateMonthIsValid()
            ]
        ),
        Field(
            item="3B",
            name='SSPMOE_FAMILIES',
            friendly_name='ssp/moe families',
            type='number',
            startIndex=15,
            endIndex=23,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="4B",
            name='NUM_2_PARENTS',
            friendly_name='number of two-parent families',
            type='number',
            startIndex=39,
            endIndex=47,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="5B",
            name='NUM_1_PARENTS',
            friendly_name='number of one-parent families',
            type='number',
            startIndex=63,
            endIndex=71,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="6B",
            name='NUM_NO_PARENTS',
            friendly_name='number of no-parent families',
            type='number',
            startIndex=87,
            endIndex=95,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="7B",
            name='NUM_RECIPIENTS',
            friendly_name='number of recipients',
            type='number',
            startIndex=111,
            endIndex=119,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="8B",
            name='ADULT_RECIPIENTS',
            friendly_name='number of adult recipients',
            type='number',
            startIndex=135,
            endIndex=143,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="9B",
            name='CHILD_RECIPIENTS',
            friendly_name='number of child recipients',
            type='number',
            startIndex=159,
            endIndex=167,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="10B",
            name='NONCUSTODIALS',
            friendly_name='number of noncustodial parents',
            type='number',
            startIndex=183,
            endIndex=191,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="11B",
            name='AMT_ASSISTANCE',
            friendly_name='amount of assistance',
            type='number',
            startIndex=211,
            endIndex=223,
            required=True,
            validators=[validators.isInLimits(0, 999999999999)]
        ),
        Field(
            item="12B",
            name='CLOSED_CASES',
            friendly_name='number of closed cases',
            type='number',
            startIndex=243,
            endIndex=251,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
    ],
)

s3 = RowSchema(
    document=SSP_M6DataSubmissionDocument(),
    preparsing_validators=[
        validators.recordHasLength(259, "M6"),
    ],
    postparsing_validators=[
        validators.sumIsEqual(
            "SSPMOE_FAMILIES", [
                "NUM_2_PARENTS",
                "NUM_1_PARENTS",
                "NUM_NO_PARENTS"
            ]
        ),
        validators.sumIsEqual(
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
            friendly_name='record type',
            type='string',
            startIndex=0,
            endIndex=2,
            required=True,
            validators=[]
        ),
        Field(
            item="2",
            name='CALENDAR_QUARTER',
            friendly_name='calendar quarter',
            type='number',
            startIndex=2,
            endIndex=7,
            required=True,
            validators=[
                validators.dateYearIsLargerThan(1998),
                validators.quarterIsValid()
            ]
        ),
        TransformField(
            calendar_quarter_to_rpt_month_year(2),
            item="2B",
            name='RPT_MONTH_YEAR',
            friendly_name='reporting month and year',
            type='number',
            startIndex=2,
            endIndex=7,
            required=True,
            validators=[
                validators.dateYearIsLargerThan(1998),
                validators.dateMonthIsValid()
            ]
        ),
        Field(
            item="3C",
            name='SSPMOE_FAMILIES',
            friendly_name='ssp/moe families',
            type='number',
            startIndex=23,
            endIndex=31,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="4C",
            name='NUM_2_PARENTS',
            friendly_name='number of two-parent families',
            type='number',
            startIndex=47,
            endIndex=55,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="5C",
            name='NUM_1_PARENTS',
            friendly_name='number of one-parent families',
            type='number',
            startIndex=71,
            endIndex=79,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="6C",
            name='NUM_NO_PARENTS',
            friendly_name='number of no-parent families',
            type='number',
            startIndex=95,
            endIndex=103,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="7C",
            name='NUM_RECIPIENTS',
            friendly_name='number of recipients',
            type='number',
            startIndex=119,
            endIndex=127,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="8C",
            name='ADULT_RECIPIENTS',
            friendly_name='number of adult recipients',
            type='number',
            startIndex=143,
            endIndex=151,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="9C",
            name='CHILD_RECIPIENTS',
            friendly_name='number of child recipients',
            type='number',
            startIndex=167,
            endIndex=175,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="10C",
            name='NONCUSTODIALS',
            friendly_name='number of noncustodial parents',
            type='number',
            startIndex=191,
            endIndex=199,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
        Field(
            item="11C",
            name='AMT_ASSISTANCE',
            friendly_name='amount of assistance',
            type='number',
            startIndex=223,
            endIndex=235,
            required=True,
            validators=[validators.isInLimits(0, 999999999999)]
        ),
        Field(
            item="12C",
            name='CLOSED_CASES',
            friendly_name='number of closed cases',
            type='number',
            startIndex=251,
            endIndex=259,
            required=True,
            validators=[validators.isInLimits(0, 99999999)]
        ),
    ],
)


m6 = SchemaManager(schemas=[s1, s2, s3])
