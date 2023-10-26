"""Schema for SSP M1 record type."""


from ...util import SchemaManager
from ...transforms import ssp_ssn_decryption_func
from ...fields import TransformField, Field
from ...row_schema import RowSchema
from ... import validators
from tdpservice.search_indexes.models.ssp import SSP_M3

first_part_schema = RowSchema(
    model=SSP_M3,
    preparsing_validators=[
        validators.notEmpty(start=19, end=60),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name='RecordType', friendly_name='record type', type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='RPT_MONTH_YEAR', friendly_name='report month year', type='number', startIndex=2, endIndex=8,
              required=True, validators=[]),
        Field(item="5", name='CASE_NUMBER', friendly_name='case number', type='string', startIndex=8, endIndex=19,
              required=True, validators=[]),
        Field(item="60", name='FAMILY_AFFILIATION', friendly_name='family affiliation', type='number', startIndex=19, endIndex=20,
              required=True, validators=[]),
        Field(item="61", name='DATE_OF_BIRTH', friendly_name='date of birth', type='string', startIndex=20, endIndex=28,
              required=True, validators=[]),
        TransformField(transform_func=ssp_ssn_decryption_func, item="62", name='SSN', friendly_name='social security number - SSN', type='string', startIndex=28,
                       endIndex=37, required=True, validators=[], is_encrypted=False),
        Field(item="63A", name='RACE_HISPANIC', friendly_name='race hispanic', type='number', startIndex=37, endIndex=38,
              required=True, validators=[]),
        Field(item="63B", name='RACE_AMER_INDIAN', friendly_name='race american indian', type='number', startIndex=38, endIndex=39,
              required=True, validators=[]),
        Field(item="63C", name='RACE_ASIAN', friendly_name='race asian', type='number', startIndex=39, endIndex=40,
              required=True, validators=[]),
        Field(item="63D", name='RACE_BLACK', friendly_name='race black', type='number', startIndex=40, endIndex=41,
              required=True, validators=[]),
        Field(item="63E", name='RACE_HAWAIIAN', friendly_name='race hawaiian', type='number', startIndex=41, endIndex=42,
              required=True, validators=[]),
        Field(item="63F", name='RACE_WHITE', friendly_name='race white', type='number', startIndex=42, endIndex=43,
              required=True, validators=[]),
        Field(item="64", name='GENDER', friendly_name='gender', type='number', startIndex=43, endIndex=44,
              required=True, validators=[]),
        Field(item="65A", name='RECEIVE_NONSSI_BENEFITS', friendly_name='receive nonssi benefits', type='number', startIndex=44, endIndex=45,
              required=True, validators=[]),
        Field(item="65B", name='RECEIVE_SSI', friendly_name='receive ssi', type='number', startIndex=45, endIndex=46,
              required=True, validators=[]),
        Field(item="66", name='RELATIONSHIP_HOH', friendly_name='relationship - ', type='number', startIndex=46, endIndex=48,
              required=True, validators=[]),
        Field(item="67", name='PARENT_MINOR_CHILD', friendly_name='parent minor child', type='number', startIndex=48, endIndex=49,
              required=True, validators=[]),
        Field(item="68", name='EDUCATION_LEVEL', friendly_name='education level', type='number', startIndex=49, endIndex=51,
              required=True, validators=[]),
        Field(item="69", name='CITIZENSHIP_STATUS', friendly_name='citizenship status', type='number', startIndex=51, endIndex=52,
              required=True, validators=[]),
        Field(item="70A", name='UNEARNED_SSI', friendly_name='unearned SSI', type='number', startIndex=52, endIndex=56,
              required=True, validators=[]),
        Field(item="70B", name='OTHER_UNEARNED_INCOME', friendly_name='other unearned income', type='number', startIndex=56, endIndex=60,
              required=True, validators=[])
    ]
)

second_part_schema = RowSchema(
    model=SSP_M3,
    quiet_preparser_errors=True,
    preparsing_validators=[
        validators.notEmpty(start=60, end=101),
    ],
    postparsing_validators=[],
    fields=[
        Field(item="0", name='RecordType', friendly_name='record type', type='string', startIndex=0, endIndex=2,
              required=True, validators=[]),
        Field(item="3", name='RPT_MONTH_YEAR', friendly_name='report month year', type='number', startIndex=2, endIndex=8,
              required=True, validators=[]),
        Field(item="5", name='CASE_NUMBER', friendly_name='case number', type='string', startIndex=8, endIndex=19,
              required=True, validators=[]),
        Field(item="60", name='FAMILY_AFFILIATION', friendly_name='family affiliation', type='number', startIndex=60, endIndex=61,
              required=True, validators=[]),
        Field(item="61", name='DATE_OF_BIRTH', friendly_name='date of birth', type='string', startIndex=61, endIndex=69,
              required=True, validators=[]),
        TransformField(transform_func=ssp_ssn_decryption_func, item="62", name='SSN', friendly_name='social security number - SSN', type='string', startIndex=69,
                       endIndex=78, required=True, validators=[], is_encrypted=False),
        Field(item="63A", name='RACE_HISPANIC', friendly_name='race hispanic', type='number', startIndex=78, endIndex=79,
              required=True, validators=[]),
        Field(item="63B", name='RACE_AMER_INDIAN', friendly_name='race american indian', type='number', startIndex=79, endIndex=80,
              required=True, validators=[]),
        Field(item="63C", name='RACE_ASIAN', friendly_name='race asian', type='number', startIndex=80, endIndex=81,
              required=True, validators=[]),
        Field(item="63D", name='RACE_BLACK', friendly_name='race black', type='number', startIndex=81, endIndex=82,
              required=True, validators=[]),
        Field(item="63E", name='RACE_HAWAIIAN', friendly_name='race hawaiian', type='number', startIndex=82, endIndex=83,
              required=True, validators=[]),
        Field(item="63F", name='RACE_WHITE', friendly_name='race white', type='number', startIndex=83, endIndex=84,
              required=True, validators=[]),
        Field(item="64", name='GENDER', friendly_name='gender', type='number', startIndex=84, endIndex=85,
              required=True, validators=[]),
        Field(item="65A", name='RECEIVE_NONSSI_BENEFITS', friendly_name='receive nonssi benefit', type='number', startIndex=85, endIndex=86,
              required=True, validators=[]),
        Field(item="65B", name='RECEIVE_SSI', friendly_name='receives ssi', type='number', startIndex=86, endIndex=87,
              required=True, validators=[]),
        Field(item="66", name='RELATIONSHIP_HOH', friendly_name='realtionship head of household', type='number', startIndex=87, endIndex=89,
              required=True, validators=[]),
        Field(item="67", name='PARENT_MINOR_CHILD', friendly_name='parent minor child', type='number', startIndex=89, endIndex=90,
              required=True, validators=[]),
        Field(item="68", name='EDUCATION_LEVEL', friendly_name='education level', type='number', startIndex=90, endIndex=92,
              required=True, validators=[]),
        Field(item="69", name='CITIZENSHIP_STATUS', friendly_name='citizenship status', type='number', startIndex=92, endIndex=93,
              required=True, validators=[]),
        Field(item="70A", name='UNEARNED_SSI', friendly_name='unearned ssi', type='number', startIndex=93, endIndex=97,
              required=True, validators=[]),
        Field(item="70B", name='OTHER_UNEARNED_INCOME', friendly_name='other unearned income', type='number', startIndex=97, endIndex=101,
              required=True, validators=[])
    ]
)

m3 = SchemaManager(
    schemas=[
        first_part_schema,
        second_part_schema
    ]
)
