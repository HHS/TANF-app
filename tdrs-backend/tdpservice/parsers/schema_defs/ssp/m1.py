"""Schema for SSP M1 record type."""


from tdpservice.parsers.util import SchemaManager
from tdpservice.parsers.fields import Field
from tdpservice.parsers.row_schema import RowSchema
from tdpservice.parsers import validators
from tdpservice.search_indexes.models.ssp import SSP_M1

m1 = SchemaManager(
    schemas=[
        RowSchema(
          model=SSP_M1,
          preparsing_validators=[
              validators.hasLength(150),
          ],
          postparsing_validators=[
            validators.if_then_validator(
                  condition_field='CASH_AMOUNT', condition_function=validators.isLargerThan(0),
                  result_field='NBR_MONTHS', result_function=validators.isLargerThan(0),
            ),
            validators.if_then_validator(
                  condition_field='CC_AMOUNT', condition_function=validators.isLargerThan(0),
                  result_field='CHILDREN_COVERED', result_function=validators.isLargerThan(0),
            ),
            validators.if_then_validator(
                  condition_field='CC_AMOUNT', condition_function=validators.isLargerThan(0),
                  result_field='CC_NBR_MONTHS', result_function=validators.isLargerThan(0),
            ),
            validators.if_then_validator(
                  condition_field='TRANSP_AMOUNT', condition_function=validators.isLargerThan(0),
                  result_field='TRANSP_NBR_MONTHS', result_function=validators.isLargerThan(0),
            ),
            validators.if_then_validator(
                  condition_field='SANC_REDUCTION_AMT', condition_function=validators.isLargerThan(0),
                  result_field='WORK_REQ_SANCTION', result_function=validators.oneOf((1, 2)),
            ),
            validators.if_then_validator(
                  condition_field='SANC_REDUCTION_AMT', condition_function=validators.isLargerThan(0),
                  result_field='SANC_TEEN_PARENT', result_function=validators.oneOf((1, 2)),
            ),
            validators.if_then_validator(
                  condition_field='SANC_REDUCTION_AMT', condition_function=validators.isLargerThan(0),
                  result_field='NON_COOPERATION_CSE', result_function=validators.oneOf((1, 2)),
            ),
            validators.if_then_validator(
                  condition_field='SANC_REDUCTION_AMT', condition_function=validators.isLargerThan(0),
                  result_field='FAILURE_TO_COMPLY', result_function=validators.oneOf((1, 2)),
            ),
            validators.if_then_validator(
                  condition_field='SANC_REDUCTION_AMT', condition_function=validators.isLargerThan(0),
                  result_field='OTHER_SANCTION', result_function=validators.oneOf((1, 2)),
            ),
            validators.if_then_validator(
                  condition_field='OTHER_TOTAL_REDUCTIONS', condition_function=validators.isLargerThan(0),
                  result_field='FAMILY_CAP', result_function=validators.oneOf((1, 2)),
            ),
            validators.if_then_validator(
                  condition_field='OTHER_TOTAL_REDUCTIONS', condition_function=validators.isLargerThan(0),
                  result_field='REDUCTIONS_ON_RECEIPTS', result_function=validators.oneOf((1, 2)),
            ),
            validators.if_then_validator(
                  condition_field='OTHER_TOTAL_REDUCTIONS', condition_function=validators.isLargerThan(0),
                  result_field='OTHER_NON_SANCTION', result_function=validators.oneOf((1, 2)),
            ),
            validators.sumIsLarger([
                  "AMT_FOOD_STAMP_ASSISTANCE",
                  "AMT_SUB_CC",
                  "CASH_AMOUNT",
                  "CC_AMOUNT",
                  "CC_NBR_MONTHS"
                  ], 0)
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
              Field(item="2", name='COUNTY_FIPS_CODE', type='string', startIndex=19, endIndex=22,
                    friendly_name="county fips code", required=True, validators=[
                        validators.isNumber(),
                    ]),
              Field(item="4", name='STRATUM', type='string', startIndex=22, endIndex=24,
                    friendly_name="stratum", required=False, validators=[
                        validators.isInStringRange(0, 99),
                    ]),
              Field(item="6", name='ZIP_CODE', type='string', startIndex=24, endIndex=29,
                    friendly_name="zip code", required=True, validators=[
                        validators.isNumber(),
                    ]),
              Field(item="7", name='DISPOSITION', type='number', startIndex=29, endIndex=30,
                    friendly_name="disposition", required=True, validators=[
                        validators.oneOf([1, 2]),
                    ]),
              Field(item="8", name='NBR_FAMILY_MEMBERS', type='number', startIndex=30, endIndex=32,
                    friendly_name="number of family numbers", required=True, validators=[
                        validators.isInLimits(1, 99),
                    ]),
              Field(item="9", name='FAMILY_TYPE', type='number', startIndex=32, endIndex=33,
                    friendly_name="family type", required=True, validators=[
                        validators.isInLimits(1, 3),
                    ]),
              Field(item="10", name='TANF_ASST_IN_6MONTHS', type='number', startIndex=33, endIndex=34,
                    friendly_name="tanf assitance in 6 months", required=True, validators=[
                        validators.isInLimits(1, 3),
                    ]),
              Field(item="11", name='RECEIVES_SUB_HOUSING', type='number', startIndex=34, endIndex=35,
                    friendly_name="receives subsidized housing", required=True, validators=[
                        validators.isInLimits(1, 2),
                    ]),
              Field(item="12", name='RECEIVES_MED_ASSISTANCE', type='number', startIndex=35, endIndex=36,
                    friendly_name="receives medical assisstance", required=True, validators=[
                        validators.isInLimits(1, 2),
                    ]),
              Field(item="13", name='RECEIVES_FOOD_STAMPS', type='number', startIndex=36, endIndex=37,
                    friendly_name="receives food assisstance", required=False, validators=[
                        validators.isInLimits(0, 2),
                    ]),
              Field(item="14", name='AMT_FOOD_STAMP_ASSISTANCE', type='number', startIndex=37, endIndex=41,
                    friendly_name="amount of food stamp assisstance", required=True, validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ]),
              Field(item="15", name='RECEIVES_SUB_CC', type='number', startIndex=41, endIndex=42,
                    friendly_name="receives subsidized child care", required=False, validators=[
                        validators.isInLimits(0, 2),
                    ]),
              Field(item="16", name='AMT_SUB_CC', type='number', startIndex=42, endIndex=46,
                    friendly_name="amount of subsidized child care", required=True, validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ]),
              Field(item="17", name='CHILD_SUPPORT_AMT', type='number', startIndex=46, endIndex=50,
                    friendly_name="child support amount", required=True, validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ]),
              Field(item="18", name='FAMILY_CASH_RESOURCES', type='number', startIndex=50, endIndex=54,
                    friendly_name="family cash resources", required=True, validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ]),
              Field(item="19A", name='CASH_AMOUNT', type='number', startIndex=54, endIndex=58,
                    friendly_name="cash amount", required=True, validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ]),
              Field(item="19B", name='NBR_MONTHS', type='number', startIndex=58, endIndex=61,
                    friendly_name="number of months", required=True, validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ]),
              Field(item="20A", name='CC_AMOUNT', type='number', startIndex=61, endIndex=65,
                    friendly_name="child care amount", required=True, validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ]),
              Field(item="20B", name='CHILDREN_COVERED', type='number', startIndex=65, endIndex=67,
                    friendly_name="children covered", required=True, validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ]),
              Field(item="20C", name='CC_NBR_MONTHS', type='number', startIndex=67, endIndex=70,
                    friendly_name="child care - number of months", required=True, validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ]),
              Field(item="21A", name='TRANSP_AMOUNT', type='number', startIndex=70, endIndex=74,
                    friendly_name="transportation amount", required=True, validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ]),
              Field(item="21B", name='TRANSP_NBR_MONTHS', type='number', startIndex=74, endIndex=77,
                    friendly_name="transmportation number of months", required=True, validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ]),
              Field(item="22A", name='TRANSITION_SERVICES_AMOUNT', type='number', startIndex=77, endIndex=81,
                    friendly_name="transition services amount", required=False, validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ]),
              Field(item="22B", name='TRANSITION_NBR_MONTHS', type='number', startIndex=81, endIndex=84,
                    friendly_name="transition number of months", required=False, validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ]),
              Field(item="23A", name='OTHER_AMOUNT', type='number', startIndex=84, endIndex=88,
                    friendly_name="other amount", required=False, validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ]),
              Field(item="23B", name='OTHER_NBR_MONTHS', type='number', startIndex=88, endIndex=91,
                    friendly_name="other nuber of months", required=False, validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ]),
              Field(item="24AI", name='SANC_REDUCTION_AMT', type='number', startIndex=91, endIndex=95,
                    friendly_name="sanction reduction amount", required=True, validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ]),
              Field(item="24AII", name='WORK_REQ_SANCTION', type='number', startIndex=95, endIndex=96,
                    friendly_name="work requirements sanction", required=True, validators=[
                        validators.oneOf([1, 2]),
                    ]),
              Field(item="24AIII", name='FAMILY_SANC_ADULT', type='number', startIndex=96, endIndex=97,
                    friendly_name="family sanction for adult", required=False, validators=[
                        validators.isInLimits(0, 9),
                    ]),
              Field(item="24AIV", name='SANC_TEEN_PARENT', type='number', startIndex=97, endIndex=98,
                    friendly_name="santion for teen parent", required=True, validators=[
                        validators.oneOf([1, 2]),
                    ]),
              Field(item="24AV", name='NON_COOPERATION_CSE', type='number', startIndex=98, endIndex=99,
                    friendly_name="non coopeartion case", required=True, validators=[
                        validators.oneOf([1, 2]),
                    ]),
              Field(item="24AVI", name='FAILURE_TO_COMPLY', type='number', startIndex=99, endIndex=100,
                    friendly_name="failure to comply", required=True, validators=[
                        validators.oneOf([1, 2]),
                    ]),
              Field(item="24AVII", name='OTHER_SANCTION', type='number', startIndex=100, endIndex=101,
                    friendly_name="other sanciton", required=True, validators=[
                        validators.oneOf([1, 2]),
                    ]),
              Field(item="24B", name='RECOUPMENT_PRIOR_OVRPMT', type='number', startIndex=101, endIndex=105,
                    friendly_name="recoupment prior overpayment", required=True, validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ]),
              Field(item="24CI", name='OTHER_TOTAL_REDUCTIONS', type='number', startIndex=105, endIndex=109,
                    friendly_name="other total reductions", required=True, validators=[
                        validators.isLargerThanOrEqualTo(0),
                    ]),
              Field(item="24CII", name='FAMILY_CAP', type='number', startIndex=109, endIndex=110,
                    friendly_name="family cap", required=True, validators=[
                        validators.oneOf([1, 2]),
                    ]),
              Field(item="24CIII", name='REDUCTIONS_ON_RECEIPTS', type='number', startIndex=110, endIndex=111,
                    friendly_name="reductions on receipts", required=True, validators=[
                        validators.oneOf([1, 2]),
                    ]),
              Field(item="24CIV", name='OTHER_NON_SANCTION', type='number', startIndex=111, endIndex=112,
                    friendly_name="other non santion", required=True, validators=[
                        validators.oneOf([1, 2]),
                    ]),
              Field(item="25", name='WAIVER_EVAL_CONTROL_GRPS', type='number', startIndex=112, endIndex=113,
                    friendly_name="waiver evaluation xperimental and control groups", required=False, validators=[
                        validators.isInLimits(0, 9),
                    ]),
              Field(item="-1", name='BLANK', type='string', startIndex=113, endIndex=150,
                    friendly_name="blank", required=False, validators=[]),
          ]
        )
    ]
)
