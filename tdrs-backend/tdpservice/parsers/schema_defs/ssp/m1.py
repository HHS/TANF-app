"""Schema for SSP M1 record type."""


from ...util import RowSchema, Field
from ... import validators
from tdpservice.search_indexes.models.ssp import SSP_M1


m1 = RowSchema(
    model=SSP_M1,
    preparsing_validators=[
        validators.hasLength(150),
    ],
    postparsing_validators=[],
    fields=[
        Field(item=1, name='RecordType', type='string', startIndex=0, endIndex=2, required=True, validators=[
        ]),
        Field(item=2, name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8, required=True, validators=[
        ]),
        Field(item=3, name='CASE_NUMBER', type='string', startIndex=8, endIndex=19, required=True, validators=[
        ]),
        Field(item=4, name='COUNTY_FIPS_CODE', type='string', startIndex=19, endIndex=22, required=True, validators=[
        ]),
        Field(item=5, name='STRATUM', type='number', startIndex=22, endIndex=24, required=True, validators=[
        ]),
        Field(item=6, name='ZIP_CODE', type='string', startIndex=24, endIndex=29, required=True, validators=[
        ]),
        Field(item=7, name='DISPOSITION', type='number', startIndex=29, endIndex=30, required=True, validators=[
        ]),
        # Field(itemNumbe=1, name='NEW_APPLICANT', type='number', startIndex=31, endIndex=32, required=True, validators=[
        # ]),
        Field(item=8, name='NBR_FAMILY_MEMBERS', type='number', startIndex=30, endIndex=32, required=True, validators=[
        ]),
        Field(item=9, name='FAMILY_TYPE', type='number', startIndex=32, endIndex=33, required=True, validators=[
        ]),
        Field(item=10, name='TANF_ASST_IN_6MONTHS', type='number', startIndex=33, endIndex=34, required=True, validators=[
        ]),
        Field(item=11, name='RECEIVES_SUB_HOUSING', type='number', startIndex=34, endIndex=35, required=True, validators=[
        ]),
        Field(item=12, name='RECEIVES_MED_ASSISTANCE', type='number', startIndex=35, endIndex=36, required=True, validators=[
        ]),
        Field(item=13, name='RECEIVES_FOOD_STAMPS', type='number', startIndex=36, endIndex=37, required=True, validators=[
        ]),
        Field(item=14, name='AMT_FOOD_STAMP_ASSISTANCE', type='number', startIndex=37, endIndex=41, required=True, validators=[
        ]),
        Field(item=15, name='RECEIVES_SUB_CC', type='number', startIndex=41, endIndex=42, required=True, validators=[
        ]),
        Field(item=16, name='AMT_SUB_CC', type='number', startIndex=42, endIndex=46, required=True, validators=[
        ]),
        Field(item=17, name='CHILD_SUPPORT_AMT', type='number', startIndex=46, endIndex=50, required=True, validators=[
        ]),
        Field(item=18, name='FAMILY_CASH_RESOURCES', type='number', startIndex=50, endIndex=54, required=True, validators=[
        ]),
        Field(item=19, name='CASH_AMOUNT', type='number', startIndex=54, endIndex=58, required=True, validators=[
        ]),
        Field(item=20, name='NBR_MONTHS', type='number', startIndex=58, endIndex=61, required=True, validators=[
        ]),
        Field(item=21, name='CC_AMOUNT', type='number', startIndex=61, endIndex=65, required=True, validators=[
        ]),
        Field(item=22, name='CHILDREN_COVERED', type='number', startIndex=65, endIndex=67, required=True, validators=[
        ]),
        Field(item=23, name='CC_NBR_MONTHS', type='number', startIndex=67, endIndex=70, required=True, validators=[
        ]),
        Field(item=24, name='TRANSP_AMOUNT', type='number', startIndex=70, endIndex=74, required=True, validators=[
        ]),
        Field(item=25, name='TRANSP_NBR_MONTHS', type='number', startIndex=74, endIndex=77, required=True, validators=[
        ]),
        Field(item=26, name='TRANSITION_SERVICES_AMOUNT', type='number', startIndex=77, endIndex=81, required=True, validators=[
        ]),
        Field(item=27, name='TRANSITION_NBR_MONTHS', type='number', startIndex=81, endIndex=84, required=True, validators=[
        ]),
        Field(item=28, name='OTHER_AMOUNT', type='number', startIndex=84, endIndex=88, required=True, validators=[
        ]),
        Field(item=29, name='OTHER_NBR_MONTHS', type='number', startIndex=88, endIndex=91, required=True, validators=[
        ]),
        Field(item=30, name='SANC_REDUCTION_AMT', type='number', startIndex=91, endIndex=95, required=True, validators=[
        ]),
        Field(item=31, name='WORK_REQ_SANCTION', type='number', startIndex=95, endIndex=96, required=True, validators=[
        ]),
        Field(item=32, name='FAMILY_SANC_ADULT', type='number', startIndex=96, endIndex=97, required=True, validators=[
        ]),
        Field(item=33, name='SANC_TEEN_PARENT', type='number', startIndex=97, endIndex=98, required=True, validators=[
        ]),
        Field(item=34, name='NON_COOPERATION_CSE', type='number', startIndex=98, endIndex=99, required=True, validators=[
        ]),
        Field(item=35, name='FAILURE_TO_COMPLY', type='number', startIndex=99, endIndex=100, required=True, validators=[
        ]),
        Field(item=36, name='OTHER_SANCTION', type='number', startIndex=100, endIndex=101, required=True, validators=[
        ]),
        Field(item=37, name='RECOUPMENT_PRIOR_OVRPMT', type='number', startIndex=101, endIndex=105, required=True, validators=[
        ]),
        Field(item=38, name='OTHER_TOTAL_REDUCTIONS', type='number', startIndex=105, endIndex=109, required=True, validators=[
        ]),
        Field(item=39, name='FAMILY_CAP', type='number', startIndex=109, endIndex=110, required=True, validators=[
        ]),
        Field(item=40, name='REDUCTIONS_ON_RECEIPTS', type='number', startIndex=110, endIndex=111, required=True, validators=[
        ]),
        Field(item=41, name='OTHER_NON_SANCTION', type='number', startIndex=111, endIndex=112, required=True, validators=[
        ]),
        Field(item=42, name='WAIVER_EVAL_CONTROL_GRPS', type='number', startIndex=112, endIndex=113, required=True, validators=[
        ]),
        # Field(item=1, name='FAMILY_EXEMPT_TIME_LIMITS', type='number', startIndex=114, endIndex=116, required=True, validators=[
        # ]),
        # Field(item=1, name='FAMILY_NEW_CHILD', type='number', startIndex=116, endIndex=117, required=True, validators=[
        # ]),
        Field(item=43, name='BLANK', type='string', startIndex=113, endIndex=150, required=False, validators=[]),
    ],
)
