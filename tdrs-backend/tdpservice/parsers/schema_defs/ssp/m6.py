"""Schema for HEADER row of all submission types."""


from ...util import SchemaManager
from ...transforms import calendar_quarter_to_rpt_month_year
from ...fields import Field, TransformField
from ...row_schema import RowSchema
from ... import validators
from tdpservice.search_indexes.models.ssp import SSP_M6

s1 = RowSchema(
    model=SSP_M6,
    preparsing_validators=[
        validators.hasLength(259),
    ],
    postparsing_validators=[
        validators.sumIsEqual(
            "SSPMOE_FAMILIES", ["NUM_2_PARENTS", "NUM_1_PARENTS", "NUM_NO_PARENTS"]),
        validators.sumIsEqual(
            "NUM_RECIPIENTS", ["ADULT_RECIPIENTS", "CHILD_RECIPIENTS"]),
    ],
    fields=[
        Field(item="0", name='RecordType', type='string', startIndex=0, endIndex=2,
              friendly_name='record type', required=True, validators=[]),
        Field(item="2", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              friendly_name='calendar quarter', required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                           validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(0), item="2B", name='RPT_MONTH_YEAR', type='number',
                       friendly_name='reporting month and year',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="3A", name='SSPMOE_FAMILIES', type='number', startIndex=7, endIndex=15,
              friendly_name='ssp/moe families',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="4A", name='NUM_2_PARENTS', type='number', startIndex=31, endIndex=39,
              friendly_name='number of two-parent families',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="5A", name='NUM_1_PARENTS', type='number', startIndex=55, endIndex=63,
              friendly_name='number of one-parent families',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="6A", name='NUM_NO_PARENTS', type='number', startIndex=79, endIndex=87,
              friendly_name='number of no-parent families',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="7A", name='NUM_RECIPIENTS', type='number', startIndex=103, endIndex=111,
              friendly_name='number of recipients',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="8A", name='ADULT_RECIPIENTS', type='number', startIndex=127, endIndex=135,
              friendly_name='number of adult recipients',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="9A", name='CHILD_RECIPIENTS', type='number', startIndex=151, endIndex=159,
              friendly_name='number of child recipients',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="10A", name='NONCUSTODIALS', type='number', startIndex=175, endIndex=183,
              friendly_name='number of noncustodial parents',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="11A", name='AMT_ASSISTANCE', type='number', startIndex=199, endIndex=211,
              friendly_name='amount of assistance',
              required=True, validators=[validators.isInLimits(0, 999999999999)]),
        Field(item="12A", name='CLOSED_CASES', type='number', startIndex=235, endIndex=243,
              friendly_name='number of closed cases',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
    ],
)

s2 = RowSchema(
    model=SSP_M6,
    preparsing_validators=[
        validators.hasLength(259),
    ],
    postparsing_validators=[
        validators.sumIsEqual(
            "SSPMOE_FAMILIES", ["NUM_2_PARENTS", "NUM_1_PARENTS", "NUM_NO_PARENTS"]),
        validators.sumIsEqual(
            "NUM_RECIPIENTS", ["ADULT_RECIPIENTS", "CHILD_RECIPIENTS"]),
    ],
    fields=[
        Field(item="0", name='RecordType', type='string', startIndex=0, endIndex=2,
              friendly_name='record type',
              required=True, validators=[]),
        Field(item="2", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              friendly_name='calendar quarter',
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(1), item="2B", name='RPT_MONTH_YEAR', type='number',
                       friendly_name='reporting month and year',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="3B", name='SSPMOE_FAMILIES', type='number', startIndex=15, endIndex=23,
              friendly_name='ssp/moe families',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="4B", name='NUM_2_PARENTS', type='number', startIndex=39, endIndex=47,
              friendly_name='number of two-parent families',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="5B", name='NUM_1_PARENTS', type='number', startIndex=63, endIndex=71,
              friendly_name='number of one-parent families',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="6B", name='NUM_NO_PARENTS', type='number', startIndex=87, endIndex=95,
              friendly_name='number of no-parent families',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="7B", name='NUM_RECIPIENTS', type='number', startIndex=111, endIndex=119,
              friendly_name='number of recipients',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="8B", name='ADULT_RECIPIENTS', type='number', startIndex=135, endIndex=143,
              friendly_name='number of adult recipients',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="9B", name='CHILD_RECIPIENTS', type='number', startIndex=159, endIndex=167,
              friendly_name='number of child recipients',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="10B", name='NONCUSTODIALS', type='number', startIndex=183, endIndex=191,
              friendly_name='number of noncustodial parents',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="11B", name='AMT_ASSISTANCE', type='number', startIndex=211, endIndex=223,
              friendly_name='amount of assistance',
              required=True, validators=[validators.isInLimits(0, 999999999999)]),
        Field(item="12B", name='CLOSED_CASES', type='number', startIndex=243, endIndex=251,
              friendly_name='number of closed cases',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
    ],
)

s3 = RowSchema(
    model=SSP_M6,
    preparsing_validators=[
        validators.hasLength(259),
    ],
    postparsing_validators=[
        validators.sumIsEqual(
            "SSPMOE_FAMILIES", ["NUM_2_PARENTS", "NUM_1_PARENTS", "NUM_NO_PARENTS"]),
        validators.sumIsEqual(
            "NUM_RECIPIENTS", ["ADULT_RECIPIENTS", "CHILD_RECIPIENTS"]),
    ],
    fields=[
        Field(item="0", name='RecordType', type='string', startIndex=0, endIndex=2,
              friendly_name='record type',
              required=True, validators=[]),
        Field(item="2", name='CALENDAR_QUARTER', type='number', startIndex=2, endIndex=7,
              friendly_name='calendar quarter',
              required=True, validators=[validators.dateYearIsLargerThan(1998),
                                         validators.quarterIsValid()]),
        TransformField(calendar_quarter_to_rpt_month_year(2), item="2B", name='RPT_MONTH_YEAR', type='number',
                       friendly_name='reporting month and year',
                       startIndex=2, endIndex=7, required=True, validators=[validators.dateYearIsLargerThan(1998),
                                                                            validators.dateMonthIsValid()]),
        Field(item="3C", name='SSPMOE_FAMILIES', type='number', startIndex=23, endIndex=31,
              friendly_name='ssp/moe families',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="4C", name='NUM_2_PARENTS', type='number', startIndex=47, endIndex=55,
              friendly_name='number of two-parent families',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="5C", name='NUM_1_PARENTS', type='number', startIndex=71, endIndex=79,
              friendly_name='number of one-parent families',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="6C", name='NUM_NO_PARENTS', type='number', startIndex=95, endIndex=103,
              friendly_name='number of no-parent families',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="7C", name='NUM_RECIPIENTS', type='number', startIndex=119, endIndex=127,
              friendly_name='number of recipients',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="8C", name='ADULT_RECIPIENTS', type='number', startIndex=143, endIndex=151,
              friendly_name='number of adult recipients',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="9C", name='CHILD_RECIPIENTS', type='number', startIndex=167, endIndex=175,
              friendly_name='number of child recipients',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="10C", name='NONCUSTODIALS', type='number', startIndex=191, endIndex=199,
              friendly_name='number of noncustodial parents',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
        Field(item="11C", name='AMT_ASSISTANCE', type='number', startIndex=223, endIndex=235,
              friendly_name='amount of assistance',
              required=True, validators=[validators.isInLimits(0, 999999999999)]),
        Field(item="12C", name='CLOSED_CASES', type='number', startIndex=251, endIndex=259,
              friendly_name='number of closed cases',
              required=True, validators=[validators.isInLimits(0, 99999999)]),
    ],
)


m6 = SchemaManager(
    schemas=[
        s1,
        s2,
        s3
    ]
)
