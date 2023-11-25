"""Schema for SSP M1 record type."""


from tdpservice.parsers.util import SchemaManager
from tdpservice.parsers.transforms import ssp_ssn_decryption_func
from tdpservice.parsers.fields import TransformField, Field
from tdpservice.parsers.row_schema import RowSchema
from tdpservice.parsers import validators
from tdpservice.search_indexes.models.ssp import SSP_M2


m2 = SchemaManager(
    schemas=[
        RowSchema(
          model=SSP_M2,
          preparsing_validators=[
              validators.hasLength(150),
          ],
          postparsing_validators=[
            validators.validate__FAM_AFF__SSN(),
            validators.if_then_validator(
                condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                result_field='SSN', result_function=validators.validateSSN(),
            ),
            validators.if_then_validator(
                condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                result_field='RACE_HISPANIC', result_function=validators.isInLimits(1, 2),
            ),
            validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                    result_field='RACE_AMER_INDIAN', result_function=validators.isInLimits(1, 2),
                ),
            validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                    result_field='RACE_ASIAN', result_function=validators.isInLimits(1, 2),
                ),
            validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                    result_field='RACE_BLACK', result_function=validators.isInLimits(1, 2),
                ),
            validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                    result_field='RACE_HAWAIIAN', result_function=validators.isInLimits(1, 2),
                ),
            validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                    result_field='RACE_WHITE', result_function=validators.isInLimits(1, 2),
                ),
            validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                    result_field='MARITAL_STATUS', result_function=validators.isInLimits(1, 5),
                ),
            validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 2),
                    result_field='PARENT_MINOR_CHILD', result_function=validators.isInLimits(1, 3),
                ),
            validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                    result_field='EDUCATION_LEVEL', result_function=validators.or_validators(
                        validators.isInStringRange(1, 16),
                        validators.isInStringRange(98, 99)
                    ),
                ),
            validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                    result_field='CITIZENSHIP_STATUS', result_function=validators.oneOf((1, 2)),
                ),
            validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                    result_field='COOPERATION_CHILD_SUPPORT', result_function=validators.oneOf((1, 2, 9)),
                ),
            validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                    result_field='EMPLOYMENT_STATUS', result_function=validators.isInLimits(1, 3),
                ),
            validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                    result_field='WORK_ELIGIBLE_INDICATOR', result_function=validators.or_validators(
                        validators.isInLimits(1, 9),
                        validators.oneOf((11, 12))
                    ),
                ),
            validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.oneOf((1, 2)),
                    result_field='WORK_PART_STATUS', result_function=validators.oneOf([
                        1, 2, 5, 7, 9,
                        15, 16, 17, 18, 99
                    ]),
                ),
            validators.if_then_validator(
                    condition_field='WORK_ELIGIBLE_INDICATOR', condition_function=validators.isInLimits(1, 5),
                    result_field='WORK_PART_STATUS', result_function=validators.notMatches(99),
                ),
          ],
          fields=[
              Field(item="0", name='RecordType', type='string', startIndex=0, endIndex=2,
                    friendly_name="record type", required=True, validators=[]),
              Field(item="3", name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8,
                    friendly_name="report month year", required=True, validators=[
                        validators.dateYearIsLargerThan(1998),
                        validators.dateMonthIsValid(),
                    ]),
              Field(item="5", name='CASE_NUMBER', type='string', startIndex=8, endIndex=19,
                    friendly_name="case number", required=True, validators=[
                        validators.isAlphaNumeric()
                    ]),
              Field(item="26", name='FAMILY_AFFILIATION', type='number', startIndex=19, endIndex=20,
                    friendly_name="family affiliation", required=True, validators=[
                        validators.oneOf([1, 2, 3, 5])
                    ]),
              Field(item="27", name='NONCUSTODIAL_PARENT', type='number', startIndex=20, endIndex=21,
                    friendly_name="noncustodial parent", required=True, validators=[
                        validators.oneOf([1, 2])
                    ]),
              Field(item="28", name='DATE_OF_BIRTH', type='number', startIndex=21, endIndex=29,
                    friendly_name="date of birth", required=True, validators=[
                        validators.isLargerThan(0)
                    ]),
              TransformField(transform_func=ssp_ssn_decryption_func, item="29", name='SSN', type='string',
                             startIndex=29, endIndex=38, required=True, validators=[validators.validateSSN()],
                             friendly_name="social security number - ssn", is_encrypted=False),
              Field(item="30A", name='RACE_HISPANIC', type='number', startIndex=38, endIndex=39, required=False,
                    friendly_name="race hispanic", validators=[
                        validators.isInLimits(0, 2)
                    ]),
              Field(item="30B", name='RACE_AMER_INDIAN', type='number', startIndex=39, endIndex=40,
                    friendly_name="race american indian", required=False, validators=[
                        validators.isInLimits(0, 2)
                    ]),
              Field(item="30C", name='RACE_ASIAN', type='number', startIndex=40, endIndex=41,
                    friendly_name="race asian", required=False, validators=[
                        validators.isInLimits(0, 2)
                    ]),
              Field(item="30D", name='RACE_BLACK', type='number', startIndex=41, endIndex=42,
                    friendly_name="race black", required=False, validators=[
                        validators.isInLimits(0, 2)
                    ]),
              Field(item="30E", name='RACE_HAWAIIAN', type='number', startIndex=42, endIndex=43,
                    friendly_name="race hawaiian", required=False, validators=[
                        validators.isInLimits(0, 2)
                    ]),
              Field(item="30F", name='RACE_WHITE', type='number', startIndex=43, endIndex=44,
                    friendly_name="race white", required=False, validators=[
                        validators.isInLimits(0, 2)
                    ]),
              Field(item="31", name='GENDER', type='number', startIndex=44, endIndex=45,
                    friendly_name="gender", required=True, validators=[
                        validators.isLargerThanOrEqualTo(0)
                    ]),
              Field(item="32A", name='FED_OASDI_PROGRAM', type='number', startIndex=45, endIndex=46,
                    friendly_name="federal qasdi program", required=True, validators=[
                        validators.oneOf([1, 2])
                    ]),
              Field(item="32B", name='FED_DISABILITY_STATUS', type='number', startIndex=46, endIndex=47,
                    friendly_name="federal disability status", required=True, validators=[
                        validators.oneOf([1, 2])
                    ]),
              Field(item="32C", name='DISABLED_TITLE_XIVAPDT', type='number', startIndex=47, endIndex=48,
                    friendly_name="disabled title xivapdt", required=True, validators=[
                        validators.oneOf([1, 2])
                    ]),
              Field(item="32D", name='AID_AGED_BLIND', type='number', startIndex=48, endIndex=49,
                    friendly_name="receives aid to the aid aged blind", required=False, validators=[
                        validators.isLargerThanOrEqualTo(0)
                    ]),
              Field(item="32E", name='RECEIVE_SSI', type='number', startIndex=49, endIndex=50,
                    friendly_name="receive ssi", required=True, validators=[
                        validators.oneOf([1, 2])
                    ]),
              Field(item="33", name='MARITAL_STATUS', type='number', startIndex=50, endIndex=51,
                    friendly_name="marital status", required=False, validators=[
                        validators.isInLimits(0, 5)
                    ]),
              Field(item="34", name='RELATIONSHIP_HOH', type='string', startIndex=51, endIndex=53,
                    friendly_name="relationship to head of household", required=True, validators=[
                        validators.isInStringRange(1, 10)
                    ]),
              Field(item="35", name='PARENT_MINOR_CHILD', type='number', startIndex=53, endIndex=54,
                    friendly_name="parent of minor child", required=False, validators=[
                        validators.isInLimits(0, 3)
                    ]),
              Field(item="36", name='NEEDS_PREGNANT_WOMAN', type='number', startIndex=54, endIndex=55,
                    friendly_name="needs of pregnant woman", required=False, validators=[
                        validators.isInLimits(0, 9)
                    ]),
              Field(item="37", name='EDUCATION_LEVEL', type='number', startIndex=55, endIndex=57,
                    friendly_name="education level", required=False, validators=[
                        validators.or_validators(
                            validators.isInLimits(0, 16),
                            validators.isInLimits(98, 99)
                        )
                    ]),
              Field(item="38", name='CITIZENSHIP_STATUS', type='number', startIndex=57, endIndex=58,
                    friendly_name="citizenship status", required=False, validators=[
                        validators.oneOf([0, 1, 2, 3, 9])
                    ]),
              Field(item="39", name='COOPERATION_CHILD_SUPPORT', type='number', startIndex=58, endIndex=59,
                    friendly_name="cooperation child support", required=False, validators=[
                        validators.oneOf([0, 1, 2, 9])
                    ]),
              Field(item="40", name='EMPLOYMENT_STATUS', type='number', startIndex=59, endIndex=60,
                    friendly_name="employment status", required=False, validators=[
                        validators.isInLimits(0, 3)
                    ]),
              Field(item="41", name='WORK_ELIGIBLE_INDICATOR', type='number', startIndex=60, endIndex=62,
                    friendly_name="work eligible indicator", required=True, validators=[
                        validators.or_validators(
                            validators.isInLimits(1, 4),
                            validators.isInLimits(6, 9),
                            validators.isInLimits(11, 12)
                        )
                    ]),
              Field(item="42", name='WORK_PART_STATUS', type='number', startIndex=62, endIndex=64,
                    friendly_name="work part-time status", required=False, validators=[
                        validators.oneOf([1, 2, 5, 7, 9, 15, 16, 17, 18, 19, 99])
                    ]),
              Field(item="43", name='UNSUB_EMPLOYMENT', type='number', startIndex=64, endIndex=66,
                    friendly_name="unsubsidized employment", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="44", name='SUB_PRIVATE_EMPLOYMENT', type='number', startIndex=66, endIndex=68,
                    friendly_name="subsidized private employment", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="45", name='SUB_PUBLIC_EMPLOYMENT', type='number', startIndex=68, endIndex=70,
                    friendly_name="subsidized public employment", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="46A", name='WORK_EXPERIENCE_HOP', type='number', startIndex=70, endIndex=72,
                    friendly_name="work experience - hours of participation", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="46B", name='WORK_EXPERIENCE_EA', type='number', startIndex=72, endIndex=74,
                    friendly_name="work experience - excused absense", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="46C", name='WORK_EXPERIENCE_HOL', type='number', startIndex=74, endIndex=76,
                    friendly_name="work experience holiday", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="47", name='OJT', type='number', startIndex=76, endIndex=78,
                    friendly_name="OJT", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="48A", name='JOB_SEARCH_HOP', type='number', startIndex=78, endIndex=80,
                    friendly_name="job search - hours of participation", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="48B", name='JOB_SEARCH_EA', type='number', startIndex=80, endIndex=82,
                    friendly_name="job search - excused absence", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="48C", name='JOB_SEARCH_HOL', type='number', startIndex=82, endIndex=84,
                    friendly_name="job search - holiday", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="49A", name='COMM_SERVICES_HOP', type='number', startIndex=84, endIndex=86,
                    friendly_name="community services - hours of participation", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="49B", name='COMM_SERVICES_EA', type='number', startIndex=86, endIndex=88,
                    friendly_name="community services - excused absence", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="49C", name='COMM_SERVICES_HOL', type='number', startIndex=88, endIndex=90,
                    friendly_name="community services - holiday", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="50A", name='VOCATIONAL_ED_TRAINING_HOP', type='number', startIndex=90, endIndex=92,
                    friendly_name="vocational education training - hours of operation", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="50B", name='VOCATIONAL_ED_TRAINING_EA', type='number', startIndex=92, endIndex=94,
                    friendly_name="vocational education training - excused absence", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="50C", name='VOCATIONAL_ED_TRAINING_HOL', type='number', startIndex=94, endIndex=96,
                    friendly_name="vocational education training - holiday", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="51A", name='JOB_SKILLS_TRAINING_HOP', type='number', startIndex=96, endIndex=98,
                    friendly_name="job skills training - hours of operation", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="51B", name='JOB_SKILLS_TRAINING_EA', type='number', startIndex=98, endIndex=100,
                    friendly_name="job skills training - excused absence", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="51C", name='JOB_SKILLS_TRAINING_HOL', type='number', startIndex=100, endIndex=102,
                    friendly_name="job skills training - holiday", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="52A", name='ED_NO_HIGH_SCHOOL_DIPL_HOP', type='number', startIndex=102, endIndex=104,
                    friendly_name="education no high school diploma - hours of participation",
                    required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="52B", name='ED_NO_HIGH_SCHOOL_DIPL_EA', type='number', startIndex=104, endIndex=106,
                    friendly_name="education no high school diploma - excused absence", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="52C", name='ED_NO_HIGH_SCHOOL_DIPL_HOL', type='number', startIndex=106, endIndex=108,
                    friendly_name="education no high school diploma - holiday", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="53A", name='SCHOOL_ATTENDENCE_HOP', type='number', startIndex=108, endIndex=110,
                    friendly_name="school attendance - hours of participation", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="53B", name='SCHOOL_ATTENDENCE_EA', type='number', startIndex=110, endIndex=112,
                    friendly_name="school attendance - excused absence", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="53C", name='SCHOOL_ATTENDENCE_HOL', type='number', startIndex=112, endIndex=114,
                    friendly_name="school attendance - holiday", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="54A", name='PROVIDE_CC_HOP', type='number', startIndex=114, endIndex=116,
                    friendly_name="provide child care - hours of participation", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="54B", name='PROVIDE_CC_EA', type='number', startIndex=116, endIndex=118,
                    friendly_name="provide child care - excused absence", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="54C", name='PROVIDE_CC_HOL', type='number', startIndex=118, endIndex=120,
                    friendly_name="provide child care - holiday", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="55", name='OTHER_WORK_ACTIVITIES', type='number', startIndex=120, endIndex=122,
                    friendly_name="other work activities", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="56", name='DEEMED_HOURS_FOR_OVERALL', type='number', startIndex=122, endIndex=124,
                    friendly_name="deemed hours for overall", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="57", name='DEEMED_HOURS_FOR_TWO_PARENT', type='number', startIndex=124, endIndex=126,
                    friendly_name="deemed hours for two parents", required=False, validators=[
                        validators.isInLimits(0, 99)
                    ]),
              Field(item="58", name='EARNED_INCOME', type='number', startIndex=126, endIndex=130,
                    friendly_name="earned income", required=True, validators=[
                        validators.isInLimits(0, 9999)
                    ]),
              Field(item="59A", name='UNEARNED_INCOME_TAX_CREDIT', type='number', startIndex=130, endIndex=134,
                    friendly_name="unearned income tax credit", required=False, validators=[
                        validators.isInLimits(0, 9999)
                    ]),
              Field(item="59B", name='UNEARNED_SOCIAL_SECURITY', type='number', startIndex=134, endIndex=138,
                    friendly_name="unearned social security", required=True, validators=[
                        validators.isInLimits(0, 9999)
                    ]),
              Field(item="59C", name='UNEARNED_SSI', type='number', startIndex=138, endIndex=142,
                    friendly_name="unearned ssi benefit", required=True, validators=[
                        validators.isInLimits(0, 9999)
                    ]),
              Field(item="59D", name='UNEARNED_WORKERS_COMP', type='number', startIndex=142, endIndex=146,
                    friendly_name="unearned workers compensation", required=True, validators=[
                        validators.isInLimits(0, 9999)
                    ]),
              Field(item="59E", name='OTHER_UNEARNED_INCOME', type='number', startIndex=146, endIndex=150,
                    friendly_name="other unearned income", required=True, validators=[
                        validators.isInLimits(0, 9999)
                    ]),
          ],
        )
    ]
)
