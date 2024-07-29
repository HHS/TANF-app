"""Schema for SSP M1 record type."""

from tdpservice.parsers.transforms import zero_pad
from tdpservice.parsers.fields import Field, TransformField
from tdpservice.parsers.row_schema import RowSchema, SchemaManager
from tdpservice.parsers.validators.category1 import PreparsingValidators
from tdpservice.parsers.validators.category2 import FieldValidators
from tdpservice.parsers.validators.category3 import ComposableValidators
from tdpservice.search_indexes.documents.ssp import SSP_M1DataSubmissionDocument
from tdpservice.parsers.util import generate_t1_t4_hashes, get_t1_t4_partial_hash_members

m1 = SchemaManager(
    schemas=[
        RowSchema(
            record_type="M1",
            document=SSP_M1DataSubmissionDocument(),
            generate_hashes_func=generate_t1_t4_hashes,
            get_partial_hash_members_func=get_t1_t4_partial_hash_members,
            preparsing_validators=[
                PreparsingValidators.recordHasLengthBetween(113, 150),
                PreparsingValidators.caseNumberNotEmpty(8, 19),
                PreparsingValidators.or_priority_validators([
                    PreparsingValidators.validate_fieldYearMonth_with_headerYearQuarter(),
                    PreparsingValidators.validateRptMonthYear(),
                ]),
            ],
            postparsing_validators=[
                ComposableValidators.ifThenAlso(
                    condition_field_name='CASH_AMOUNT',
                    condition_function=ComposableValidators.isGreaterThan(0),
                    result_field_name='NBR_MONTHS',
                    result_function=ComposableValidators.isGreaterThan(0),
                ),
                ComposableValidators.ifThenAlso(
                    condition_field_name='CC_AMOUNT',
                    condition_function=ComposableValidators.isGreaterThan(0),
                    result_field_name='CHILDREN_COVERED',
                    result_function=ComposableValidators.isGreaterThan(0),
                ),
                ComposableValidators.ifThenAlso(
                    condition_field_name='CC_AMOUNT',
                    condition_function=ComposableValidators.isGreaterThan(0),
                    result_field_name='CC_NBR_MONTHS',
                    result_function=ComposableValidators.isGreaterThan(0),
                ),
                ComposableValidators.ifThenAlso(
                    condition_field_name='TRANSP_AMOUNT',
                    condition_function=ComposableValidators.isGreaterThan(0),
                    result_field_name='TRANSP_NBR_MONTHS',
                    result_function=ComposableValidators.isGreaterThan(0),
                ),
                ComposableValidators.ifThenAlso(
                    condition_field_name='SANC_REDUCTION_AMT',
                    condition_function=ComposableValidators.isGreaterThan(0),
                    result_field_name='WORK_REQ_SANCTION',
                    result_function=ComposableValidators.isOneOf((1, 2)),
                ),
                ComposableValidators.ifThenAlso(
                    condition_field_name='SANC_REDUCTION_AMT',
                    condition_function=ComposableValidators.isGreaterThan(0),
                    result_field_name='SANC_TEEN_PARENT',
                    result_function=ComposableValidators.isOneOf((1, 2)),
                ),
                ComposableValidators.ifThenAlso(
                    condition_field_name='SANC_REDUCTION_AMT',
                    condition_function=ComposableValidators.isGreaterThan(0),
                    result_field_name='NON_COOPERATION_CSE',
                    result_function=ComposableValidators.isOneOf((1, 2)),
                ),
                ComposableValidators.ifThenAlso(
                    condition_field_name='SANC_REDUCTION_AMT',
                    condition_function=ComposableValidators.isGreaterThan(0),
                    result_field_name='FAILURE_TO_COMPLY',
                    result_function=ComposableValidators.isOneOf((1, 2)),
                ),
                ComposableValidators.ifThenAlso(
                    condition_field_name='SANC_REDUCTION_AMT',
                    condition_function=ComposableValidators.isGreaterThan(0),
                    result_field_name='OTHER_SANCTION',
                    result_function=ComposableValidators.isOneOf((1, 2)),
                ),
                ComposableValidators.ifThenAlso(
                    condition_field_name='OTHER_TOTAL_REDUCTIONS',
                    condition_function=ComposableValidators.isGreaterThan(0),
                    result_field_name='FAMILY_CAP',
                    result_function=ComposableValidators.isOneOf((1, 2)),
                ),
                ComposableValidators.ifThenAlso(
                    condition_field_name='OTHER_TOTAL_REDUCTIONS',
                    condition_function=ComposableValidators.isGreaterThan(0),
                    result_field_name='REDUCTIONS_ON_RECEIPTS',
                    result_function=ComposableValidators.isOneOf((1, 2)),
                ),
                ComposableValidators.ifThenAlso(
                    condition_field_name='OTHER_TOTAL_REDUCTIONS',
                    condition_function=ComposableValidators.isGreaterThan(0),
                    result_field_name='OTHER_NON_SANCTION',
                    result_function=ComposableValidators.isOneOf((1, 2)),
                ),
                ComposableValidators.sumIsLarger([
                    "AMT_FOOD_STAMP_ASSISTANCE",
                    "AMT_SUB_CC",
                    "CASH_AMOUNT",
                    "CC_AMOUNT",
                    "CC_NBR_MONTHS"], 0)
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
                TransformField(
                    zero_pad(3),
                    item="2",
                    name='COUNTY_FIPS_CODE',
                    friendly_name="County FIPS code",
                    type='string',
                    startIndex=19,
                    endIndex=22,
                    required=True,
                    validators=[FieldValidators.isNumber()],
                ),
                Field(
                    item="4",
                    name='STRATUM',
                    friendly_name="Stratum",
                    type='string',
                    startIndex=22,
                    endIndex=24,
                    required=False,
                    validators=[FieldValidators.isBetween(0, 99, inclusive=True, cast=int),]
                ),
                Field(
                    item="6",
                    name='ZIP_CODE',
                    friendly_name="ZIP Code",
                    type='string',
                    startIndex=24,
                    endIndex=29,
                    required=True,
                    validators=[FieldValidators.isNumber(),]
                ),
                Field(
                    item="7",
                    name='DISPOSITION',
                    friendly_name="Disposition",
                    type='number',
                    startIndex=29,
                    endIndex=30,
                    required=True,
                    validators=[FieldValidators.isOneOf([1, 2]),]
                ),
                Field(
                    item="8",
                    name='NBR_FAMILY_MEMBERS',
                    friendly_name="Number of Family Members",
                    type='number',
                    startIndex=30,
                    endIndex=32,
                    required=True,
                    validators=[FieldValidators.isBetween(1, 99, inclusive=True),]
                ),
                Field(
                    item="9",
                    name='FAMILY_TYPE',
                    friendly_name="Type of Family for Work Participation",
                    type='number',
                    startIndex=32,
                    endIndex=33,
                    required=True,
                    validators=[FieldValidators.isBetween(1, 3, inclusive=True),]
                ),
                Field(
                    item="10",
                    name='TANF_ASST_IN_6MONTHS',
                    friendly_name="Received Assistance Under a State (Tribal) TANF Program Within the Past Six Months",
                    type='number',
                    startIndex=33,
                    endIndex=34,
                    required=True,
                    validators=[FieldValidators.isBetween(1, 3, inclusive=True),]
                ),
                Field(
                    item="11",
                    name='RECEIVES_SUB_HOUSING',
                    friendly_name="Receives Subsidized Housing",
                    type='number',
                    startIndex=34,
                    endIndex=35,
                    required=True,
                    validators=[FieldValidators.isBetween(1, 2, inclusive=True),]
                ),
                Field(
                    item="12",
                    name='RECEIVES_MED_ASSISTANCE',
                    friendly_name="Received Medical Assistance",
                    type='number',
                    startIndex=35,
                    endIndex=36,
                    required=True,
                    validators=[FieldValidators.isBetween(1, 2, inclusive=True),]
                ),
                Field(
                    item="13",
                    name='RECEIVES_FOOD_STAMPS',
                    friendly_name="Receives SNAP Assistance",
                    type='number',
                    startIndex=36,
                    endIndex=37,
                    required=False,
                    validators=[FieldValidators.isBetween(0, 2, inclusive=True),]
                ),
                Field(
                    item="14",
                    name='AMT_FOOD_STAMP_ASSISTANCE',
                    friendly_name="Amount of SNAP Benefits",
                    type='number',
                    startIndex=37,
                    endIndex=41,
                    required=True,
                    validators=[FieldValidators.isGreaterThan(0, inclusive=True),]
                ),
                Field(
                    item="15",
                    name='RECEIVES_SUB_CC',
                    friendly_name="Receives Subsidized Child Care",
                    type='number',
                    startIndex=41,
                    endIndex=42,
                    required=False,
                    validators=[FieldValidators.isBetween(0, 2, inclusive=True),]
                ),
                Field(
                    item="16",
                    name='AMT_SUB_CC',
                    friendly_name="Amount of Subsidized Child Care",
                    type='number',
                    startIndex=42,
                    endIndex=46,
                    required=True,
                    validators=[FieldValidators.isGreaterThan(0, inclusive=True),]
                ),
                Field(
                    item="17",
                    name='CHILD_SUPPORT_AMT',
                    friendly_name="Amount of Child Support",
                    type='number',
                    startIndex=46,
                    endIndex=50,
                    required=True,
                    validators=[FieldValidators.isGreaterThan(0, inclusive=True),]
                ),
                Field(
                    item="18",
                    name='FAMILY_CASH_RESOURCES',
                    friendly_name="Amount of the Family's Cash Resources",
                    type='number',
                    startIndex=50,
                    endIndex=54,
                    required=True,
                    validators=[FieldValidators.isGreaterThan(0, inclusive=True),]
                ),
                Field(
                    item="19A",
                    name='CASH_AMOUNT',
                    friendly_name="Cash and Cash Equivalents: Amount",
                    type='number',
                    startIndex=54,
                    endIndex=58,
                    required=True,
                    validators=[FieldValidators.isGreaterThan(0, inclusive=True),]
                ),
                Field(
                    item="19B",
                    name='NBR_MONTHS',
                    friendly_name="Cash and Cash Equivalents: Number of Months",
                    type='number',
                    startIndex=58,
                    endIndex=61,
                    required=True,
                    validators=[FieldValidators.isGreaterThan(0, inclusive=True),]
                ),
                Field(
                    item="20A",
                    name='CC_AMOUNT',
                    friendly_name="SSP-MOE Child Care: Amount",
                    type='number',
                    startIndex=61,
                    endIndex=65,
                    required=True,
                    validators=[FieldValidators.isGreaterThan(0, inclusive=True),]
                ),
                Field(
                    item="20B",
                    name='CHILDREN_COVERED',
                    friendly_name="SSP-MOE Child Care: Number of Children Covered",
                    type='number',
                    startIndex=65,
                    endIndex=67,
                    required=True,
                    validators=[FieldValidators.isGreaterThan(0, inclusive=True),]
                ),
                Field(
                    item="20C",
                    name='CC_NBR_MONTHS',
                    friendly_name="SSP-MOE Child Care: Number of Months",
                    type='number',
                    startIndex=67,
                    endIndex=70,
                    required=True,
                    validators=[FieldValidators.isGreaterThan(0, inclusive=True),]
                ),
                Field(
                    item="21A",
                    name='TRANSP_AMOUNT',
                    friendly_name="Transportation and Other Supportive Services: Amount",
                    type='number',
                    startIndex=70,
                    endIndex=74,
                    required=True,
                    validators=[FieldValidators.isGreaterThan(0, inclusive=True),]
                ),
                Field(
                    item="21B",
                    name='TRANSP_NBR_MONTHS',
                    friendly_name="Transportation and Other Supportive Services: Number of Months",
                    type='number',
                    startIndex=74,
                    endIndex=77,
                    required=True,
                    validators=[FieldValidators.isGreaterThan(0, inclusive=True),]
                ),
                Field(
                    item="22A",
                    name='TRANSITION_SERVICES_AMOUNT',
                    friendly_name="Transitional Services: Amount",
                    type='number',
                    startIndex=77,
                    endIndex=81,
                    required=False,
                    validators=[FieldValidators.isGreaterThan(0, inclusive=True),]
                ),
                Field(
                    item="22B",
                    name='TRANSITION_NBR_MONTHS',
                    friendly_name="Transitional Services: Number of Months",
                    type='number',
                    startIndex=81,
                    endIndex=84,
                    required=False,
                    validators=[FieldValidators.isGreaterThan(0, inclusive=True),]
                ),
                Field(
                    item="23A",
                    name='OTHER_AMOUNT',
                    friendly_name="Other: Amount",
                    type='number',
                    startIndex=84,
                    endIndex=88,
                    required=False,
                    validators=[FieldValidators.isGreaterThan(0, inclusive=True),]
                ),
                Field(
                    item="23B",
                    name='OTHER_NBR_MONTHS',
                    friendly_name="Other: Number of Months",
                    type='number',
                    startIndex=88,
                    endIndex=91,
                    required=False,
                    validators=[FieldValidators.isGreaterThan(0, inclusive=True),]
                ),
                Field(
                    item="24AI",
                    name='SANC_REDUCTION_AMT',
                    friendly_name="Sanctions: Total Dollar Amount of Reductions due to Sanctions",
                    type='number',
                    startIndex=91,
                    endIndex=95,
                    required=True,
                    validators=[FieldValidators.isGreaterThan(0, inclusive=True),]
                ),
                Field(
                    item="24AII",
                    name='WORK_REQ_SANCTION',
                    friendly_name="Sanctions: Work Requirements",
                    type='number',
                    startIndex=95,
                    endIndex=96,
                    required=True,
                    validators=[FieldValidators.isOneOf([1, 2]),]
                ),
                Field(
                    item="24AIII",
                    name='FAMILY_SANC_ADULT',
                    friendly_name="Family Sanctions",
                    type='number',
                    startIndex=96,
                    endIndex=97,
                    required=False,
                    validators=[FieldValidators.isBetween(0, 9, inclusive=True),]
                ),
                Field(
                    item="24AIV",
                    name='SANC_TEEN_PARENT',
                    friendly_name="Sanction: Teen Parent not Attending School",
                    type='number',
                    startIndex=97,
                    endIndex=98,
                    required=True,
                    validators=[FieldValidators.isOneOf([1, 2]),]
                ),
                Field(
                    item="24AV",
                    name='NON_COOPERATION_CSE',
                    friendly_name="Sanction: Non-Cooperation with Child Support",
                    type='number',
                    startIndex=98,
                    endIndex=99,
                    required=True,
                    validators=[FieldValidators.isOneOf([1, 2]),]
                ),
                Field(
                    item="24AVI",
                    name='FAILURE_TO_COMPLY',
                    friendly_name="Sanction: Failure to Comply with an Individual Responsibility Plan ",
                    type='number',
                    startIndex=99,
                    endIndex=100,
                    required=True,
                    validators=[FieldValidators.isOneOf([1, 2]),]
                ),
                Field(
                    item="24AVII",
                    name='OTHER_SANCTION',
                    friendly_name="Sanction: Other",
                    type='number',
                    startIndex=100,
                    endIndex=101,
                    required=True,
                    validators=[FieldValidators.isOneOf([1, 2]),]
                ),
                Field(
                    item="24B",
                    name='RECOUPMENT_PRIOR_OVRPMT',
                    friendly_name="Recoupment of Prior Overpayment",
                    type='number',
                    startIndex=101,
                    endIndex=105,
                    required=True,
                    validators=[FieldValidators.isGreaterThan(0, inclusive=True),]
                ),
                Field(
                    item="24CI",
                    name='OTHER_TOTAL_REDUCTIONS',
                    friendly_name="Other: Total Dollar Amount of Reductions for Other Reasons",
                    type='number',
                    startIndex=105,
                    endIndex=109,
                    required=True,
                    validators=[FieldValidators.isGreaterThan(0, inclusive=True),]
                ),
                Field(
                    item="24CII",
                    name='FAMILY_CAP',
                    friendly_name="Other: Family Cap",
                    type='number',
                    startIndex=109,
                    endIndex=110,
                    required=True,
                    validators=[FieldValidators.isOneOf([1, 2]),]
                ),
                Field(
                    item="24CIII",
                    name='REDUCTIONS_ON_RECEIPTS',
                    friendly_name="Other: Reduction Based on Time Limit",
                    type='number',
                    startIndex=110,
                    endIndex=111,
                    required=True,
                    validators=[FieldValidators.isOneOf([1, 2]),]
                ),
                Field(
                    item="24CIV",
                    name='OTHER_NON_SANCTION',
                    friendly_name="Other: Non-Sanction, Non-Recoupment",
                    type='number',
                    startIndex=111,
                    endIndex=112,
                    required=True,
                    validators=[FieldValidators.isOneOf([1, 2]),]
                ),
                Field(
                    item="25",
                    name='WAIVER_EVAL_CONTROL_GRPS',
                    friendly_name="Waiver Evaluation Experimental and Control Groups",
                    type='number',
                    startIndex=112,
                    endIndex=113,
                    required=False,
                    validators=[FieldValidators.isBetween(0, 9, inclusive=True),]
                ),
                Field(
                    item="-1",
                    name='BLANK',
                    friendly_name="blank",
                    type='string',
                    startIndex=113,
                    endIndex=150,
                    required=False,
                    validators=[]
                ),
            ]
        )
    ]
)
