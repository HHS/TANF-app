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
        Field(item=1, name='RecordType', type='string', startIndex=0, endIndex=2, required=True, validators=[
        ]),
        Field(item=2, name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8, required=True, validators=[
        ]),
        Field(item=3, name='CASE_NUMBER', type='string', startIndex=8, endIndex=19, required=True, validators=[
        ]),
        # Field(item=1, name='FIPS_CODE', type='string', startIndex=8, endIndex=19, required=True, validators=[
        # ]),
        Field(item=4, name='FAMILY_AFFILIATION', type='number', startIndex=19, endIndex=20, required=True, validators=[
        ]),
        Field(item=5, name='DATE_OF_BIRTH', type='string', startIndex=20, endIndex=28, required=True, validators=[
        ]),
        Field(item=6, name='SSN', type='string', startIndex=28, endIndex=37, required=True, validators=[
        ]),
        Field(item=7, name='RACE_HISPANIC', type='number', startIndex=37, endIndex=38, required=True, validators=[
        ]),
        Field(item=8, name='RACE_AMER_INDIAN', type='number', startIndex=38, endIndex=39, required=True, validators=[
        ]),
        Field(item=9, name='RACE_ASIAN', type='number', startIndex=39, endIndex=40, required=True, validators=[
        ]),
        Field(item=10, name='RACE_BLACK', type='number', startIndex=40, endIndex=41, required=True, validators=[
        ]),
        Field(item=11, name='RACE_HAWAIIAN', type='number', startIndex=41, endIndex=42, required=True, validators=[
        ]),
        Field(item=12, name='RACE_WHITE', type='number', startIndex=42, endIndex=43, required=True, validators=[
        ]),
        Field(item=13, name='GENDER', type='number', startIndex=43, endIndex=44, required=True, validators=[
        ]),
        Field(item=14, name='RECEIVE_NONSSI_BENEFITS', type='number', startIndex=44, endIndex=45, required=True, validators=[
        ]),
        Field(item=15, name='RECEIVE_SSI', type='number', startIndex=45, endIndex=46, required=True, validators=[
        ]),
        Field(item=16, name='RELATIONSHIP_HOH', type='number', startIndex=46, endIndex=48, required=True, validators=[
        ]),
        Field(item=17, name='PARENT_MINOR_CHILD', type='number', startIndex=48, endIndex=49, required=True, validators=[
        ]),
        Field(item=18, name='EDUCATION_LEVEL', type='number', startIndex=49, endIndex=51, required=True, validators=[
        ]),
        Field(item=19, name='CITIZENSHIP_STATUS', type='number', startIndex=51, endIndex=52, required=True, validators=[
        ]),
        Field(item=20, name='UNEARNED_SSI', type='number', startIndex=52, endIndex=56, required=True, validators=[
        ]),
        Field(item=21, name='OTHER_UNEARNED_INCOME', type='number', startIndex=56, endIndex=60, required=True, validators=[
        ])
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
        Field(item=1, name='RecordType', type='string', startIndex=0, endIndex=2, required=True, validators=[
        ]),
        Field(item=2, name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8, required=True, validators=[
        ]),
        Field(item=3, name='CASE_NUMBER', type='string', startIndex=8, endIndex=19, required=True, validators=[
        ]),
        # Field(item=1, name='FIPS_CODE', type='string', startIndex=8, endIndex=19, required=True, validators=[
        # ]),
        Field(item=22, name='FAMILY_AFFILIATION', type='number', startIndex=60, endIndex=61, required=True, validators=[
        ]),
        Field(item=23, name='DATE_OF_BIRTH', type='string', startIndex=61, endIndex=69, required=True, validators=[
        ]),
        Field(item=24, name='SSN', type='string', startIndex=69, endIndex=78, required=True, validators=[
        ]),
        Field(item=25, name='RACE_HISPANIC', type='number', startIndex=78, endIndex=79, required=True, validators=[
        ]),
        Field(item=26, name='RACE_AMER_INDIAN', type='number', startIndex=79, endIndex=80, required=True, validators=[
        ]),
        Field(item=27, name='RACE_ASIAN', type='number', startIndex=80, endIndex=81, required=True, validators=[
        ]),
        Field(item=28, name='RACE_BLACK', type='number', startIndex=81, endIndex=82, required=True, validators=[
        ]),
        Field(item=29, name='RACE_HAWAIIAN', type='number', startIndex=82, endIndex=83, required=True, validators=[
        ]),
        Field(item=30, name='RACE_WHITE', type='number', startIndex=83, endIndex=84, required=True, validators=[
        ]),
        Field(item=31, name='GENDER', type='number', startIndex=84, endIndex=85, required=True, validators=[
        ]),
        Field(item=32, name='RECEIVE_NONSSI_BENEFITS', type='number', startIndex=85, endIndex=86, required=True, validators=[
        ]),
        Field(item=33, name='RECEIVE_SSI', type='number', startIndex=86, endIndex=87, required=True, validators=[
        ]),
        Field(item=34, name='RELATIONSHIP_HOH', type='number', startIndex=87, endIndex=89, required=True, validators=[
        ]),
        Field(item=35, name='PARENT_MINOR_CHILD', type='number', startIndex=89, endIndex=90, required=True, validators=[
        ]),
        Field(item=36, name='EDUCATION_LEVEL', type='number', startIndex=90, endIndex=92, required=True, validators=[
        ]),
        Field(item=37, name='CITIZENSHIP_STATUS', type='number', startIndex=92, endIndex=93, required=True, validators=[
        ]),
        Field(item=38, name='UNEARNED_SSI', type='number', startIndex=93, endIndex=97, required=True, validators=[
        ]),
        Field(item=39, name='OTHER_UNEARNED_INCOME', type='number', startIndex=97, endIndex=101, required=True, validators=[
        ])
    ]
)

m3 = MultiRecordRowSchema(
    schemas=[
        first_part_schema,
        second_part_schema
    ]
)


# m3 = RowSchema(
#     model=SSP_M3,
#     preparsing_validators=[
#         validators.hasLength(150),  # ?? the format document shows double fields/length?
#     ],
#     postparsing_validators=[],
#     fields=[
#         Field(item=1, name='RecordType', type='string', startIndex=0, endIndex=2, required=True, validators=[
#         ]),
#         Field(item=1, name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8, required=True, validators=[
#         ]),
#         Field(item=1, name='CASE_NUMBER', type='string', startIndex=8, endIndex=19, required=True, validators=[
#         ]),
#         # Field(item=1, name='FIPS_CODE', type='string', startIndex=8, endIndex=19, required=True, validators=[
#         # ]),
#         Field(item=1, name='FAMILY_AFFILIATION', type='number', startIndex=19, endIndex=20, required=True, validators=[
#         ]),
#         Field(item=1, name='DATE_OF_BIRTH', type='number', startIndex=20, endIndex=28, required=True, validators=[
#         ]),
#         Field(item=1, name='SSN', type='number', startIndex=28, endIndex=37, required=True, validators=[
#         ]),
#         Field(item=1, name='RACE_HISPANIC', type='number', startIndex=37, endIndex=38, required=True, validators=[
#         ]),
#         Field(item=1, name='RACE_AMER_INDIAN', type='number', startIndex=38, endIndex=39, required=True, validators=[
#         ]),
#         Field(item=1, name='RACE_ASIAN', type='number', startIndex=39, endIndex=40, required=True, validators=[
#         ]),
#         Field(item=1, name='RACE_BLACK', type='number', startIndex=40, endIndex=41, required=True, validators=[
#         ]),
#         Field(item=1, name='RACE_HAWAIIAN', type='number', startIndex=41, endIndex=42, required=True, validators=[
#         ]),
#         Field(item=1, name='RACE_WHITE', type='number', startIndex=42, endIndex=43, required=True, validators=[
#         ]),
#         Field(item=1, name='GENDER', type='number', startIndex=43, endIndex=44, required=True, validators=[
#         ]),
#         Field(item=1, name='RECEIVE_NONSSI_BENEFITS', type='number', startIndex=44, endIndex=45, required=True, validators=[
#         ]),
#         Field(item=1, name='RECEIVE_SSI', type='number', startIndex=45, endIndex=46, required=True, validators=[
#         ]),
#         Field(item=1, name='RELATIONSHIP_HOH', type='number', startIndex=46, endIndex=48, required=True, validators=[
#         ]),
#         Field(item=1, name='PARENT_MINOR_CHILD', type='number', startIndex=48, endIndex=49, required=True, validators=[
#         ]),
#         Field(item=1, name='EDUCATION_LEVEL', type='number', startIndex=49, endIndex=51, required=True, validators=[
#         ]),
#         Field(item=1, name='CITIZENSHIP_STATUS', type='number', startIndex=51, endIndex=52, required=True, validators=[
#         ]),
#         Field(item=1, name='UNEARNED_SSI', type='number', startIndex=52, endIndex=56, required=True, validators=[
#         ]),
#         Field(item=1, name='OTHER_UNEARNED_INCOME', type='number', startIndex=56, endIndex=60, required=True, validators=[
#         ]),

#         # ??
#         Field(item=1, name='FAMILY_AFFILIATION', type='number', startIndex=60, endIndex=61, required=True, validators=[
#         ]),
#         Field(item=1, name='DATE_OF_BIRTH', type='number', startIndex=61, endIndex=69, required=True, validators=[
#         ]),
#         Field(item=1, name='SSN', type='number', startIndex=69, endIndex=78, required=True, validators=[
#         ]),
#         Field(item=1, name='RACE_HISPANIC', type='number', startIndex=78, endIndex=79, required=True, validators=[
#         ]),
#         Field(item=1, name='RACE_AMER_INDIAN', type='number', startIndex=79, endIndex=80, required=True, validators=[
#         ]),
#         Field(item=1, name='RACE_ASIAN', type='number', startIndex=80, endIndex=81, required=True, validators=[
#         ]),
#         Field(item=1, name='RACE_BLACK', type='number', startIndex=81, endIndex=82, required=True, validators=[
#         ]),
#         Field(item=1, name='RACE_HAWAIIAN', type='number', startIndex=82, endIndex=83, required=True, validators=[
#         ]),
#         Field(item=1, name='RACE_WHITE', type='number', startIndex=83, endIndex=84, required=True, validators=[
#         ]),
#         Field(item=1, name='GENDER', type='number', startIndex=84, endIndex=85, required=True, validators=[
#         ]),
#         Field(item=1, name='RECEIVE_NONSSI_BENEFITS', type='number', startIndex=85, endIndex=86, required=True, validators=[
#         ]),
#         Field(item=1, name='RECEIVE_SSI', type='number', startIndex=86, endIndex=87, required=True, validators=[
#         ]),
#         Field(item=1, name='RELATIONSHIP_HOH', type='number', startIndex=87, endIndex=89, required=True, validators=[
#         ]),
#         Field(item=1, name='PARENT_MINOR_CHILD', type='number', startIndex=89, endIndex=90, required=True, validators=[
#         ]),
#         Field(item=1, name='EDUCATION_LEVEL', type='number', startIndex=90, endIndex=92, required=True, validators=[
#         ]),
#         Field(item=1, name='CITIZENSHIP_STATUS', type='number', startIndex=92, endIndex=93, required=True, validators=[
#         ]),
#         Field(item=1, name='UNEARNED_SSI', type='number', startIndex=93, endIndex=97, required=True, validators=[
#         ]),
#         Field(item=1, name='OTHER_UNEARNED_INCOME', type='number', startIndex=97, endIndex=101, required=True, validators=[
#         ]),
#         # Field(item=1, name='BLANK', type='string', startIndex=101, endIndex=150, required=False, validators=[]),
#     ],
# )
