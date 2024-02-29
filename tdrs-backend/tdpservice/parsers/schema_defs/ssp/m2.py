"""Schema for SSP M1 record type."""


from tdpservice.parsers.transforms import ssp_ssn_decryption_func
from tdpservice.parsers.fields import TransformField, Field
from tdpservice.parsers.row_schema import RowSchema, SchemaManager
from tdpservice.parsers import validators
from tdpservice.search_indexes.documents.ssp import SSP_M2DataSubmissionDocument


m2 = SchemaManager(
    schemas=[
        RowSchema(
            document=SSP_M2DataSubmissionDocument(),
            preparsing_validators=[
                validators.hasLength(150),
                validators.notEmpty(8, 19),
                validators.field_year_month_with_header_year_quarter(),
            ],
            postparsing_validators=[
                validators.validate__FAM_AFF__SSN(),
                validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION',
                    condition_function=validators.matches(1),
                    result_field='SSN',
                    result_function=validators.validateSSN(),
                ),
                validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field='RACE_HISPANIC',
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field='RACE_AMER_INDIAN',
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field='RACE_ASIAN',
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field='RACE_BLACK',
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field='RACE_HAWAIIAN',
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field='RACE_WHITE',
                    result_function=validators.isInLimits(1, 2),
                ),
                validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field='MARITAL_STATUS',
                    result_function=validators.isInLimits(1, 5),
                ),
                validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 2),
                    result_field='PARENT_MINOR_CHILD',
                    result_function=validators.isInLimits(1, 3),
                ),
                validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field='EDUCATION_LEVEL',
                    result_function=validators.or_validators(
                        validators.isInStringRange(1, 16),
                        validators.isInStringRange(98, 99),
                    ),
                ),
                validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION',
                    condition_function=validators.matches(1),
                    result_field='CITIZENSHIP_STATUS',
                    result_function=validators.oneOf((1, 2)),
                ),
                validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field='COOPERATION_CHILD_SUPPORT',
                    result_function=validators.oneOf((1, 2, 9)),
                ),
                validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION',
                    condition_function=validators.isInLimits(1, 3),
                    result_field='EMPLOYMENT_STATUS',
                    result_function=validators.isInLimits(1, 3),
                ),
                validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION',
                    condition_function=validators.oneOf((1, 2)),
                    result_field='WORK_ELIGIBLE_INDICATOR',
                    result_function=validators.or_validators(
                        validators.isInLimits(1, 9),
                        validators.oneOf((11, 12))
                    ),
                ),
                validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION',
                    condition_function=validators.oneOf((1, 2)),
                    result_field='WORK_PART_STATUS',
                    result_function=validators.oneOf([1, 2, 5, 7, 9, 15, 16, 17, 18, 99]),
                ),
                validators.if_then_validator(
                    condition_field='WORK_ELIGIBLE_INDICATOR',
                    condition_function=validators.isInLimits(1, 5),
                    result_field='WORK_PART_STATUS',
                    result_function=validators.notMatches(99),
                ),
            ],
            fields=[
                Field(
                    item="0",
                    name='RecordType',
                    friendly_name="record type",
                    type='string',
                    startIndex=0,
                    endIndex=2,
                    required=True,
                    validators=[]
                ),
                Field(
                    item="3",
                    name='RPT_MONTH_YEAR',
                    friendly_name="reporting month and year",
                    type='number',
                    startIndex=2,
                    endIndex=8,
                    required=True,
                    validators=[
                        validators.dateYearIsLargerThan(1998),
                        validators.dateMonthIsValid(),
                    ]
                ),
                Field(
                    item="5",
                    name='CASE_NUMBER',
                    friendly_name="case number",
                    type='string',
                    startIndex=8,
                    endIndex=19,
                    required=True,
                    validators=[validators.notEmpty()]
                ),
                Field(
                    item="26",
                    name='FAMILY_AFFILIATION',
                    friendly_name="family affiliation",
                    type='number',
                    startIndex=19,
                    endIndex=20,
                    required=True,
                    validators=[validators.oneOf([1, 2, 3, 5])]
                ),
                Field(
                    item="27",
                    name='NONCUSTODIAL_PARENT',
                    friendly_name="noncustodial parent",
                    type='number',
                    startIndex=20,
                    endIndex=21,
                    required=True,
                    validators=[validators.oneOf([1, 2])]
                ),
                Field(
                    item="28",
                    name='DATE_OF_BIRTH',
                    friendly_name="date of birth",
                    type='number',
                    startIndex=21,
                    endIndex=29,
                    required=True,
                    validators=[validators.isLargerThan(0)]
                ),
                TransformField(
                    transform_func=ssp_ssn_decryption_func,
                    item="29",
                    name='SSN',
                    friendly_name="social security number",
                    type='string',
                    startIndex=29,
                    endIndex=38,
                    required=True,
                    validators=[validators.isNumber()],
                    is_encrypted=False
                ),
                Field(
                    item="30A",
                    name='RACE_HISPANIC',
                    type='number',
                    friendly_name="race hispanic",
                    startIndex=38,
                    endIndex=39,
                    required=False,
                    validators=[validators.isInLimits(0, 2)]
                ),
                Field(
                    item="30B",
                    name='RACE_AMER_INDIAN',
                    friendly_name="race american-indian",
                    type='number',
                    startIndex=39,
                    endIndex=40,
                    required=False,
                    validators=[validators.isInLimits(0, 2)]
                ),
                Field(
                    item="30C",
                    name='RACE_ASIAN',
                    friendly_name="race asian",
                    type='number',
                    startIndex=40,
                    endIndex=41,
                    required=False,
                    validators=[validators.isInLimits(0, 2)]
                ),
                Field(
                    item="30D",
                    name='RACE_BLACK',
                    friendly_name="race black",
                    type='number',
                    startIndex=41,
                    endIndex=42,
                    required=False,
                    validators=[validators.isInLimits(0, 2)]
                ),
                Field(
                    item="30E",
                    name='RACE_HAWAIIAN',
                    friendly_name="race hawaiian",
                    type='number',
                    startIndex=42,
                    endIndex=43,
                    required=False,
                    validators=[validators.isInLimits(0, 2)]
                ),
                Field(
                    item="30F",
                    name='RACE_WHITE',
                    friendly_name="race white",
                    type='number',
                    startIndex=43,
                    endIndex=44,
                    required=False,
                    validators=[validators.isInLimits(0, 2)]
                ),
                Field(
                    item="31",
                    name='GENDER',
                    friendly_name="gender",
                    type='number',
                    startIndex=44,
                    endIndex=45,
                    required=True,
                    validators=[validators.isLargerThanOrEqualTo(0)]
                ),
                Field(
                    item="32A",
                    name='FED_OASDI_PROGRAM',
                    friendly_name="federal old-age survivors and disability insurance program",
                    type='number',
                    startIndex=45,
                    endIndex=46,
                    required=True,
                    validators=[validators.oneOf([1, 2])]
                ),
                Field(
                    item="32B",
                    name='FED_DISABILITY_STATUS',
                    friendly_name="federal disability status",
                    type='number',
                    startIndex=46,
                    endIndex=47,
                    required=True,
                    validators=[validators.oneOf([1, 2])]
                ),
                Field(
                    item="32C",
                    name='DISABLED_TITLE_XIVAPDT',
                    friendly_name="received aid under Title XIV-APDT",
                    type='number',
                    startIndex=47,
                    endIndex=48,
                    required=True,
                    validators=[validators.oneOf([1, 2])]
                ),
                Field(
                    item="32D",
                    name='AID_AGED_BLIND',
                    friendly_name="receives from aid to the aged, blind, and disabled program",
                    type='number',
                    startIndex=48,
                    endIndex=49,
                    required=False,
                    validators=[validators.isLargerThanOrEqualTo(0)]
                ),
                Field(
                    item="32E",
                    name='RECEIVE_SSI',
                    friendly_name="receives SSI",
                    type='number',
                    startIndex=49,
                    endIndex=50,
                    required=True,
                    validators=[validators.oneOf([1, 2])]
                ),
                Field(
                    item="33",
                    name='MARITAL_STATUS',
                    friendly_name="marital status",
                    type='number',
                    startIndex=50,
                    endIndex=51,
                    required=False,
                    validators=[validators.isInLimits(0, 5)]
                ),
                Field(
                    item="34",
                    name='RELATIONSHIP_HOH',
                    friendly_name="relationship to head of household",
                    type='string',
                    startIndex=51,
                    endIndex=53,
                    required=True,
                    validators=[validators.isInStringRange(1, 10)]
                ),
                Field(
                    item="35",
                    name='PARENT_MINOR_CHILD',
                    friendly_name="parent of minor child",
                    type='number',
                    startIndex=53,
                    endIndex=54,
                    required=False,
                    validators=[validators.isInLimits(0, 3)]
                ),
                Field(
                    item="36",
                    name='NEEDS_PREGNANT_WOMAN',
                    friendly_name="needs of pregnant woman",
                    type='number',
                    startIndex=54,
                    endIndex=55,
                    required=False,
                    validators=[validators.isInLimits(0, 9)]
                ),
                Field(
                    item="37",
                    name='EDUCATION_LEVEL',
                    friendly_name="education level",
                    type='number',
                    startIndex=55,
                    endIndex=57,
                    required=False,
                    validators=[
                        validators.or_validators(
                            validators.isInLimits(0, 16), validators.isInLimits(98, 99)
                        )
                    ]
                ),
                Field(
                    item="38",
                    name='CITIZENSHIP_STATUS',
                    friendly_name="citizenship status",
                    type='number',
                    startIndex=57,
                    endIndex=58,
                    required=False,
                    validators=[validators.oneOf([0, 1, 2, 3, 9])]
                ),
                Field(
                    item="39",
                    name='COOPERATION_CHILD_SUPPORT',
                    friendly_name="cooperation with child support",
                    type='number',
                    startIndex=58,
                    endIndex=59,
                    required=False,
                    validators=[validators.oneOf([0, 1, 2, 9])]
                ),
                Field(
                    item="40",
                    name='EMPLOYMENT_STATUS',
                    friendly_name="employment status",
                    type='number',
                    startIndex=59,
                    endIndex=60,
                    required=False,
                    validators=[validators.isInLimits(0, 3)]
                ),
                Field(
                    item="41",
                    name='WORK_ELIGIBLE_INDICATOR',
                    friendly_name="work eligible indicator",
                    type='number',
                    startIndex=60,
                    endIndex=62,
                    required=True,
                    validators=[
                        validators.or_validators(
                            validators.isInLimits(1, 4),
                            validators.isInLimits(6, 9),
                            validators.isInLimits(11, 12),
                        )
                    ]
                ),
                Field(
                    item="42",
                    name='WORK_PART_STATUS',
                    friendly_name="work participation status",
                    type='number',
                    startIndex=62,
                    endIndex=64,
                    required=False,
                    validators=[validators.oneOf([1, 2, 5, 7, 9, 15, 16, 17, 18, 19, 99])]
                ),
                Field(
                    item="43",
                    name='UNSUB_EMPLOYMENT',
                    friendly_name="unsubsidized employment",
                    type='number',
                    startIndex=64,
                    endIndex=66,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="44",
                    name='SUB_PRIVATE_EMPLOYMENT',
                    friendly_name="subsidized private employment",
                    type='number',
                    startIndex=66,
                    endIndex=68,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="45",
                    name='SUB_PUBLIC_EMPLOYMENT',
                    friendly_name="subsidized public employment",
                    type='number',
                    startIndex=68,
                    endIndex=70,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="46A",
                    name='WORK_EXPERIENCE_HOP',
                    friendly_name="work experience - hours of participation",
                    type='number',
                    startIndex=70,
                    endIndex=72,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="46B",
                    name='WORK_EXPERIENCE_EA',
                    friendly_name="work experience - excused absence",
                    type='number',
                    startIndex=72,
                    endIndex=74,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="46C",
                    name='WORK_EXPERIENCE_HOL',
                    friendly_name="work experience hours - holiday",
                    type='number',
                    startIndex=74,
                    endIndex=76,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="47",
                    name='OJT',
                    friendly_name="OJT",
                    type='number',
                    startIndex=76,
                    endIndex=78,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="48A",
                    name='JOB_SEARCH_HOP',
                    friendly_name="job search - hours of participation",
                    type='number',
                    startIndex=78,
                    endIndex=80,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="48B",
                    name='JOB_SEARCH_EA',
                    friendly_name="job search - excused absence",
                    type='number',
                    startIndex=80,
                    endIndex=82,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="48C",
                    name='JOB_SEARCH_HOL',
                    friendly_name="job search - holiday",
                    type='number',
                    startIndex=82,
                    endIndex=84,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="49A",
                    name='COMM_SERVICES_HOP',
                    friendly_name="community services - hours of participation",
                    type='number',
                    startIndex=84,
                    endIndex=86,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="49B",
                    name='COMM_SERVICES_EA',
                    friendly_name="community services - excused absence",
                    type='number',
                    startIndex=86,
                    endIndex=88,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="49C",
                    name='COMM_SERVICES_HOL',
                    friendly_name="community services - holiday",
                    type='number',
                    startIndex=88,
                    endIndex=90,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="50A",
                    name='VOCATIONAL_ED_TRAINING_HOP',
                    friendly_name="vocational education training - hours of participation",
                    type='number',
                    startIndex=90,
                    endIndex=92,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="50B",
                    name='VOCATIONAL_ED_TRAINING_EA',
                    friendly_name="vocational education training - excused absence",
                    type='number',
                    startIndex=92,
                    endIndex=94,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="50C",
                    name='VOCATIONAL_ED_TRAINING_HOL',
                    friendly_name="vocational education training - holiday",
                    type='number',
                    startIndex=94,
                    endIndex=96,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="51A",
                    name='JOB_SKILLS_TRAINING_HOP',
                    friendly_name="job skills training - hours of participation",
                    type='number',
                    startIndex=96,
                    endIndex=98,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="51B",
                    name='JOB_SKILLS_TRAINING_EA',
                    friendly_name="job skills training - excused absence",
                    type='number',
                    startIndex=98,
                    endIndex=100,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="51C",
                    name='JOB_SKILLS_TRAINING_HOL',
                    friendly_name="job skills training - holiday",
                    type='number',
                    startIndex=100,
                    endIndex=102,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="52A",
                    name='ED_NO_HIGH_SCHOOL_DIPL_HOP',
                    friendly_name="education no high school diploma - hours of participation",
                    type='number',
                    startIndex=102,
                    endIndex=104,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="52B",
                    name='ED_NO_HIGH_SCHOOL_DIPL_EA',
                    friendly_name="education no high school diploma - excused absence",
                    type='number',
                    startIndex=104,
                    endIndex=106,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="52C",
                    name='ED_NO_HIGH_SCHOOL_DIPL_HOL',
                    friendly_name="education no high school diploma - holiday",
                    type='number',
                    startIndex=106,
                    endIndex=108,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="53A",
                    name='SCHOOL_ATTENDENCE_HOP',
                    friendly_name="school attendance - hours of participation",
                    type='number',
                    startIndex=108,
                    endIndex=110,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="53B",
                    name='SCHOOL_ATTENDENCE_EA',
                    friendly_name="school attendance - excused absence",
                    type='number',
                    startIndex=110,
                    endIndex=112,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="53C",
                    name='SCHOOL_ATTENDENCE_HOL',
                    friendly_name="school attendance - holiday",
                    type='number',
                    startIndex=112,
                    endIndex=114,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="54A",
                    name='PROVIDE_CC_HOP',
                    friendly_name="provide child care - hours of participation",
                    type='number',
                    startIndex=114,
                    endIndex=116,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="54B",
                    name='PROVIDE_CC_EA',
                    friendly_name="provide child care - excused absence",
                    type='number',
                    startIndex=116,
                    endIndex=118,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="54C",
                    name='PROVIDE_CC_HOL',
                    friendly_name="provide child care - holiday",
                    type='number',
                    startIndex=118,
                    endIndex=120,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="55",
                    name='OTHER_WORK_ACTIVITIES',
                    friendly_name="other work activities",
                    type='number',
                    startIndex=120,
                    endIndex=122,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="56",
                    name='DEEMED_HOURS_FOR_OVERALL',
                    friendly_name="deemed hours for overall",
                    type='number',
                    startIndex=122,
                    endIndex=124,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="57",
                    name='DEEMED_HOURS_FOR_TWO_PARENT',
                    friendly_name="deemed hours for two parents",
                    type='number',
                    startIndex=124,
                    endIndex=126,
                    required=False,
                    validators=[validators.isInLimits(0, 99)]
                ),
                Field(
                    item="58",
                    name='EARNED_INCOME',
                    friendly_name="earned income",
                    type='number',
                    startIndex=126,
                    endIndex=130,
                    required=True,
                    validators=[validators.isInLimits(0, 9999)]
                ),
                Field(
                    item="59A",
                    name='UNEARNED_INCOME_TAX_CREDIT',
                    friendly_name="unearned income tax credit",
                    type='number',
                    startIndex=130,
                    endIndex=134,
                    required=False,
                    validators=[validators.isInLimits(0, 9999)]
                ),
                Field(
                    item="59B",
                    name='UNEARNED_SOCIAL_SECURITY',
                    friendly_name="unearned social security",
                    type='number',
                    startIndex=134,
                    endIndex=138,
                    required=True,
                    validators=[validators.isInLimits(0, 9999)]
                ),
                Field(
                    item="59C",
                    name='UNEARNED_SSI',
                    friendly_name="unearned SSI benefit",
                    type='number',
                    startIndex=138,
                    endIndex=142,
                    required=True,
                    validators=[validators.isInLimits(0, 9999)]
                ),
                Field(
                    item="59D",
                    name='UNEARNED_WORKERS_COMP',
                    friendly_name="unearned workers compensation",
                    type='number',
                    startIndex=142,
                    endIndex=146,
                    required=True,
                    validators=[validators.isInLimits(0, 9999)]
                ),
                Field(
                    item="59E",
                    name='OTHER_UNEARNED_INCOME',
                    friendly_name="other unearned income",
                    type='number',
                    startIndex=146,
                    endIndex=150,
                    required=True,
                    validators=[validators.isInLimits(0, 9999)]
                ),
            ],
        )
    ]
)
