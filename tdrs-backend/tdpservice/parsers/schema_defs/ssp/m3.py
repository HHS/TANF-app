"""Schema for SSP M1 record type."""


from ...util import MultiRecordRowSchema, RowSchema, Field
from ... import validators
from tdpservice.search_indexes.models.ssp import SSP_M3

first_part_schema = RowSchema(
    model=SSP_M3,
    preparsing_validators=[
        # validators.hasLength(150),  # unreliable.
        validators.notEmpty(start=19, end=60),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name='RecordType', type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8,
              required=True, validators=[]),
        Field(item="5", name='CASE_NUMBER', type='string', startIndex=8, endIndex=19,
              required=True, validators=[]),
        Field(item="60", name='FAMILY_AFFILIATION', type='number', startIndex=19, endIndex=20,
              required=True, validators=[]),
        Field(item="61", name='DATE_OF_BIRTH', type='string', startIndex=20, endIndex=28,
              required=True, validators=[]),
        Field(item="62", name='SSN', type='string', startIndex=28, endIndex=37,
              required=True, validators=[]),
        Field(item="63A", name='RACE_HISPANIC', type='number', startIndex=37, endIndex=38,
              required=True, validators=[]),
        Field(item="63B", name='RACE_AMER_INDIAN', type='number', startIndex=38, endIndex=39,
              required=True, validators=[]),
        Field(item="63C", name='RACE_ASIAN', type='number', startIndex=39, endIndex=40,
              required=True, validators=[]),
        Field(item="63D", name='RACE_BLACK', type='number', startIndex=40, endIndex=41,
              required=True, validators=[]),
        Field(item="63E", name='RACE_HAWAIIAN', type='number', startIndex=41, endIndex=42,
              required=True, validators=[]),
        Field(item="63F", name='RACE_WHITE', type='number', startIndex=42, endIndex=43,
              required=True, validators=[]),
        Field(item="64", name='GENDER', type='number', startIndex=43, endIndex=44,
              required=True, validators=[]),
        Field(item="65A", name='RECEIVE_NONSSI_BENEFITS', type='number', startIndex=44, endIndex=45,
              required=True, validators=[]),
        Field(item="65B", name='RECEIVE_SSI', type='number', startIndex=45, endIndex=46,
              required=True, validators=[]),
        Field(item="66", name='RELATIONSHIP_HOH', type='number', startIndex=46, endIndex=48,
              required=True, validators=[]),
        Field(item="67", name='PARENT_MINOR_CHILD', type='number', startIndex=48, endIndex=49,
              required=True, validators=[]),
        Field(item="68", name='EDUCATION_LEVEL', type='number', startIndex=49, endIndex=51,
              required=True, validators=[]),
        Field(item="69", name='CITIZENSHIP_STATUS', type='number', startIndex=51, endIndex=52,
              required=True, validators=[]),
        Field(item="70A", name='UNEARNED_SSI', type='number', startIndex=52, endIndex=56,
              required=True, validators=[]),
        Field(item="70B", name='OTHER_UNEARNED_INCOME', type='number', startIndex=56, endIndex=60,
              required=True, validators=[])
    ]
)

second_part_schema = RowSchema(
    model=SSP_M3,
    quiet_preparser_errors=True,
    preparsing_validators=[
        # validators.hasLength(150),  # unreliable.
        validators.notEmpty(start=60, end=101),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name='RecordType', type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8,
              required=True, validators=[]),
        Field(item="5", name='CASE_NUMBER', type='string', startIndex=8, endIndex=19,
              required=True, validators=[]),
        Field(item="60", name='FAMILY_AFFILIATION', type='number', startIndex=60, endIndex=61,
              required=True, validators=[]),
        Field(item="61", name='DATE_OF_BIRTH', type='string', startIndex=61, endIndex=69,
              required=True, validators=[]),
        Field(item="62", name='SSN', type='string', startIndex=69, endIndex=78,
              required=True, validators=[]),
        Field(item="63A", name='RACE_HISPANIC', type='number', startIndex=78, endIndex=79,
              required=True, validators=[]),
        Field(item="63B", name='RACE_AMER_INDIAN', type='number', startIndex=79, endIndex=80,
              required=True, validators=[]),
        Field(item="63C", name='RACE_ASIAN', type='number', startIndex=80, endIndex=81,
              required=True, validators=[]),
        Field(item="63D", name='RACE_BLACK', type='number', startIndex=81, endIndex=82,
              required=True, validators=[]),
        Field(item="63E", name='RACE_HAWAIIAN', type='number', startIndex=82, endIndex=83,
              required=True, validators=[]),
        Field(item="63F", name='RACE_WHITE', type='number', startIndex=83, endIndex=84,
              required=True, validators=[]),
        Field(item="64", name='GENDER', type='number', startIndex=84, endIndex=85,
              required=True, validators=[]),
        Field(item="65A", name='RECEIVE_NONSSI_BENEFITS', type='number', startIndex=85, endIndex=86,
              required=True, validators=[]),
        Field(item="65B", name='RECEIVE_SSI', type='number', startIndex=86, endIndex=87,
              required=True, validators=[]),
        Field(item="66", name='RELATIONSHIP_HOH', type='number', startIndex=87, endIndex=89,
              required=True, validators=[]),
        Field(item="67", name='PARENT_MINOR_CHILD', type='number', startIndex=89, endIndex=90,
              required=True, validators=[]),
        Field(item="68", name='EDUCATION_LEVEL', type='number', startIndex=90, endIndex=92,
              required=True, validators=[]),
        Field(item="69", name='CITIZENSHIP_STATUS', type='number', startIndex=92, endIndex=93,
              required=True, validators=[]),
        Field(item="70A", name='UNEARNED_SSI', type='number', startIndex=93, endIndex=97,
              required=True, validators=[]),
        Field(item="70B", name='OTHER_UNEARNED_INCOME', type='number', startIndex=97, endIndex=101,
              required=True, validators=[])
    ]
)

m3 = MultiRecordRowSchema(
    schemas=[
        first_part_schema,
        second_part_schema
    ]
)
