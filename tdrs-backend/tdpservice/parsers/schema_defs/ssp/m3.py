"""Schema for SSP M1 record type."""


from tdpservice.parsers.transforms import ssp_ssn_decryption_func
from tdpservice.parsers.fields import TransformField, Field
from tdpservice.parsers.row_schema import RowSchema, SchemaManager
from tdpservice.parsers.validators.category1 import PreparsingValidators
from tdpservice.parsers.validators.category2 import FieldValidators
from tdpservice.parsers.validators.category3 import ComposableValidators
from tdpservice.parsers.validators.util import is_quiet_preparser_errors
from tdpservice.search_indexes.documents.ssp import SSP_M3DataSubmissionDocument
from tdpservice.parsers.util import generate_t2_t3_t5_hashes, get_t2_t3_t5_partial_hash_members

FIRST_CHILD = 1
SECOND_CHILD = 2

first_part_schema = RowSchema(
    record_type="M3",
    document=SSP_M3DataSubmissionDocument(),
    generate_hashes_func=generate_t2_t3_t5_hashes,
    should_skip_partial_dup_func=lambda record: record.FAMILY_AFFILIATION in {2, 4, 5},
    get_partial_hash_members_func=get_t2_t3_t5_partial_hash_members,
    preparsing_validators=[
        PreparsingValidators.t3_m3_child_validator(FIRST_CHILD),
        PreparsingValidators.caseNumberNotEmpty(8, 19),
        PreparsingValidators.or_priority_validators([
                    PreparsingValidators.validate_fieldYearMonth_with_headerYearQuarter(),
                    PreparsingValidators.validateRptMonthYear(),
                ]),
        PreparsingValidators.recordIsNotEmpty(8, 19)
    ],
    postparsing_validators=[
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isEqual(1),
            result_field_name='SSN',
            result_function=ComposableValidators.validateSSN(),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isOneOf((1, 2)),
            result_field_name='RACE_HISPANIC',
            result_function=ComposableValidators.isBetween(1, 2, inclusive=True),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isOneOf((1, 2)),
            result_field_name='RACE_AMER_INDIAN',
            result_function=ComposableValidators.isBetween(1, 2, inclusive=True),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isOneOf((1, 2)),
            result_field_name='RACE_ASIAN',
            result_function=ComposableValidators.isBetween(1, 2, inclusive=True),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isOneOf((1, 2)),
            result_field_name='RACE_BLACK',
            result_function=ComposableValidators.isBetween(1, 2, inclusive=True),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isOneOf((1, 2)),
            result_field_name='RACE_HAWAIIAN',
            result_function=ComposableValidators.isBetween(1, 2, inclusive=True),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isOneOf((1, 2)),
            result_field_name='RACE_WHITE',
            result_function=ComposableValidators.isBetween(1, 2, inclusive=True),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isOneOf((1, 2)),
            result_field_name='RELATIONSHIP_HOH',
            result_function=ComposableValidators.isBetween(4, 9, inclusive=True),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isOneOf((1, 2)),
            result_field_name='PARENT_MINOR_CHILD',
            result_function=ComposableValidators.isOneOf((1, 2, 3)),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isEqual(1),
            result_field_name='EDUCATION_LEVEL',
            result_function=ComposableValidators.isNotEqual(99),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isEqual(1),
            result_field_name='CITIZENSHIP_STATUS',
            result_function=ComposableValidators.isOneOf((1, 2)),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isEqual(2),
            result_field_name='CITIZENSHIP_STATUS',
            result_function=ComposableValidators.isOneOf((1, 2, 3, 9)),
            ),
    ],
    fields=[
        Field(
            item="0",
            name='RecordType',
            friendly_name="Record Type",
            type='string',
            startIndex=0,
            endIndex=2,
            required=True,
            validators=[]
        ),
        Field(
            item="3",
            name='RPT_MONTH_YEAR',
            friendly_name="Reporting Year and Month",
            type='number',
            startIndex=2,
            endIndex=8,
            required=True,
            validators=[
                FieldValidators.dateYearIsLargerThan(1998),
                FieldValidators.dateMonthIsValid(),
            ]
        ),
        Field(
            item="5",
            name='CASE_NUMBER',
            friendly_name="Case Number",
            type='string',
            startIndex=8,
            endIndex=19,
            required=True,
            validators=[FieldValidators.isNotEmpty()]
        ),
        Field(
            item="60",
            name='FAMILY_AFFILIATION',
            friendly_name="Family Affiliation",
            type='number',
            startIndex=19,
            endIndex=20,
            required=True,
            validators=[FieldValidators.isOneOf([1, 2, 4])]
        ),
        Field(
            item="61",
            name='DATE_OF_BIRTH',
            friendly_name="Date of Birth",
            type='string',
            startIndex=20,
            endIndex=28,
            required=True,
            validators=[FieldValidators.intHasLength(8),
                        FieldValidators.dateYearIsLargerThan(1900),
                        FieldValidators.dateMonthIsValid(),
                        FieldValidators.dateDayIsValid()
                        ]
        ),
        TransformField(
            transform_func=ssp_ssn_decryption_func,
            item="62",
            name='SSN',
            friendly_name="Social Security Number",
            type='string',
            startIndex=28,
            endIndex=37,
            required=True,
            is_encrypted=False,
            validators=[FieldValidators.isNumber()]
        ),
        Field(
            item="63A",
            name='RACE_HISPANIC',
            friendly_name="Hispanic or Latino",
            type='number',
            startIndex=37,
            endIndex=38,
            required=False,
            validators=[FieldValidators.isBetween(0, 2, inclusive=True)]
        ),
        Field(
            item="63B",
            name='RACE_AMER_INDIAN',
            friendly_name="American Indian or Alaska Native",
            type='number',
            startIndex=38,
            endIndex=39,
            required=False,
            validators=[FieldValidators.isBetween(0, 2, inclusive=True)]
        ),
        Field(
            item="63C",
            name='RACE_ASIAN',
            friendly_name="Asian",
            type='number',
            startIndex=39,
            endIndex=40,
            required=False,
            validators=[FieldValidators.isBetween(0, 2, inclusive=True)]
        ),
        Field(
            item="63D",
            name='RACE_BLACK',
            friendly_name="Black or African American",
            type='number',
            startIndex=40,
            endIndex=41,
            required=False,
            validators=[FieldValidators.isBetween(0, 2, inclusive=True)]
        ),
        Field(
            item="63E",
            name='RACE_HAWAIIAN',
            friendly_name="Native Hawaiian or Pacific Islander",
            type='number',
            startIndex=41,
            endIndex=42,
            required=False,
            validators=[FieldValidators.isBetween(0, 2, inclusive=True)]
        ),
        Field(
            item="63F",
            name='RACE_WHITE',
            friendly_name="White",
            type='number',
            startIndex=42,
            endIndex=43,
            required=False,
            validators=[FieldValidators.isBetween(0, 2, inclusive=True)]
        ),
        Field(
            item="64",
            name='GENDER',
            friendly_name="Gender",
            type='number',
            startIndex=43,
            endIndex=44,
            required=True,
            validators=[FieldValidators.isBetween(0, 9, inclusive=True)]
        ),
        Field(
            item="65A",
            name='RECEIVE_NONSSI_BENEFITS',
            friendly_name="Receives Disability Benefits: Federal Disability Status",
            type='number',
            startIndex=44,
            endIndex=45,
            required=True,
            validators=[FieldValidators.isOneOf([1, 2])]
        ),
        Field(
            item="65B",
            name='RECEIVE_SSI',
            friendly_name="Receives Disability Benefits: SSI or AABD",
            type='number',
            startIndex=45,
            endIndex=46,
            required=True,
            validators=[FieldValidators.isOneOf([1, 2])]
        ),
        Field(
            item="66",
            name='RELATIONSHIP_HOH',
            friendly_name="Relationship to Head-of-Household",
            type='number',
            startIndex=46,
            endIndex=48,
            required=False,
            validators=[FieldValidators.isBetween(0, 10, inclusive=True, cast=int)]
        ),
        Field(
            item="67",
            name='PARENT_MINOR_CHILD',
            friendly_name="Parental Status of Minor",
            type='number',
            startIndex=48,
            endIndex=49,
            required=False,
            validators=[FieldValidators.isOneOf([0, 2, 3])]
        ),
        Field(
            item="68",
            name='EDUCATION_LEVEL',
            friendly_name="Educational Level",
            type='string',
            startIndex=49,
            endIndex=51,
            required=True,
            validators=[
                FieldValidators.orValidators([
                    ComposableValidators.isBetween(1, 16, inclusive=True, cast=int),
                    ComposableValidators.isBetween(98, 99, inclusive=True, cast=int)
                ]),
            ]
        ),
        Field(
            item="69",
            name='CITIZENSHIP_STATUS',
            friendly_name="Citizenship/Immigration Status",
            type='number',
            startIndex=51,
            endIndex=52,
            required=False,
            validators=[FieldValidators.isOneOf([1, 2, 3, 9])]
        ),
        Field(
            item="70A",
            name='UNEARNED_SSI',
            friendly_name="Amount of Unearned Income: SSI",
            type='number',
            startIndex=52,
            endIndex=56,
            required=True,
            validators=[FieldValidators.isBetween(0, 9999, inclusive=True)]
        ),
        Field(
            item="70B",
            name='OTHER_UNEARNED_INCOME',
            friendly_name="Amount of Unearned Income: Other",
            type='number',
            startIndex=56,
            endIndex=60,
            required=True,
            validators=[FieldValidators.isBetween(0, 9999, inclusive=True)]
        )
    ]
)

second_part_schema = RowSchema(
    record_type="M3",
    document=SSP_M3DataSubmissionDocument(),
    generate_hashes_func=generate_t2_t3_t5_hashes,
    should_skip_partial_dup_func=lambda record: record.FAMILY_AFFILIATION in {2, 4, 5},
    get_partial_hash_members_func=get_t2_t3_t5_partial_hash_members,
    quiet_preparser_errors=is_quiet_preparser_errors(min_length=61),
    preparsing_validators=[
        PreparsingValidators.t3_m3_child_validator(SECOND_CHILD),
        PreparsingValidators.caseNumberNotEmpty(8, 19),
        PreparsingValidators.or_priority_validators([
                    PreparsingValidators.validate_fieldYearMonth_with_headerYearQuarter(),
                    PreparsingValidators.validateRptMonthYear(),
                ]),
    ],
    postparsing_validators=[
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isEqual(1),
            result_field_name='SSN',
            result_function=ComposableValidators.validateSSN(),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isOneOf((1, 2)),
            result_field_name='RACE_HISPANIC',
            result_function=ComposableValidators.isBetween(1, 2, inclusive=True),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isOneOf((1, 2)),
            result_field_name='RACE_AMER_INDIAN',
            result_function=ComposableValidators.isBetween(1, 2, inclusive=True),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isOneOf((1, 2)),
            result_field_name='RACE_ASIAN',
            result_function=ComposableValidators.isBetween(1, 2, inclusive=True),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isOneOf((1, 2)),
            result_field_name='RACE_BLACK',
            result_function=ComposableValidators.isBetween(1, 2, inclusive=True),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isOneOf((1, 2)),
            result_field_name='RACE_HAWAIIAN',
            result_function=ComposableValidators.isBetween(1, 2, inclusive=True),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isOneOf((1, 2)),
            result_field_name='RACE_WHITE',
            result_function=ComposableValidators.isBetween(1, 2, inclusive=True),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isOneOf((1, 2)),
            result_field_name='RELATIONSHIP_HOH',
            result_function=ComposableValidators.isBetween(4, 9, inclusive=True, cast=int),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isOneOf((1, 2)),
            result_field_name='PARENT_MINOR_CHILD',
            result_function=ComposableValidators.isOneOf((1, 2, 3)),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isEqual(1),
            result_field_name='EDUCATION_LEVEL',
            result_function=ComposableValidators.isNotEqual(99),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isEqual(1),
            result_field_name='CITIZENSHIP_STATUS',
            result_function=ComposableValidators.isOneOf((1, 2)),
            ),
        ComposableValidators.ifThenAlso(
            condition_field_name='FAMILY_AFFILIATION',
            condition_function=ComposableValidators.isEqual(2),
            result_field_name='CITIZENSHIP_STATUS',
            result_function=ComposableValidators.isOneOf((1, 2, 3, 9)),
            ),
    ],
    fields=[
        Field(
            item="0",
            name='RecordType',
            friendly_name="Record Type",
            type='string',
            startIndex=0,
            endIndex=2,
            required=True,
            validators=[]
        ),
        Field(
            item="3",
            name='RPT_MONTH_YEAR',
            friendly_name="Reporting Year and Month",
            type='number',
            startIndex=2,
            endIndex=8,
            required=True,
            validators=[
                FieldValidators.dateYearIsLargerThan(1998),
                FieldValidators.dateMonthIsValid(),
            ]
        ),
        Field(
            item="5",
            name='CASE_NUMBER',
            friendly_name="Case Number",
            type='string',
            startIndex=8,
            endIndex=19,
            required=True,
            validators=[FieldValidators.isNotEmpty()]
        ),
        Field(
            item="60",
            name='FAMILY_AFFILIATION',
            friendly_name="Family Affiliation",
            type='number',
            startIndex=60,
            endIndex=61,
            required=True,
            validators=[FieldValidators.isOneOf([1, 2, 4])]
        ),
        Field(
            item="61",
            name='DATE_OF_BIRTH',
            friendly_name="Date of Birth",
            type='string',
            startIndex=61,
            endIndex=69,
            required=True,
            validators=[FieldValidators.intHasLength(8),
                        FieldValidators.dateYearIsLargerThan(1900),
                        FieldValidators.dateMonthIsValid(),
                        FieldValidators.dateDayIsValid()
                        ]
        ),
        TransformField(
            transform_func=ssp_ssn_decryption_func,
            item="62",
            name='SSN',
            friendly_name="Social Security Number",
            type='string',
            startIndex=69,
            endIndex=78,
            required=True,
            is_encrypted=False,
            validators=[FieldValidators.isNumber()]
        ),
        Field(
            item="63A",
            name='RACE_HISPANIC',
            friendly_name="Hispanic or Latino",
            type='number',
            startIndex=78,
            endIndex=79,
            required=False,
            validators=[FieldValidators.isBetween(0, 2, inclusive=True)]
        ),
        Field(
            item="63B",
            name='RACE_AMER_INDIAN',
            friendly_name="American Indian or Alaska Native",
            type='number',
            startIndex=79,
            endIndex=80,
            required=False,
            validators=[FieldValidators.isBetween(0, 2, inclusive=True)]
        ),
        Field(
            item="63C",
            name='RACE_ASIAN',
            friendly_name="Asian",
            type='number',
            startIndex=80,
            endIndex=81,
            required=False,
            validators=[FieldValidators.isBetween(0, 2, inclusive=True)]
        ),
        Field(
            item="63D",
            name='RACE_BLACK',
            friendly_name="Black or African American",
            type='number',
            startIndex=81,
            endIndex=82,
            required=False,
            validators=[FieldValidators.isBetween(0, 2, inclusive=True)]
        ),
        Field(
            item="63E",
            name='RACE_HAWAIIAN',
            friendly_name="Native Hawaiian or Pacific Islander",
            type='number',
            startIndex=82,
            endIndex=83,
            required=False,
            validators=[FieldValidators.isBetween(0, 2, inclusive=True)]
        ),
        Field(
            item="63F",
            name='RACE_WHITE',
            friendly_name="White",
            type='number',
            startIndex=83,
            endIndex=84,
            required=False,
            validators=[FieldValidators.isBetween(0, 2, inclusive=True)]
        ),
        Field(
            item="64",
            name='GENDER',
            friendly_name="Gender",
            type='number',
            startIndex=84,
            endIndex=85,
            required=True,
            validators=[FieldValidators.isBetween(0, 9, inclusive=True)]
        ),
        Field(
            item="65A",
            name='RECEIVE_NONSSI_BENEFITS',
            friendly_name="Receives Disability Benefits: Other Federal Disability Status",
            type='number',
            startIndex=85,
            endIndex=86,
            required=True,
            validators=[FieldValidators.isOneOf([1, 2])]
        ),
        Field(
            item="65B",
            name='RECEIVE_SSI',
            friendly_name="Receives Disability Benefits: SSI or AABD",
            type='number',
            startIndex=86,
            endIndex=87,
            required=True,
            validators=[FieldValidators.isOneOf([1, 2])]
        ),
        Field(
            item="66",
            name='RELATIONSHIP_HOH',
            friendly_name="Relationship to Head-of-Household",
            type='number',
            startIndex=87,
            endIndex=89,
            required=False,
            validators=[FieldValidators.isBetween(0, 10, inclusive=True)]
        ),
        Field(
            item="67",
            name='PARENT_MINOR_CHILD',
            friendly_name="Parental Status of Minor",
            type='number',
            startIndex=89,
            endIndex=90,
            required=False,
            validators=[FieldValidators.isOneOf([0, 2, 3])]
        ),
        Field(
            item="68",
            name='EDUCATION_LEVEL',
            friendly_name="Educational Level",
            type='string',
            startIndex=90,
            endIndex=92,
            required=True,
            validators=[
                FieldValidators.orValidators([
                    ComposableValidators.isBetween(1, 16, inclusive=True, cast=int),
                    ComposableValidators.isBetween(98, 99, inclusive=True, cast=int)
                ])
            ]
        ),
        Field(
            item="69",
            name='CITIZENSHIP_STATUS',
            friendly_name="Citizenship/Immigration Status",
            type='number',
            startIndex=92,
            endIndex=93,
            required=False,
            validators=[FieldValidators.isOneOf([1, 2, 3, 9])]
        ),
        Field(
            item="70A",
            name='UNEARNED_SSI',
            friendly_name="Amount of Unearned Income: SSI",
            type='number',
            startIndex=93,
            endIndex=97,
            required=True,
            validators=[FieldValidators.isBetween(0, 9999, inclusive=True)]
        ),
        Field(
            item="70B",
            name='OTHER_UNEARNED_INCOME',
            friendly_name="Amount of Unearned Income: Other",
            type='number',
            startIndex=97,
            endIndex=101,
            required=True,
            validators=[FieldValidators.isBetween(0, 9999, inclusive=True)]
        )
    ]
)

m3 = SchemaManager(schemas=[first_part_schema, second_part_schema])
